// Kiểm UI bằng Chrome có sẵn và CDP; không cần npm install, không dùng khi chạy app.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

const base = process.env.REVIEW_LENS_TEST_URL || 'http://127.0.0.1:8000';
const chrome = process.env.REVIEW_LENS_CHROME || 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const profile = await fs.mkdtemp(path.join(os.tmpdir(), 'review-lens-browser-'));
const child = spawn(chrome, ['--headless=new', '--disable-gpu', '--remote-debugging-port=0', `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', 'about:blank'], { windowsHide: true, stdio: ['ignore', 'ignore', 'pipe'] });
if (process.env.REVIEW_LENS_BROWSER_DEBUG) child.stderr.on('data', bytes => process.stderr.write(bytes));
child.on('error', error => { console.error(error.message); process.exitCode = 1; });
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
let ws, next = 0;
const pending = new Map();
let report;
try {
  let port;
  for (let i = 0; i < 100; i++) {
    try { port = (await fs.readFile(path.join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; break; } catch { await sleep(100); }
  }
  assert(port, 'Chrome phải khởi động được');
  const tabs = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { ws.addEventListener('open', resolve, { once: true }); ws.addEventListener('error', event => reject(new Error(event.message || event.error?.message || String(event.error) || 'WebSocket connection failed')), { once: true }); });
  ws.addEventListener('message', event => { if (process.env.REVIEW_LENS_BROWSER_DEBUG) console.log('CDP:', String(event.data).slice(0, 250)); const msg = JSON.parse(event.data); if (pending.has(msg.id)) { const { resolve, reject, timer } = pending.get(msg.id); clearTimeout(timer); pending.delete(msg.id); msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result); } });
  async function cdp(method, params = {}) { return new Promise((resolve, reject) => { const id = ++next; const timer = setTimeout(() => { pending.delete(id); reject(new Error(`CDP timeout: ${method}`)); }, 10000); pending.set(id, { resolve, reject, timer }); ws.send(JSON.stringify({ id, method, params })); }); }
  async function evaluate(expression) { const res = await cdp('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }); if (res.exceptionDetails) throw new Error(JSON.stringify(res.exceptionDetails)); return res.result.value; }
  async function waitFor(expression) { for (let i = 0; i < 100; i++) { if (await evaluate(expression)) return; await sleep(100); } throw new Error(`UI timeout: ${expression}`); }
  async function submitText(text) { await evaluate(`document.getElementById('reviews').value=${JSON.stringify(text)};document.getElementById('reviews').dispatchEvent(new Event('input'));document.getElementById('review-form').requestSubmit();`); await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`); }
  async function screenshot(file, width, mobile = false) {
    await cdp('Emulation.setDeviceMetricsOverride', { width, height: mobile ? 844 : 1000, deviceScaleFactor: 1, mobile });
    await sleep(100);
    assert(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'), `Không tràn ngang ở ${width}px`);
    const result = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    await fs.writeFile(file, Buffer.from(result.data, 'base64'));
  }

  await cdp('Page.enable');
  await cdp('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
  await cdp('Page.navigate', { url: base });
  await waitFor(`document.getElementById('product-select')?.options.length === 4`);
  await fs.mkdir('.local', { recursive: true });
  await screenshot('.local/ui-home.png', 1440);
  assert(await evaluate(`document.getElementById('input-mode').value==='link' && document.getElementById('manual-fields').hidden`));
  await evaluate(`document.getElementById('review-form').requestSubmit()`);
  assert(await evaluate(`!document.getElementById('form-error').hidden && document.activeElement.id==='product-url'`));
  await evaluate(`document.getElementById('input-mode').value='reviews';document.getElementById('input-mode').dispatchEvent(new Event('change'));document.getElementById('product-select').value='DEMO01';document.getElementById('product-select').dispatchEvent(new Event('change'))`);
  await waitFor(`document.getElementById('reviews').value.includes('2 |')`);
  await evaluate(`document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Chưa đủ căn cứ phân tích');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`), 0);
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Số lần gọi model: 1'));
  assert((await evaluate(`document.getElementById('coverage-section').textContent`)).includes('Chưa có thống kê lọc nhiễu'));
  assert(!(await evaluate(`document.getElementById('quantitative').textContent`)).includes('%'));
  await screenshot('.local/ui-desktop.png', 1440);
  await screenshot('.local/ui-mobile.png', 390, true);
  await cdp('Emulation.setDeviceMetricsOverride', { width: 320, height: 844, deviceScaleFactor: 1, mobile: true });
  assert(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Không tràn ngang ở 320px');
  await evaluate(`document.getElementById('reviews').value='Không có số sao';document.getElementById('reviews').dispatchEvent(new Event('input'));document.getElementById('review-form').requestSubmit()`);
  assert(await evaluate(`!document.getElementById('form-error').hidden && document.activeElement.id==='reviews'`));
  const fixture = {
    analysis: { status: 'risks', summary: 'Dữ liệu giả lập trong kiểm thử trình duyệt; không phải AI thật.', review_count: 3, model: 'test-only',
      risks: [
        { title: 'Kết nối', summary: 'Fixture kết nối', citations: [{ id:'R01', text:'Tai trái mất kết nối.', rating:2, date:'2026-11-27', variant:'Đen' }] },
        { title: 'Pin', summary: 'Fixture pin', citations: [{ id:'R02', text:'Pin tụt nhanh.', rating:2 }] },
        { title: 'Cảm giác đeo', summary: 'Fixture cảm giác', citations: [{ id:'R03', text:'Đeo đau tai.', rating:3 }] }
      ] },
    sources: [
      { id:'R01', text:'Tai trái mất kết nối.', rating:2, date:'2026-11-27', variant:'Đen' },
      { id:'R02', text:'Pin tụt nhanh.', rating:2 }, { id:'R03', text:'Đeo đau tai.', rating:3 }
    ], coverage: { counts_complete:false }, usage: { models:['test-only'], model_calls:1,tool_calls:0,tokens_in:0,tokens_out:0 },mock:false,origin:'backend'
  };
  await evaluate(`window.originalFetch=window.fetch;window.uiTestFixture=${JSON.stringify(fixture)};window.fetch=(url,options)=>url==='/api/analyze'?Promise.resolve(new Response(JSON.stringify(window.uiTestFixture),{status:200,headers:{'Content-Type':'application/json'}})):window.originalFetch(url,options)`);
  await submitText('2 | Tai trái mất kết nối.');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`), 3);
  await evaluate(`document.querySelector('#risk-list .source-link').click()`);
  assert(await evaluate(`document.getElementById('source-dialog').open`));
  assert.equal(await evaluate(`document.getElementById('source-content').textContent`), 'Tai trái mất kết nối.');
  assert((await evaluate(`document.getElementById('source-context').textContent`)).includes('2 sao'));
  assert((await evaluate(`document.getElementById('source-context').textContent`)).includes('Đen'));
  await evaluate(`document.getElementById('source-dialog').close()`);
  await evaluate(`window.uiTestFixture.analysis={status:'no_clear_risk',summary:'Fixture không có rủi ro rõ.',risks:[],review_count:3}`);
  await submitText('5 | Sử dụng ổn định.');
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Chưa thấy rủi ro rõ ràng');
  await evaluate(`document.getElementById('reviews').value+=String.fromCharCode(10)+'4 | Nội dung mới';document.getElementById('reviews').dispatchEvent(new Event('input'))`);
  assert(await evaluate(`document.getElementById('results').hidden && !document.getElementById('stale-note').hidden`));
  await evaluate(`window.fetch=(url,options)=>url==='/api/analyze'?Promise.reject(new Error('test network')):window.originalFetch(url,options);document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Lần kiểm tra chưa hoàn tất');
  assert(await evaluate(`document.getElementById('quantitative').hidden`));
  await evaluate(`window.fetch=window.originalFetch;document.getElementById('clear').click()`);
  assert.equal(await evaluate(`document.getElementById('reviews').value`), '');
  await evaluate(`document.getElementById('input-mode').value='link';document.getElementById('input-mode').dispatchEvent(new Event('change'));document.getElementById('product-url').value='https://other.example/product/1/2';document.getElementById('product-url').dispatchEvent(new Event('input'));document.getElementById('review-form').requestSubmit()`);
  assert((await evaluate(`document.getElementById('form-error').textContent`)).includes('shopee.vn'));
  report = { passed:true,checks:['link input mode','URL validation','rated-review mode','sample selection','fake backend insufficient without risks','actual tracing usage','no fabricated noise statistics','desktop/mobile 390/320','missing stars rejected','risk cards from explicit QA response fixture','verbatim source and metadata','no_clear_risk QA fixture','stale result reset','network error','clear'],limitations:'Không gọi crawler hoặc OpenAI thật. Ba thẻ rủi ro/no_clear_risk được kiểm bằng response fixture chèn riêng trong browser QA, không có generator trong app.',screenshots:['.local/ui-home.png','.local/ui-desktop.png','.local/ui-mobile.png'] };
  await fs.writeFile('.local/browser-smoke.json', JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));

} finally {
  if (ws) ws.close();
  child.kill();
  // Profile ở thư mục tạm của hệ điều hành, không đụng profile trình duyệt người dùng.
}
