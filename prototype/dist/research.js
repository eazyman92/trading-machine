'use strict';
(() => {
  let job = null, timer = null, pending = false, error = '', requestKey = null;
  let history = [], offset = 0, nextOffset = null, selection = 0;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const terminal = () => job && ['completed','failed','cancelled'].includes(job.status);
  function draw() {
    const root = document.querySelector('#research-root');
    if (!root) return;
    const result = job?.result;
    root.innerHTML = `<div class="page-heading"><div><div class="eyebrow">BACKEND-CONNECTED RESEARCH</div><h1>Research lab</h1><p class="muted">Run a reproducible test and inspect the actual worker output.</p></div></div>
      <div class="notice">Synthetic engineering fixtures only. These results do not measure historical profitability. No broker or AI is connected.</div>
      <section class="panel content-card"><h2>London session breakout v0.1</h2><p>EUR/USD · one-minute synthetic bid/ask candles · two sessions spanning the London DST change.</p><p class="muted">Fixed fixture: $25 estimated risk budget, $10,000 notional cap, spread, fees and adverse slippage. Parameters are locked for this first integration.</p>
      <button class="btn primary" id="run-research" ${pending || (job && !terminal()) ? 'disabled' : ''}>${pending ? 'Submitting…' : requestKey && !job ? 'Retry submission' : 'Run synthetic backtest'}</button>
      ${job && !terminal() ? '<button class="btn secondary" id="cancel-research">Cancel job</button>' : ''}
      <p role="status" aria-live="polite">${job ? 'Job: '+escape(job.status)+' · '+escape(job.id) : 'Ready to run'}</p><p class="form-error" role="alert">${escape(error)}</p>
      ${job?.error ? `<p role="alert">Worker error: ${escape(job.error)}</p>` : ''}</section>
      ${result ? `<section class="panel content-card"><h2>Completed fixture replay</h2><p>${escape(result.bar_count)} candles · ${escape(result.trades.length)} trades · ${escape(result.rejected_sessions.length)} excluded sessions</p><p class="muted">${escape(result.cost_model)}</p><div style="overflow-x:auto"><table><thead><tr><th>Session</th><th>Side</th><th>Units</th><th>Entry (UTC)</th><th>Exit reason</th><th>Net USD</th></tr></thead><tbody>${result.trades.map(t=>`<tr><td>${escape(t.session)}</td><td>${escape(t.side)}</td><td>${escape(t.units)}</td><td>${escape(t.entry_at)}</td><td>${escape(t.reason)}</td><td>${escape(t.net_usd)}</td></tr>`).join('')}</tbody></table></div><details><summary>Trade details, exclusions and reproducibility metadata</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${escape(JSON.stringify(result,null,2))}</pre></details><p class="muted">Dataset SHA-256: <span style="overflow-wrap:anywhere">${escape(result.dataset_sha256)}</span></p></section>` : ''}`;
    root.querySelector('#run-research').addEventListener('click', submit);
    root.querySelector('#cancel-research')?.addEventListener('click', cancel);
    const saved = document.createElement('section');
    saved.className='panel content-card';
    saved.innerHTML=`<h2>Saved research runs</h2><p class="muted">Saved in the development database. Select a run to reopen its results.</p><button class="btn secondary" id="refresh-history">Refresh history</button><div>${history.map(h=>`<p><button class="btn secondary" data-job-id="${escape(h.id)}">${escape(new Date(h.created_at*1000).toISOString())} · ${escape(h.status)} · ${escape(h.id.slice(0,8))}</button></p>`).join('') || '<p>No saved runs on this page.</p>'}</div><button class="btn secondary" id="history-prev" ${offset===0?'disabled':''}>Previous</button> <button class="btn secondary" id="history-next" ${nextOffset===null?'disabled':''}>Next</button>`;
    root.append(saved);
    saved.querySelector('#refresh-history').onclick=()=>loadHistory(false);
    saved.querySelector('#history-prev').onclick=()=>{offset=Math.max(0,offset-20);loadHistory(false);};
    saved.querySelector('#history-next').onclick=()=>{offset=nextOffset;loadHistory(false);};
    saved.querySelectorAll('[data-job-id]').forEach(b=>b.onclick=()=>openJob(b.dataset.jobId));
  }
  async function api(path, options) {
    const response = await fetch('/api/v1/research/jobs'+path, {...options, signal: AbortSignal.timeout(10000)});
    if (!response.ok) throw new Error(`Research API returned ${response.status}. Check the API and worker services.`);
    return response.json();
  }
  function schedule() {
    clearTimeout(timer);
    if (job && !terminal() && document.querySelector('#research-root')) timer=setTimeout(poll,750);
  }
  async function poll() {
    const current=selection, id=job.id;
    try { const fetched=await api('/'+id); if(current!==selection)return; job=fetched; error=''; } catch (e) { if(current!==selection)return; error=e.message; }
    draw(); schedule();
    if(terminal())loadHistory(false);
  }
  async function openJob(id) {
    const current=++selection; clearTimeout(timer);
    try {const fetched=await api('/'+id);if(current!==selection)return;job=fetched;error='';}catch(e){if(current!==selection)return;error=e.message;}
    draw();schedule();
  }
  async function loadHistory(restore) {
    try {const data=await api('?limit=20&offset='+offset);history=data.items;nextOffset=data.next_offset;error='';
      if(restore && !job && history.length){await openJob(history[0].id);return;}
    }catch(e){error=e.message;}
    draw();
  }
  async function submit() {
    ++selection;
    pending=true; error=''; requestKey ??= crypto.randomUUID(); draw();
    try {
      job=await api('', {method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':requestKey},body:JSON.stringify({dataset:'synthetic-london-dst-v1',strategy:'session-breakout-v0.1',symbol:'EUR_USD'})});
      requestKey=null;
    } catch(e) {error=e.message;}
    pending=false; draw(); schedule();
    loadHistory(false);
  }
  async function cancel() {
    try {job=await api('/'+job.id+'/cancel',{method:'POST'});error='';} catch(e) {error=e.message;}
    draw();schedule();
  }
  window.addEventListener('research:mount',()=>{draw();schedule();loadHistory(true);});
  if(location.hash==='#research') {draw();schedule();loadHistory(true);}
})();
