"use strict";
const $ = id => document.getElementById(id);
const form = $("review-form");
let busy = false, revision = 0, snapshot = [], lastSourceButton = null;
let limits = { max_reviews: 250, max_per_star: 50, max_review_chars: 3000 };
const lines = () => $("reviews").value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
function node(tag, text, cls) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; }
function sourceButton(id) {
  const button = node("button", `[${id}] Xem review gốc`, "source-link"); button.type = "button";
  button.addEventListener("click", () => {
    const source = snapshot.find(r => r.id === id); if (!source) return;
    lastSourceButton = button;
    $("source-title").textContent = `Review gốc [${id}]`;
    $("source-content").textContent = source.text;
    $("source-context").textContent = `${source.rating} sao · ${source.date || "Chưa rõ ngày"} · Biến thể: ${source.variant || "chưa rõ"}`;
    $("source-dialog").showModal();
  }); return button;
}
function preview() {
  const rows = lines();
  $("input-count").textContent = `${rows.length} review · Mã nguồn sẽ xuất hiện cùng kết quả phân tích`;
  $("preview-list").replaceChildren(...rows.slice(0, limits.max_reviews).map(s => node("li", s)));
}
function invalidate() {
  revision++; snapshot = []; $("results").hidden = true; $("empty-state").hidden = false; $("stale-note").hidden = false;
  $("form-error").hidden = true; $("reviews").removeAttribute("aria-invalid"); $("product-url").removeAttribute("aria-invalid"); preview();
}
function inputError(message, target = "reviews") {
  $("form-error").textContent = message; $("form-error").hidden = false; $(target).setAttribute("aria-invalid", "true"); $(target).focus();
}
function setBusy(value) {
  busy = value; form.querySelectorAll("input,select,textarea,button").forEach(el => el.disabled = value);
  $("loading").hidden = !value; $("result-region").setAttribute("aria-busy", String(value));
  $("analyze").textContent = value ? "Đang xử lý…" : "Kiểm tra rủi ro";
}
function render(data) {
  const r = data.analysis; snapshot = data.sources || [];
  const titles = { risks: `Có ${r.risks.length} rủi ro cần cân nhắc`, insufficient: "Chưa đủ căn cứ phân tích", no_clear_risk: "Chưa thấy rủi ro rõ ràng", refused: "Yêu cầu ngoài phạm vi Shopee", invalid_input: "Kiểm tra lại đầu vào", error: "Lần kiểm tra chưa hoàn tất" };
  $("empty-state").hidden = true; $("results").hidden = false;
  $("result-kind").textContent = data.mock ? "CHẾ ĐỘ THỬ NGHIỆM · CHƯA GỌI AI THẬT" : "KẾT QUẢ PHÂN TÍCH";
  $("result-heading").textContent = titles[r.status] || "Chưa thể hiển thị kết quả";
  $("result-message").textContent = r.summary;
  const measured = data.origin === "backend" && Number.isInteger(r.review_count);
  $("quantitative").hidden = !measured; $("coverage-section").hidden = !measured;
  const stats = [[String(r.review_count || 0), "review có nội dung"], [String(r.risks.length), "rủi ro có nguồn"], [data.coverage?.counts_complete === true ? "Đã xác nhận" : "Chưa rõ", "độ phủ nguồn"]];
  $("quantitative").replaceChildren(...stats.map(([value, label]) => { const el = node("div", undefined, "stat"); el.append(node("strong", value), node("span", label)); return el; }));
  const coverage = data.coverage;
  $("coverage-note").textContent = coverage?.counts_complete === true ? "Nguồn báo đã lấy đủ theo phạm vi truy vấn. Không đồng nghĩa mọi người mua đều có cùng trải nghiệm." : "Nguồn chưa xác nhận đã lấy đủ review. Kết quả chỉ phản ánh phần dữ liệu backend nhận được.";
  $("risk-list").replaceChildren(...r.risks.slice(0, 3).map((risk, i) => {
    const card = node("article", undefined, "panel risk");
    card.append(node("p", `RỦI RO ${i + 1}`, "eyebrow"), node("h3", risk.title), node("p", risk.summary, "risk-description"));
    risk.citations.forEach(source => { const block = node("div", undefined, "evidence"); block.append(node("blockquote", source.text), sourceButton(source.id)); card.append(block); });
    return card;
  }));
  $("state-action").hidden = r.status === "risks"; $("retry").hidden = r.status !== "error";
  $("usage-values").textContent = data.usage ? `Model: ${data.usage.models.join(", ") || "không gọi"}\nSố lần gọi model: ${data.usage.model_calls} · Công cụ: ${data.usage.tool_calls}\nToken vào: ${data.usage.tokens_in} · Token ra: ${data.usage.tokens_out}` : "Chưa nhận usage từ backend, không tự ước lượng token.";
  $("usage-mode").textContent = data.mock ? "Backend fake không tạo rủi ro. Token 0 không dùng để dự báo chi phí hay chất lượng AI thật." : "Usage lấy từ tracing; lượt không đủ dữ liệu có thể không gọi model.";
  $("result-heading").focus();
}
form.addEventListener("submit", async event => {
  event.preventDefault(); if (busy) return;
  const url = $("product-url").value.trim(); let parsed;
  try { parsed = new URL(url); } catch { inputError("Hãy nhập link sản phẩm Shopee hợp lệ.", "product-url"); return; }
  const mode = $("input-mode").value;
  if (!["http:", "https:"].includes(parsed.protocol) || parsed.hostname !== "shopee.vn") { inputError("Chỉ hỗ trợ link sản phẩm trên shopee.vn.", "product-url"); return; }
  const request = { url, mode };
  if (mode === "reviews") {
    const rows = lines();
    if (!rows.length) { inputError("Hãy dán review theo dạng: số sao | nội dung."); return; }
    if (rows.length > limits.max_reviews) { inputError(`Tối đa ${limits.max_reviews} review mỗi lần.`); return; }
    const reviews = [];
    for (let i = 0; i < rows.length; i++) {
      const match = rows[i].match(/^([1-5])\s*\|\s*(.*)$/);
      if (!match || match[2].length > limits.max_review_chars) { inputError(`Dòng ${i + 1}: cần số sao 1–5 | nội dung tối đa ${limits.max_review_chars} ký tự.`); return; }
      reviews.push({ rating_star: Number(match[1]), comment: match[2] });
    }
    request.reviews = reviews;
  }
  const ticket = revision;
  $("form-error").hidden = true; $("results").hidden = true; $("empty-state").hidden = true; setBusy(true);
  const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 480000);
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(request), signal: controller.signal });
    const data = await response.json(); if (!data.analysis || !Array.isArray(data.analysis.risks)) throw new Error("invalid-response");
    if (ticket === revision) render(data);
  } catch (_) {
    if (ticket === revision) render({ analysis: { status: "error", summary: "Không thể nhận kết quả. Đầu vào vẫn được giữ; hãy kiểm tra kết nối rồi thử lại.", risks: [] }, sources: [] });
  } finally { clearTimeout(timeout); setBusy(false); }
});
function changeMode() {
  const manual = $("input-mode").value === "reviews";
  $("manual-fields").hidden = !manual; $("input-preview").hidden = !manual; $("crawl-note").hidden = manual;
  if (!manual && $("product-url").value === "https://shopee.vn/product/1/1") $("product-url").value = "";
  invalidate();
}
$("input-mode").addEventListener("change", changeMode);
$("reviews").addEventListener("input", invalidate); $("product-url").addEventListener("input", invalidate);
$("clear").addEventListener("click", () => { $("reviews").value = ""; $("product-url").value = ""; $("product-select").value = ""; invalidate(); $("reviews").focus(); });
$("edit").addEventListener("click", () => { $("product-url").focus(); $("product-url").scrollIntoView({ block: "center" }); });
$("retry").addEventListener("click", () => form.requestSubmit());
$("close-source").addEventListener("click", () => $("source-dialog").close());
$("source-dialog").addEventListener("close", () => { if (lastSourceButton?.isConnected) lastSourceButton.focus(); });
$("product-select").addEventListener("change", async () => {
  const id = $("product-select").value; const ticket = ++revision;
  if (!id) { $("reviews").value = ""; invalidate(); return; }
  try {
    const response = await fetch(`/api/products/${encodeURIComponent(id)}`); if (!response.ok) throw new Error("catalog");
    const data = await response.json(); if (ticket !== revision) return;
    $("product-url").value = data.url;
    $("reviews").value = data.reviews.map(r => `${r.rating_star} | ${r.comment}`).join("\n"); invalidate();
    $("catalog-note").textContent = "Đã nạp review và URL tự dựng để thử chế độ dán. Fake không tự tạo rủi ro; không crawl URL này.";
  } catch (_) { inputError("Chưa tải được bộ minh họa. Bạn có thể dán review có số sao."); }
});
async function init() {
  try {
    const response = await fetch("/api/products"); if (!response.ok) throw new Error("config");
    const data = await response.json(); limits = data.limits;
    data.products.forEach(p => { const option = node("option", `${p.name} · ${p.review_count} review minh họa`); option.value = p.id; $("product-select").append(option); });
    $("mode").textContent = data.model_provider === "fake" ? "Chế độ thử nghiệm · Chưa phân tích bằng AI thật" : "Kết quả chỉ dựa trên các review nhận được";
    $("crawl-note").textContent = data.crawler_configured ? "Crawler đã có cấu hình trên máy; khả năng lấy review còn phụ thuộc nguồn." : "Chưa có cấu hình Apify để crawl link trên máy. Bạn vẫn có thể dùng chế độ dán review có số sao.";
    $("limit-note").textContent = `Tối đa ${limits.max_reviews} review, giữ tối đa ${limits.max_per_star} mỗi mức sao. Kết quả có thể chưa bao phủ toàn bộ đánh giá của sản phẩm.`;
  } catch (_) { $("mode").textContent = "Chưa tải được cấu hình. Kiểm tra backend local rồi thử lại."; }
  preview();
}
init();
