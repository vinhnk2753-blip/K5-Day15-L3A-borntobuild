const API_URL = "http://127.0.0.1:8765/analyze";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "ANALYZE_SHOPEE_REVIEWS") return undefined;

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload)
  })
    .then(async response => {
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || `Backend trả HTTP ${response.status}`);
      sendResponse(result);
    })
    .catch(error => sendResponse({ ok: false, error: error.message }));

  return true;
});
