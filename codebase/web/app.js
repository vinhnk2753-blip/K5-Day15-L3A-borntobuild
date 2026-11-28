"use strict";
const $ = id => document.getElementById(id);
const form = $("review-form");
let busy = false, revision = 0, snapshot = [], lastSourceButton = null, hasResult = false;
let activePayload = null;
let limits = { max_reviews: 250, max_review_chars: 3000 };
const DEFAULT_PAYLOAD_TITLE = "Chưa có dữ liệu từ Chrome extension.";
const DEFAULT_PAYLOAD_META = "Mở trang sản phẩm Shopee, bấm “Crawl & phân tích trang này” trong extension để tự động đẩy sang đây, hoặc chọn file JSON đã tải.";
const lines = () => $("reviews").value.split(/\r?\n/);
function node(tag, text, cls) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; }
function sourceButton(id) {
  const button = node("button", `[${id}] Xem review gốc`, "source-link"); button.type = "button";
  button.addEventListener("click", () => {
    const source = snapshot.find(row => row.id === id); if (!source) return;
    lastSourceButton = button; $("source-title").textContent = `Review gốc [${id}]`;
    $("source-content").textContent = source.text;
    const rating = source.rating == null ? "Không có số sao trong nguồn" : `${source.rating} sao`;
    $("source-context").textContent = `${rating} · ${source.date || "Chưa rõ ngày"} · Biến thể: ${source.variant || "chưa rõ"}`;
    $("source-dialog").showModal();
  }); return button;
}
function preview() {
  const rows = lines().filter(s => s.trim());
  $("input-count").textContent = `${rows.length} dòng · Mã nguồn do backend xác định khi phân tích`;
  $("preview-list").replaceChildren(...rows.slice(0, limits.max_reviews).map(s => node("li", s)));
}
function invalidate() {
  revision++; snapshot = []; $("results").hidden = true; $("empty-state").hidden = false;
  $("stale-note").hidden = !hasResult; $("form-error").hidden = true;
  $("reviews").removeAttribute("aria-invalid"); $("product-select").removeAttribute("aria-invalid");
  $("payload-file").removeAttribute("aria-invalid"); preview();
}
function resetPayloadBanner() {
  $("payload-title").textContent = DEFAULT_PAYLOAD_TITLE;
  $("payload-meta").textContent = DEFAULT_PAYLOAD_META;
}
function formatPayloadPreview(payload) {
  const rows = Array.isArray(payload?.reviews) ? payload.reviews : [];
  return rows.map((row, index) => {
    const rid = `R${String(index + 1).padStart(2, "0")}`;
    const rating = row?.rating_star ?? row?.rating;
    const starText = rating != null && rating !== "" ? `${rating}★ · ` : "";
    const body = String(row?.comment ?? row?.text ?? "").replace(/\s+/g, " ").trim() || "(không có nội dung)";
    return `[${rid}] ${starText}${body}`;
  }).join("\n");
}
function applyPayload(payload, sourceLabel) {
  activePayload = payload;
  const product = payload?.product && typeof payload.product === "object" ? payload.product : {};
  const name = product.name || payload?.product_name || "Sản phẩm Shopee";
  const url = payload?.url || product.url || "";
  const count = Array.isArray(payload?.reviews) ? payload.reviews.length : 0;
  const stars = payload?.counts_by_star && typeof payload.counts_by_star === "object"
    ? Object.entries(payload.counts_by_star).map(([star, n]) => `${star}★: ${n}`).join(" · ")
    : "";
  $("payload-title").textContent = `${sourceLabel}: ${name}`;
  $("payload-meta").textContent = [`${count} review`, stars, url].filter(Boolean).join(" · ");
  $("reviews").value = formatPayloadPreview(payload);
  preview();
}
function inputError(message, target = "reviews") {
  $("form-error").textContent = message; $("form-error").hidden = false;
  $(target).setAttribute("aria-invalid", "true"); $(target).focus();
}
function setBusy(value) {
  busy = value; form.querySelectorAll("input,select,textarea,button").forEach(el => el.disabled = value);
  $("loading").hidden = !value; $("result-region").setAttribute("aria-busy", String(value));
  $("analyze").textContent = value ? "Đang xử lý…" : "Kiểm tra rủi ro";
}
function render(data) {
  const r = data.analysis;
  hasResult = data.origin === "backend" && ["risks", "no_clear_risk", "insufficient"].includes(r.status);
  $("stale-note").hidden = true; snapshot = data.sources || [];
  const titles = { risks: `Có ${r.risks.length} rủi ro cần cân nhắc`, insufficient: "Chưa đủ căn cứ phân tích",
    no_clear_risk: "Chưa thấy rủi ro rõ ràng", refused: "Yêu cầu ngoài phạm vi", invalid_input: "Kiểm tra lại đầu vào", error: "Lần kiểm tra chưa hoàn tất" };
  $("empty-state").hidden = true; $("results").hidden = false;
  $("result-kind").textContent = data.mock ? "CHẾ ĐỘ GIẢ · CHƯA PHÂN TÍCH BẰNG AI THẬT" :
    data.usage?.model_calls ? "KẾT QUẢ PHÂN TÍCH" : "KIỂM TRA DỮ LIỆU · CHƯA GỌI AI";
  $("result-heading").textContent = titles[r.status] || "Chưa thể hiển thị kết quả";
  $("result-message").textContent = r.summary;
  const measured = data.origin === "backend" && r.stats && !["error", "invalid_input", "refused"].includes(r.status);
  ["quantitative", "coverage-section", "signals-section", "sources-section"].forEach(id => $(id).hidden = !measured);
  $("quantitative").replaceChildren(); $("signal-counts").replaceChildren(); $("flag-list").replaceChildren(); $("all-sources").replaceChildren();
  if (measured) {
    const s = r.stats;
    const stats = [[s.total, "review đầu vào"], [s.filtered_noise, `loại theo quy tắc (${s.noise_pct}%)`], [s.kept_clean, "review giữ lại"]];
    $("quantitative").append(...stats.map(([value, label]) => { const el = node("div", undefined, "stat"); el.append(node("strong", value), node("span", label)); return el; }));
    $("signals-summary").textContent = `Tổng ${s.total}, loại ${s.filtered_noise}, giữ ${s.kept_clean}. Đã che thông tin liên hệ trong ${s.pii_redacted_review_count || 0} review.`;
    const labels = { nhieu_trong: "Trống", nhieu_khen_chung: "Khen chung", nhieu_hoi_dap_rao_ban: "Hỏi đáp/rao bán",
      nhieu_ngoai_chat_luong: "Ngoài chất lượng", nhieu_lap_bat_thuong: "Lặp", nhieu_nhan_xu: "Nhận thưởng", nhieu_chua_dung: "Chưa dùng", nhieu_qua_ngan: "Quá ngắn" };
    $("signal-counts").append(...Object.entries(s.noise_breakdown || {}).filter(([, n]) => n > 0).map(([key, n]) => node("li", `${labels[key] || key}: ${n}`)));
    $("anomalies").textContent = r.flags.length ? r.flags.join(" ") : "Chưa có cờ bất thường được backend ghi nhận.";
    const a = r.anomalies;
    $("duplicate-summary").textContent = `${a.duplicate_count || 0}/${a.review_count || 0} review lặp (${Math.round((a.duplicate_rate || 0) * 10000) / 100}%). Không đủ để kết luận seeding/gian lận.`;
    (a.duplicate_clusters || []).forEach(cluster => {
      const el = node("div", undefined, "flag"); el.append(node("p", `Nhóm nội dung lặp: ${cluster.count} review`));
      cluster.review_ids.forEach(id => { if (snapshot.some(source => source.id === id)) el.append(sourceButton(id)); });
      $("flag-list").append(el);
    });
    $("all-sources").append(...snapshot.map(source => { const li = node("li"); li.append(sourceButton(source.id)); return li; }));
    $("coverage-note").textContent = `Mẫu review cho ${r.product_name || "sản phẩm được cung cấp"}. Chưa xác nhận đại diện toàn bộ người mua.`;
  }
  $("risk-list").replaceChildren(...r.risks.slice(0, 3).map((risk, i) => {
    const card = node("article", undefined, "panel risk");
    card.append(node("p", `RỦI RO ${i + 1}`, "eyebrow"), node("h3", risk.title), node("p", risk.summary, "risk-description"));
    risk.citations.forEach(source => {
      const canonical = snapshot.find(row => row.id === source.id); if (!canonical) return;
      const el = node("div", undefined, "evidence"); el.append(node("blockquote", canonical.text), sourceButton(source.id)); card.append(el);
    }); return card;
  }));
  $("state-action").hidden = r.status === "risks"; $("retry").hidden = r.status !== "error";
  const usage = data.usage;
  $("usage-values").textContent = usage ? `Model: ${usage.models.join(", ") || "không gọi"}\nSố lần gọi model: ${usage.model_calls} · Công cụ: ${usage.tool_calls}\nToken vào: ${usage.tokens_in} · Token ra: ${usage.tokens_out}` : "Chưa nhận usage từ backend, không tự ước lượng token.";
  $("usage-mode").textContent = data.mock ? "Fake trả insufficient theo backend main; UI không tự sinh rủi ro. Token 0 không dùng làm bằng chứng AI thật." : "Usage lấy từ tracing; lượt không còn review sạch có thể không gọi model.";
  $("result-heading").focus();
}
form.addEventListener("submit", async event => {
  event.preventDefault(); if (busy) return;
  let request;
  const mode = $("input-mode").value;
  if (mode === "catalog") {
    const id = $("product-select").value;
    if (!id) { inputError("Hãy chọn sản phẩm hoặc bộ minh họa.", "product-select"); return; }
    request = id.startsWith("SP") ? { mode: "catalog", product_id: id } : { mode: "reviews", text: $("reviews").value };
  } else if (mode === "payload") {
    if (!activePayload) { inputError("Chưa có dữ liệu JSON từ extension. Hãy crawl từ extension hoặc chọn file JSON.", "payload-file"); return; }
    request = { mode: "payload", payload: activePayload };
  } else {
    if (!$("reviews").value.trim()) { inputError("Hãy dán tập review, mỗi review một dòng."); return; }
    if (lines().length > limits.max_reviews || lines().some(line => line.length > limits.max_review_chars)) { inputError("Tối đa 250 dòng, mỗi dòng 3.000 ký tự."); return; }
    request = { mode: "reviews", text: $("reviews").value };
  }
  const ticket = revision; $("form-error").hidden = true; $("results").hidden = true; $("empty-state").hidden = true; setBusy(true);
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), 120000);
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(request), signal: controller.signal });
    let data = await response.json();
    if (!response.ok && typeof data.message === "string") data = { analysis: { status: response.status < 500 ? "invalid_input" : "error", summary: data.message, risks: [] }, sources: [], origin: "http_error" };
    if (!data.analysis || !Array.isArray(data.analysis.risks)) throw new Error("invalid-response");
    if (ticket === revision) render(data);
  } catch (_) {
    if (ticket === revision) render({ analysis: { status: "error", summary: "Không thể nhận kết quả. Nội dung vẫn được giữ; kiểm tra kết nối rồi thử lại.", risks: [] }, sources: [] });
  } finally { clearTimeout(timeout); setBusy(false); }
});
function changeMode() {
  const mode = $("input-mode").value;
  $("catalog-fields").hidden = mode !== "catalog";
  $("payload-fields").hidden = mode !== "payload";
  $("reviews").readOnly = mode !== "reviews";
  invalidate();
}
$("input-mode").addEventListener("change", changeMode);
$("reviews").addEventListener("input", invalidate);
$("payload-file").addEventListener("change", async () => {
  const file = $("payload-file").files?.[0];
  invalidate();
  if (!file) { activePayload = null; resetPayloadBanner(); $("reviews").value = ""; preview(); return; }
  try {
    const data = JSON.parse(await file.text());
    if (!data || typeof data !== "object" || Array.isArray(data) || !Array.isArray(data.reviews)) {
      throw new Error("schema");
    }
    applyPayload(data, "Đã nạp từ file JSON");
  } catch (_) {
    activePayload = null; resetPayloadBanner(); $("reviews").value = ""; preview();
    inputError("File JSON không đúng định dạng payload review từ extension Shopee.", "payload-file");
  }
});
$("clear").addEventListener("click", () => {
  hasResult = false; activePayload = null; $("payload-file").value = ""; resetPayloadBanner();
  $("reviews").value = ""; $("product-select").value = ""; $("input-mode").value = "reviews";
  changeMode(); $("reviews").focus();
});
$("edit").addEventListener("click", () => {
  const mode = $("input-mode").value;
  const target = mode === "reviews" ? $("reviews") : mode === "payload" ? $("payload-file") : $("product-select");
  target.focus(); target.scrollIntoView({ block: "center" });
});
$("retry").addEventListener("click", () => form.requestSubmit());
$("close-source").addEventListener("click", () => $("source-dialog").close());
$("source-dialog").addEventListener("close", () => { if (lastSourceButton?.isConnected) lastSourceButton.focus(); });
$("product-select").addEventListener("change", async () => {
  const id = $("product-select").value; invalidate(); const ticket = revision;
  if (!id) { $("reviews").value = ""; preview(); return; }
  try {
    const response = await fetch(`/api/products/${encodeURIComponent(id)}`);
    if (!response.ok) throw new Error("catalog");
    const data = await response.json(); if (ticket !== revision) return;
    $("reviews").value = data.text; preview();
    $("catalog-note").textContent = data.synthetic ? "Bộ synthetic để thử UI, không phải dữ liệu thu thập thật." : "Mẫu review công khai đã lưu; không tải lại trang nguồn.";
  } catch (_) { if (ticket === revision) inputError("Chưa tải được sản phẩm; có thể chuyển sang dán review.", "product-select"); }
});
async function loadExtensionHandoff(handoffId) {
  $("input-mode").value = "payload";
  changeMode();
  $("payload-title").textContent = "Đang tải dữ liệu từ Chrome extension…";
  $("payload-meta").textContent = "Tự động nhận review vừa crawl và chạy kiểm tra rủi ro.";
  const ticket = revision;
  try {
    const response = await fetch(`/api/extension-handoff/${encodeURIComponent(handoffId)}`);
    const data = await response.json();
    if (ticket !== revision) return;
    if (!response.ok || !data.payload) {
      resetPayloadBanner();
      inputError(data.message || "Không tải được dữ liệu từ extension (có thể đã hết hạn).", "payload-file");
      return;
    }
    if (window.history?.replaceState) {
      window.history.replaceState(null, "", window.location.pathname);
    }
    applyPayload(data.payload, "Nhận tự động từ Chrome extension");
    form.requestSubmit();
  } catch (_) {
    if (ticket === revision) {
      resetPayloadBanner();
      inputError("Không kết nối được backend để tải dữ liệu từ extension.", "payload-file");
    }
  }
}
async function init() {
  try {
    const response = await fetch("/api/products"); if (!response.ok) throw new Error("config");
    const data = await response.json(); limits = data.limits;
    data.products.forEach(p => { const option = node("option", `${p.id} · ${p.name} · ${p.review_count} review${p.synthetic ? " minh họa" : ""}`); option.value = p.id; $("product-select").append(option); });
    $("mode").textContent = data.model_provider === "fake" ? "Chế độ giả · Chưa phân tích bằng AI thật" : "Phân tích dựa trên review nhận được";
    $("limit-note").textContent = "Dán tối đa 250 dòng, mỗi dòng 3.000 ký tự. Không bắt buộc số sao hay URL.";
  } catch (_) { $("mode").textContent = "Chưa tải được cấu hình; kiểm tra backend local."; }
  const handoffId = new URLSearchParams(window.location.search).get("handoff");
  if (handoffId) {
    await loadExtensionHandoff(handoffId);
  } else {
    changeMode();
  }
}
init();
