"""Hồi quy cho thống kê có nguồn, G10 và demo dùng chung qua answer(text)."""
import json
import os
import sys
import unittest
from unittest.mock import patch

os.environ["MODEL_PROVIDER"] = "fake"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "codebase"))
import agent
import tracing
from review_signals import signals_for, mock_risks

URL = "https://shopee.vn/product/123/456"


def sources(texts):
    return [{"id": "R%02d" % (i + 1), "text": text, "rating": 2} for i, text in enumerate(texts)]


def rows(texts):
    return [{"rating_star": 2, "comment": text} for text in texts]


class ReviewSignalTests(unittest.TestCase):
    def test_partition_counts_original_sources_and_duplicate_reference(self):
        data = sources(["...", "Giao hàng nhanh", "Đánh giá để nhận xu", "Chưa sử dụng",
                        "Sản phẩm rất tốt", "Pin yếu sau một giờ", "PIN yếu sau một giờ!"])
        result = signals_for(data)
        stats = result["stats"]
        self.assertEqual((stats["total"], stats["filtered_noise"], stats["kept_clean"]), (7, 6, 1))
        self.assertEqual(sum(stats["noise_breakdown"].values()), 6)
        self.assertEqual(result["kept"], [data[5]])
        self.assertEqual(result["flags"][-1]["duplicate_of"], "R06")
        self.assertEqual(result["flags"][0]["citations"][0]["text"], "...")
        self.assertEqual(stats["noise_pct"], 85.7)

    def test_word_boundaries_shipping_flagship_and_apology(self):
        result = signals_for(sources(["Shipping nhanh, đóng gói cẩn thận.", "Hàng flagship nhìn rất đẹp.", "Shop xin lỗi vì giao trễ."]))
        self.assertEqual([x["kind"] for x in result["flags"]], ["shipping_only", "shipping_only"])
        self.assertEqual([x["id"] for x in result["kept"]], ["R02"])

    def test_product_detail_is_kept_alongside_shipping_and_unicode_duplicate(self):
        result = signals_for(sources(["Shipping nhanh nhưng pin yếu.", "Âm thanh rõ khi nghe nhạc.", "Chất lượng hoàn thiện chắc chắn.", "Âm thanh rõ khi nghe nhạc!" ]))
        self.assertEqual(len(result["kept"]), 3)
        self.assertEqual(result["flags"][0]["kind"], "duplicate")

    def test_mock_does_not_infer_fault_from_stars_or_negated_failure(self):
        data = sources(["Chưa thấy mất kết nối.", "Không bị đau tai.", "Không có hiện tượng pin yếu.", "Âm thanh nghe rõ."])
        self.assertEqual(mock_risks(data), [])

    def test_g10_counts_unique_kept_reviews_without_calling_model(self):
        tracing.begin("g10")
        with patch.object(agent, "call_model") as model:
            result = agent.answer(json.dumps({"mode": "reviews", "url": URL,
                                             "reviews": rows(["Pin yếu.", "Pin yếu.", "Giao hàng nhanh."])}))
        usage, _ = tracing.end()
        model.assert_not_called()
        self.assertEqual(result["structured"]["status"], "insufficient")
        self.assertEqual(result["structured"]["stats"]["kept_clean"], 1)
        self.assertEqual((usage["model_calls"], usage["tool_calls"]), (0, 1))

    def test_demo_goes_through_answer_with_three_verifiable_risks_and_one_tool(self):
        tracing.begin("demo")
        data = rows(["Tai trái mất kết nối.", "Giao hàng nhanh, chưa dùng.", "Pin nhanh hết.", "Đeo đau tai."])
        with patch.object(agent, "crawl_shopee_reviews") as crawl:
            result = agent.answer(json.dumps({"mode": "reviews", "url": URL, "reviews": data}))
        usage, events = tracing.end()
        crawl.assert_not_called()
        analysis = result["structured"]
        self.assertEqual(len(analysis["risks"]), 3)
        self.assertTrue(analysis["mock"])
        for risk in analysis["risks"]:
            for source in risk["citations"]:
                self.assertEqual(source["text"], data[int(source["id"][1:]) - 1]["comment"])
                self.assertIn("[%s]" % source["id"], result["output"])
        self.assertEqual((usage["model_calls"], usage["tool_calls"], usage["tokens_in"], usage["tokens_out"]), (1, 1, 0, 0))
        self.assertFalse(usage["errors"])
        self.assertEqual(sum(event.get("name") == "quantify_review_signals" for event in events), 1)

    def test_per_star_limit_is_disclosed_instead_of_counted_as_noise(self):
        result = agent.analyze_reviews(URL, rows(["Pin dùng được %d giờ." % i for i in range(60)]))
        stats = result["stats"]
        self.assertEqual((stats["input_total"], stats["total"], stats["excluded_limit"]), (60, 50, 10))
        self.assertEqual((stats["filtered_noise"], stats["kept_clean"]), (0, 50))

    def test_model_only_receives_kept_sources_and_cannot_cite_removed_review(self):
        output = {"status": "risks", "summary": "Fixture", "risks": [
            {"title": "Sai nguồn", "summary": "Không được dùng", "citations": ["R02"]}]}
        with patch.object(agent, "call_model", return_value={"text": json.dumps(output), "model": "test-only"}) as model:
            result = agent.analyze_reviews(URL, rows(["Pin yếu.", "Giao hàng nhanh.", "Đeo đau tai.", "Mất kết nối."]))
        payload = json.loads(model.call_args.args[1])
        self.assertEqual([row["id"] for row in payload["reviews"]], ["R01", "R03", "R04"])
        self.assertEqual(result["risks"], [])
        self.assertEqual(result["flags"][0]["citations"][0]["id"], "R02")

    def test_plain_link_still_uses_crawler_and_same_structured_result(self):
        data = rows(["Pin yếu.", "Đeo đau tai.", "Mất kết nối."])
        with patch.object(agent, "crawl_shopee_reviews", return_value={"reviews": data, "coverage": {"counts_complete": False}}) as crawl:
            result = agent.answer(URL)
        crawl.assert_called_once_with(URL)
        self.assertIsInstance(result["output"], str)
        self.assertEqual(len(result["structured"]["risks"]), 3)

    def test_fake_positive_input_does_not_force_three_risks(self):
        result = agent.answer(json.dumps({"mode": "reviews", "url": URL, "reviews": rows([
            "Pin đủ dùng một buổi.", "Âm thanh rõ khi nghe nhạc.", "Đeo thoải mái khi sử dụng."])}))
        self.assertEqual(result["structured"]["status"], "no_clear_risk")
        self.assertEqual(result["structured"]["risks"], [])
        self.assertTrue(result["structured"]["mock"])


if __name__ == "__main__":
    unittest.main()
