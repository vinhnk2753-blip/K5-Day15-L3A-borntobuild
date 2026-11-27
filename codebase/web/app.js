"use strict";
const $ = (id) => document.getElementById(id);
const form = $("review-form");
let busy = false, revision = 0, snapshot = [], lastSourceButton = null;
let limits = { max_reviews: 100, max_review_chars: 4000, max_input_chars: 50000, min_clean_reviews: 2 };
const labels = { duplicate: "Nội dung lặp", not_used: "Chưa dùng / nhận xu", shipping_only: "Chỉ giao hàng / đóng gói", instruction: "Chỉ dẫn ngoài phạm vi", other: "Cần đọc lại" };
const lines = () => $("reviews").value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
function node(tag, text, cls) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; }
function sourceButton(id, text) {
  const button = node("button", text || `[${id}] Xem review gốc`, "source-link"); button.type = "button";
  button.addEventListener("click", () => {
    const source = snapshot.find(r => r.id === id);
    if (!source) return;
    lastSourceButton = button;
    $("source-title").textContent = `Review gốc [${id}]`;
    $("source-content").textContent = source.text;
    $("source-context").textContent = "Nguồn thuộc tập đánh giá của lần kiểm tra đang hiển thị.";
    $("source-dialog").showModal();
  }); return button;
}
function preview() {
  const rows = lines(); $("input-count").textContent = `${rows.length} review${rows.length ? ` · Mã R01–R${String(rows.length).padStart(2, "0")}` : " · Chưa có nội dung"}`;
  $("preview-list").replaceChildren(...rows.slice(0, limits.max_reviews).map((s, i) => {
    const li = node("li"); li.append(node("strong", `[R${String(i + 1).padStart(2, "0")}] `), node("span", s)); return li;
  }));
}
function invalidate() {
  revision++; snapshot = []; $("results").hidden = true; $("empty-state").hidden = false;
  $("stale-note").hidden = false; $("form-error").hidden = true; $("reviews").removeAttribute("aria-invalid"); preview();
}
function inputError(message) {
  $("form-error").textContent = message; $("form-error").hidden = false;
  $("reviews").setAttribute("aria-invalid", "true"); $("reviews").focus();
}
function setBusy(value) {
  busy = value; form.querySelectorAll("input,select,textarea,button").forEach(el => el.disabled = value);
  $("loading").hidden = !value; $("result-region").setAttribute("aria-busy", String(value));
  $("analyze").textContent = value ? "Đang kiểm tra…" : "Kiểm tra rủi ro";
}
function render(data) {
  const r = data.result; snapshot = data.sources || [];
  const titles = { ok: `Có ${r.risks.length} rủi ro cần cân nhắc`, insufficient_evidence: "Chưa đủ dữ liệu", out_of_scope: "Yêu cầu ngoài phạm vi", no_risk_found: "Chưa thấy rủi ro trong dữ liệu này", invalid_input: "Kiểm tra lại đầu vào", error: "Lần kiểm tra chưa hoàn tất" };
  $("empty-state").hidden = true; $("results").hidden = false;
  $("result-kind").textContent = data.mock ? "KẾT QUẢ MÔ PHỎNG · CHƯA GỌI AI THẬT" : "KẾT QUẢ KIỂM TRA";
  $("result-heading").textContent = titles[r.status] || "Chưa thể hiển thị kết quả";
  $("result-message").textContent = r.message;
  const s = r.summary;
  $("quantitative").hidden = ["error", "invalid_input"].includes(r.status);
  $("flags-section").hidden = ["error", "invalid_input"].includes(r.status);
  const stats = [[String(s.total_reviews), "review đã nhập"], [`${s.flagged_reviews}/${s.total_reviews} · ${s.flagged_percent || 0}%`, "review được gắn cờ"], [`${s.clean_reviews || 0}/${s.total_reviews}`, "review sạch theo quy tắc demo"]];
  $("quantitative").replaceChildren(...stats.map(([v, label]) => { const el = node("div", undefined, "stat"); el.append(node("strong", v), node("span", label)); return el; }));
  $("flag-rule").textContent = `“Sạch” là nội dung trải nghiệm không bị gắn cờ theo quy tắc demo. Cần ít nhất ${s.min_clean_reviews || limits.min_clean_reviews} review sạch khác nhau; đây là ngưỡng tự chọn, chưa đo trên dữ liệu thật.`;
  $("signal-counts").replaceChildren(...Object.entries(s.signal_counts || {}).filter(([, count]) => count > 0).map(([kind, count]) => node("li", `${labels[kind] || kind}: ${count}/${s.total_reviews}`)));
  $("flags-list").replaceChildren(...r.review_flags.map(f => { const el = node("div", undefined, "flag"); el.append(sourceButton(f.review_id), node("p", f.reason)); return el; }));
  if (!r.review_flags.length) $("flags-list").append(node("p", "Chưa phát hiện cờ theo các quy tắc đang dùng.", "hint"));
  $("risk-list").replaceChildren(...r.risks.slice(0, 3).map((risk, i) => {
    const card = node("article", undefined, "panel risk"); card.append(node("p", `RỦI RO ${i + 1}`, "eyebrow"), node("h3", risk.title), node("p", risk.description, "risk-description"));
    risk.evidence.forEach(ev => { const block = node("div", undefined, "evidence"); block.append(node("blockquote", ev.quote), sourceButton(ev.review_id)); card.append(block); }); return card;
  }));
  $("ordering").hidden = r.status !== "ok";
  $("state-action").hidden = r.status === "ok"; $("retry").hidden = r.status !== "error";
  $("usage-values").textContent = data.usage ? `Model: ${data.usage.models.join(", ") || "không gọi"}\nSố lần gọi model: ${data.usage.model_calls} · Công cụ: ${data.usage.tool_calls}\nToken vào: ${data.usage.tokens_in} · Token ra: ${data.usage.tokens_out}` : "Chưa có lượt chạy hoàn tất; không có số usage để báo cáo.";
  $("usage-mode").textContent = data.mock ? "Mô phỏng CP2: token 0, không phải số liệu chi phí hoặc chất lượng AI thật." : "Lượt bị chặn ở bước kiểm tra đầu vào hoặc G10 có thể không gọi model.";
  $("result-heading").focus();
}
form.addEventListener("submit", async (event) => {
  event.preventDefault(); if (busy) return;
  const rows = lines();
  if (!rows.length) { inputError("Hãy nhập ít nhất một review có nội dung."); return; }
  if (rows.length > limits.max_reviews || rows.some(s => s.length > limits.max_review_chars)) { inputError(`Giới hạn ${limits.max_reviews} review, mỗi review tối đa ${limits.max_review_chars} ký tự. Không tự cắt nội dung.`); return; }
  const input = JSON.stringify({ product_name: $("product-name").value.trim(), reviews: rows.map((text, i) => ({ id: `R${String(i + 1).padStart(2, "0")}`, text, rating: null })) });
  if (input.length > limits.max_input_chars) { inputError(`Đầu vào chuẩn hóa vượt ${limits.max_input_chars} ký tự. Hãy rút gọn số review.`); return; }
  const ticket = revision; $("form-error").hidden = true; $("results").hidden = true; $("empty-state").hidden = true; setBusy(true);
  const controller = new AbortController(); const timeout = setTimeout(() => controller.abort(), 90000);
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ input }), signal: controller.signal });
    const data = await response.json(); if (!data.result) throw new Error("invalid-response");
    if (ticket === revision) render(data);
  } catch (_) {
    if (ticket === revision) render({ result: { status: "error", message: "Không thể nhận kết quả. Nội dung đã nhập vẫn được giữ để thử lại.", risks: [], review_flags: [], summary: { total_reviews: rows.length, flagged_reviews: 0 } }, sources: [] });
  } finally { clearTimeout(timeout); setBusy(false); }
});
$("reviews").addEventListener("input", invalidate); $("product-name").addEventListener("input", invalidate);
$("clear").addEventListener("click", () => { $("reviews").value = ""; $("product-name").value = ""; $("product-select").value = ""; invalidate(); $("reviews").focus(); });
$("edit").addEventListener("click", () => { $("reviews").focus(); $("reviews").scrollIntoView({ block: "center" }); });
$("retry").addEventListener("click", () => form.requestSubmit());
$("close-source").addEventListener("click", () => $("source-dialog").close());
$("source-dialog").addEventListener("close", () => { if (lastSourceButton && lastSourceButton.isConnected) lastSourceButton.focus(); });
$("product-select").addEventListener("change", async () => {
  const id = $("product-select").value; const ticket = ++revision;
  if (!id) { $("product-name").value = ""; $("reviews").value = ""; invalidate(); return; }
  try {
    const response = await fetch(`/api/products/${encodeURIComponent(id)}`); if (!response.ok) throw new Error("catalog");
    const data = await response.json(); if (ticket !== revision) return;
    $("product-name").value = data.input.product_name; $("reviews").value = data.input.reviews.map(r => r.text).join("\n"); invalidate();
    $("catalog-note").textContent = "Đã nạp dữ liệu tự dựng. Bạn có thể sửa trước khi kiểm tra; đây không phải dữ liệu crawl.";
  } catch (_) { inputError("Chưa tải được sản phẩm mẫu. Bạn vẫn có thể dán review thủ công."); }
});
async function init() {
  try {
    const response = await fetch("/api/products"); if (!response.ok) throw new Error("config");
    const data = await response.json(); limits = data.limits;
    data.products.forEach(p => { const option = node("option", `${p.name} · ${p.review_count} review minh họa`); option.value = p.id; $("product-select").append(option); });
    $("mode").textContent = data.model_provider === "fake" ? "Bản mô phỏng CP2 · Dữ liệu chọn sẵn tự dựng · Chưa gọi AI thật" : `Bản thử nghiệm · Model provider: ${data.model_provider}`;
    $("limit-note").textContent = `Tối đa ${limits.max_reviews} review/lần. Cần ít nhất ${limits.min_clean_reviews} review sạch để rút rủi ro trong bản demo.`;
  } catch (_) { $("mode").textContent = "Chưa tải được danh mục mẫu. Bạn có thể dán review và thử kiểm tra."; }
  preview();
}
init();
