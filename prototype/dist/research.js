'use strict';
(() => {
  let job = null, timer = null, pending = false, error = '', requestKey = null;
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
    try { job=await api('/'+job.id); error=''; } catch (e) { error=e.message; }
    draw(); schedule();
  }
  async function submit() {
    pending=true; error=''; requestKey ??= crypto.randomUUID(); draw();
    try {
      job=await api('', {method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':requestKey},body:JSON.stringify({dataset:'synthetic-london-dst-v1',strategy:'session-breakout-v0.1',symbol:'EUR_USD'})});
      requestKey=null;
    } catch(e) {error=e.message;}
    pending=false; draw(); schedule();
  }
  async function cancel() {
    try {job=await api('/'+job.id+'/cancel',{method:'POST'});error='';} catch(e) {error=e.message;}
    draw();schedule();
  }
  window.addEventListener('research:mount',()=>{draw();schedule();});
  if(location.hash==='#research') {draw();schedule();}
})();
