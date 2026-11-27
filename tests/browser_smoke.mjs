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
const exited = new Promise(resolve => { child.once('exit', resolve); child.once('error', resolve); });
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
  assert(await evaluate(`document.getElementById('stale-note').hidden`), 'Không báo kết quả cũ trước lần phân tích đầu tiên');
  await evaluate(`document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Có 3 rủi ro cần cân nhắc');
  assert(await evaluate(`document.getElementById('stale-note').hidden`), 'Ẩn cảnh báo cũ sau khi có kết quả mới');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`), 3);
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Số lần gọi model: 1'));
  assert((await evaluate(`document.getElementById('quantitative').textContent`)).includes('25%'));
  assert((await evaluate(`document.getElementById('signals-summary').textContent`)).includes('Giữ 3/3'));
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Công cụ: 1'));
  await evaluate(`document.querySelector('#risk-list .source-link').click()`);
  assert.equal(await evaluate(`document.getElementById('source-content').textContent`), 'Sau một tuần dùng, tai trái hay mất kết nối.');
  await evaluate(`document.getElementById('source-dialog').close();document.querySelector('#flag-list .source-link').click()`);
  assert.equal(await evaluate(`document.getElementById('source-content').textContent`), 'Giao nhanh, chưa dùng thử nên chưa biết chất lượng.');
  await evaluate(`document.getElementById('source-dialog').close()`);
  await screenshot('.local/ui-desktop.png', 1440);
  await screenshot('.local/ui-mobile.png', 390, true);
  await cdp('Emulation.setDeviceMetricsOverride', { width: 320, height: 844, deviceScaleFactor: 1, mobile: true });
  assert(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Không tràn ngang ở 320px');
  await submitText('5 | Giao hàng nhanh, chưa sử dụng.\n5 | Đánh giá để nhận xu.');
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Chưa đủ căn cứ phân tích');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`), 0);
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Số lần gọi model: 0'));
  assert((await evaluate(`document.getElementById('signals-summary').textContent`)).includes('Giữ 0/3'));
  await submitText('5 | Pin đủ dùng một buổi.\n5 | Âm thanh rõ khi nghe nhạc.\n5 | Đeo thoải mái khi sử dụng.');
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Chưa thấy rủi ro rõ ràng');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`), 0);
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
  await evaluate(`document.getElementById('reviews').dispatchEvent(new Event('input'))`);
  assert(await evaluate(`!document.getElementById('stale-note').hidden`), 'Giữ cảnh báo khi sửa nhiều lần');
  for (const status of [400, 403, 413, 502]) {
    const message = `Thông báo HTTP ${status} từ máy chủ`;
    await evaluate(`window.fetch=(url,options)=>url==='/api/analyze'?Promise.resolve(new Response(JSON.stringify({message:${JSON.stringify(message)}}),{status:${status}})):window.originalFetch(url,options);document.getElementById('review-form').requestSubmit()`);
    await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
    assert.equal(await evaluate(`document.getElementById('result-message').textContent`), message);
    assert(await evaluate(`document.getElementById('quantitative').hidden`));
    assert(await evaluate(`document.getElementById('stale-note').hidden`));
  }
  await evaluate(`window.fetch=(url,options)=>url==='/api/analyze'?Promise.reject(new Error('test network')):window.originalFetch(url,options);document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`), 'Lần kiểm tra chưa hoàn tất');
  assert(await evaluate(`document.getElementById('quantitative').hidden`));
  await evaluate(`window.fetch=window.originalFetch;document.getElementById('clear').click()`);
  assert.equal(await evaluate(`document.getElementById('reviews').value`), '');
  await evaluate(`document.getElementById('input-mode').value='link';document.getElementById('input-mode').dispatchEvent(new Event('change'));document.getElementById('product-url').value='https://other.example/product/1/2';document.getElementById('product-url').dispatchEvent(new Event('input'));document.getElementById('review-form').requestSubmit()`);
  assert((await evaluate(`document.getElementById('form-error').textContent`)).includes('shopee.vn'));
  report = { passed:true,checks:['link input mode','URL validation','rated-review mode','sample selection','fake answer returns 3 sourced risks','actual model/tool tracing usage','measured noise count and percentage','desktop/mobile 390/320','missing stars rejected','real demo risk and flag source popups','G10 blocks noisy-only input without model','risk cards from explicit QA response fixture','verbatim source and metadata','no_clear_risk QA fixture','stale result reset','network error','clear'],limitations:'Không gọi crawler hoặc OpenAI thật. Demo mặc định đi qua answer và fake theo quy tắc; response fixture riêng chỉ dùng để kiểm bổ sung các trạng thái trình duyệt.',screenshots:['.local/ui-home.png','.local/ui-desktop.png','.local/ui-mobile.png'] };
  report.checks.push('no stale warning before first result', 'stale warning cleared after new result', 'HTTP 400/403/413/502 server messages');
  report.checks.push('positive fake input does not force risks');
  await fs.writeFile('.local/browser-smoke.json', JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));

} finally {
  if (ws) ws.close();
  child.kill();
  await exited;
  // Chỉ xóa đúng thư mục riêng do mkdtemp tạo bên trong temp của hệ điều hành.
  const resolvedProfile = path.resolve(profile);
  assert.equal(path.dirname(resolvedProfile), path.resolve(os.tmpdir()));
  assert(path.basename(resolvedProfile).startsWith('review-lens-browser-'));
  await fs.rm(resolvedProfile, { recursive: true, force: true, maxRetries: 20, retryDelay: 100 });
  assert.equal(await fs.stat(resolvedProfile).then(() => true, () => false), false, 'Đã dọn profile QA');
}
