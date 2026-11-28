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
  await waitFor(`document.getElementById('product-select')?.options.length >= 7`);
  assert(await evaluate(`!!document.querySelector('#product-select option[value="SP06"]')`), 'Catalog CP3 có SP06');
  await fs.mkdir('.local', { recursive:true });
  assert(await evaluate(`document.getElementById('input-mode').value==='catalog' && !document.getElementById('product-url')`));
  await screenshot('.local/ui-home.png',1440);
  await evaluate(`document.getElementById('product-select').value='SP01';document.getElementById('product-select').dispatchEvent(new Event('change'))`);
  await waitFor(`document.getElementById('reviews').value.includes('[R01]')`);
  assert(await evaluate(`document.getElementById('stale-note').hidden`));
  await evaluate(`document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`),'Chưa đủ căn cứ phân tích');
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`),0);
  assert.equal(await evaluate(`document.querySelectorAll('#all-sources button').length`),20);
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Công cụ: 3'));
  assert(!(await evaluate(`document.getElementById('results').textContent`)).includes('undefined'));
  await evaluate(`document.querySelector('#all-sources button').click()`);
  assert(await evaluate(`document.getElementById('source-dialog').open && document.getElementById('source-content').textContent.length>0`));
  assert((await evaluate(`document.getElementById('source-context').textContent`)).includes('Không có số sao'));
  await evaluate(`document.getElementById('source-dialog').close()`);
  await screenshot('.local/ui-desktop.png',1440);
  await screenshot('.local/ui-mobile.png',390,true);
  await cdp('Emulation.setDeviceMetricsOverride',{width:320,height:844,deviceScaleFactor:1,mobile:true});
  assert(await evaluate('document.documentElement.scrollWidth <= window.innerWidth'));
  await evaluate(`document.getElementById('product-select').value='DEMO03';document.getElementById('product-select').dispatchEvent(new Event('change'))`);
  await waitFor(`document.getElementById('reviews').value.includes('Đường may')`);
  assert.equal(await evaluate(`document.getElementById('reviews').value.split(String.fromCharCode(10)).length`),3);
  await evaluate(`document.getElementById('input-mode').value='reviews';document.getElementById('input-mode').dispatchEvent(new Event('change'))`);
  const normal='[R01] Tai trái mất kết nối khi dùng ngoài đường.\n[R02] Pin nhanh hết sau một giờ nghe nhạc.\n[R03] Đeo lâu bị đau tai.';
  await submitText(normal+'\n[R04] Tai trái mất kết nối khi dùng ngoài đường.');
  assert((await evaluate(`document.getElementById('duplicate-summary').textContent`)).includes('1/4'));
  assert.equal(await evaluate(`document.querySelectorAll('#flag-list button').length`),2);
  await evaluate(`document.querySelectorAll('#flag-list button')[1].click()`);
  assert.equal(await evaluate(`document.getElementById('source-content').textContent`),'Tai trái mất kết nối khi dùng ngoài đường.');
  await evaluate(`document.getElementById('source-dialog').close()`);
  await sleep(30); // Cho sự kiện close khôi phục focus trước thao tác tiếp theo.
  await evaluate(`document.getElementById('edit').click()`);
  assert.equal(await evaluate('document.activeElement.id'),'reviews');
  await evaluate(`document.getElementById('reviews').dispatchEvent(new Event('input'))`);
  assert(await evaluate(`!document.getElementById('stale-note').hidden`));
  await submitText('[R01] Chưa sử dụng.\n[R02] Đánh giá để nhận xu.');
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`),'Chưa đủ căn cứ phân tích');
  assert((await evaluate(`document.getElementById('usage-values').textContent`)).includes('Số lần gọi model: 0'));

  // Fixture chỉ dùng trong QA để kiểm nhánh rủi ro thật; app không có bộ fake riêng.
  const sources=[{id:'R01',text:'Pin nhanh hết.',rating:2,date:'2026-11-28',variant:'Đen'},
    {id:'R02',text:'Tai trái mất kết nối.',rating:null},{id:'R03',text:'Đeo lâu đau tai.',rating:3}];
  const fixture={analysis:{status:'risks',summary:'Fixture QA, không phải AI thật.',review_count:3,
    stats:{total:3,filtered_noise:0,noise_pct:0,kept_clean:3,noise_breakdown:{},pii_redacted_review_count:0,source:'QA'},
    flags:[],anomalies:{duplicate_count:0,duplicate_rate:0,review_count:3,duplicate_clusters:[],flags:[]},
    reviews_by_id:Object.fromEntries(sources.map(s=>[s.id,s.text])),
    risks:sources.map((s,i)=>({title:'Rủi ro '+(i+1),summary:'Fixture QA',citations:[s]}))},
    sources,usage:{models:['test-only'],model_calls:1,tool_calls:3,tokens_in:0,tokens_out:0},mock:false,origin:'backend'};
  await evaluate(`window.originalFetch=window.fetch;window.uiTestFixture=${JSON.stringify(fixture)};window.fetch=(url,options)=>url==='/api/analyze'?Promise.resolve(new Response(JSON.stringify(window.uiTestFixture),{status:200})):window.originalFetch(url,options)`);
  await submitText(normal);
  assert.equal(await evaluate(`document.querySelectorAll('#risk-list article').length`),3);
  await evaluate(`document.querySelector('#risk-list .source-link').click()`);
  assert.equal(await evaluate(`document.getElementById('source-content').textContent`),'Pin nhanh hết.');
  assert((await evaluate(`document.getElementById('source-context').textContent`)).includes('Đen'));
  await evaluate(`document.getElementById('source-dialog').close();window.uiTestFixture.analysis.status='no_clear_risk';window.uiTestFixture.analysis.risks=[]`);
  await submitText(normal);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`),'Chưa thấy rủi ro rõ ràng');
  for(const status of [400,403,413,502]){
    const message='Thông báo HTTP '+status;
    await evaluate(`window.fetch=(url,options)=>url==='/api/analyze'?Promise.resolve(new Response(JSON.stringify({message:${JSON.stringify(message)}}),{status:${status}})):window.originalFetch(url,options);document.getElementById('review-form').requestSubmit()`);
    await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
    assert.equal(await evaluate(`document.getElementById('result-message').textContent`),message);
    assert(await evaluate(`document.getElementById('signals-section').hidden && document.getElementById('quantitative').hidden`));
    await evaluate(`document.getElementById('reviews').dispatchEvent(new Event('input'))`);
    assert(await evaluate(`document.getElementById('stale-note').hidden`),'Lỗi không tạo hasResult');
  }
  await evaluate(`window.fetch=(url,options)=>url==='/api/analyze'?Promise.reject(new Error('test network')):window.originalFetch(url,options);document.getElementById('review-form').requestSubmit()`);
  await waitFor(`!document.getElementById('results').hidden && !document.getElementById('analyze').disabled`);
  assert.equal(await evaluate(`document.getElementById('result-heading').textContent`),'Lần kiểm tra chưa hoàn tất');
  await evaluate(`window.fetch=window.originalFetch;document.getElementById('clear').click();document.getElementById('reviews').value='Review mới';document.getElementById('reviews').dispatchEvent(new Event('input'))`);
  assert(await evaluate(`document.getElementById('stale-note').hidden`),'Clear reset hasResult');
  assert.equal(await evaluate('document.activeElement.id'),'reviews');
  report={passed:true,checks:['catalog SP01-SP03','raw review without URL/stars','catalog fake insufficient','native stats render','all reviews_by_id popup','missing rating metadata','desktop/mobile 390/320','DEMO03 has 3 rows','native anomaly flags dict','duplicate cluster sources','edit focuses reviews','stale only after success','no clean review no model','risk cards QA fixture','verbatim citation QA fixture','no_clear_risk QA fixture','HTTP 400/403/413/502 messages','error does not set hasResult','network error','clear resets hasResult'],
    limitations:'Fake dùng backend main trả insufficient. Nhánh risks/no_clear_risk dùng response fixture riêng trong QA; không gọi API/crawler thật.',
    screenshots:['.local/ui-home.png','.local/ui-desktop.png','.local/ui-mobile.png']};
  await fs.writeFile('.local/browser-smoke.json',JSON.stringify(report,null,2));
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
