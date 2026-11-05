'use strict';
(() => {
  let job = null, timer = null, pending = false, error = '', requestKey = null;
  let history = [], offset = 0, nextOffset = null, selection = 0;
  let openingId = null;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const terminal = () => job && ['completed','failed','cancelled'].includes(job.status);
  function draw() {
    const root = document.querySelector('#research-root');
    if (!root) return;
    const result = job?.status==='completed'?job.result:null;
    root.innerHTML = `<div class="page-heading"><div><div class="eyebrow">BACKEND-CONNECTED RESEARCH · GOLD IMPORT 2</div><h1>Research lab</h1><p class="muted">Run a reproducible test and inspect the actual worker output.</p></div></div>
      <div class="notice">Synthetic engineering fixtures only. These results do not measure historical profitability. No broker or AI is connected.</div>
      <section class="panel content-card"><h2>London session breakout v0.1</h2><p>EUR/USD · one-minute synthetic bid/ask candles · two sessions spanning the London DST change.</p><p class="muted">Fixed fixture: $25 estimated risk budget, $10,000 notional cap, spread, fees and adverse slippage. Parameters are locked for this first integration.</p>
      <button class="btn primary" id="run-research" ${pending || (job && !terminal()) ? 'disabled' : ''}>${pending ? 'Submitting…' : requestKey && !job ? 'Retry submission' : 'Run synthetic backtest'}</button>
      ${job && !terminal() ? '<button class="btn secondary" id="cancel-research">Cancel job</button>' : ''}
      <p role="status" aria-live="polite">${job ? 'Job: '+escape(job.status)+' · '+escape(job.id) : 'Ready to run'}</p><p class="form-error" role="alert">${escape(error)}</p>
      ${job?.error ? `<p role="alert">Worker error: ${escape(job.error)}</p>` : ''}</section>
      ${result ? `<section class="panel content-card"><h2>Completed fixture replay</h2><p>${escape(result.bar_count)} candles · ${escape(result.trades.length)} trades · ${escape(result.rejected_sessions.length)} excluded sessions</p><p class="muted">${escape(result.cost_model)}</p><div style="overflow-x:auto"><table><thead><tr><th>Session</th><th>Side</th><th>Units</th><th>Entry (UTC)</th><th>Exit reason</th><th>Net USD</th></tr></thead><tbody>${result.trades.map(t=>`<tr><td>${escape(t.session)}</td><td>${escape(t.side)}</td><td>${escape(t.units)}</td><td>${escape(t.entry_at)}</td><td>${escape(t.reason)}</td><td>${escape(t.net_usd)}</td></tr>`).join('')}</tbody></table></div><details><summary>Trade details, exclusions and reproducibility metadata</summary><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${escape(JSON.stringify(result,null,2))}</pre></details><p class="muted">Dataset SHA-256: <span style="overflow-wrap:anywhere">${escape(result.dataset_sha256)}</span></p></section>` : ''}`;
    root.querySelector('#run-research').addEventListener('click', submit);
    root.querySelector('#cancel-research')?.addEventListener('click', cancel);
    if(job?.status==='running' && job.result?.progress){const progress=document.createElement('p');const p=job.result.progress;progress.textContent=`Research progress: ${p.stage} · ${p.done}/${p.total} sessions or phase steps`;root.querySelector('section.panel').append(progress);}
    const saved = document.createElement('section');
    saved.className='panel content-card';
    saved.innerHTML=`<h2>Saved research runs</h2><p class="muted">Saved in the development database. Select a run to reopen its results.</p><button class="btn secondary" id="refresh-history">Refresh history</button><div>${history.map(h=>`<p><button class="btn secondary" data-job-id="${escape(h.id)}">${escape(new Date(h.created_at*1000).toISOString())} · ${escape(h.status)} · ${escape(h.id.slice(0,8))}</button></p>`).join('') || '<p>No saved runs on this page.</p>'}</div><button class="btn secondary" id="history-prev" ${offset===0?'disabled':''}>Previous</button> <button class="btn secondary" id="history-next" ${nextOffset===null?'disabled':''}>Next</button>`;
    root.append(saved);
    const selectionNotice=document.createElement('p');
    selectionNotice.setAttribute('role','status');
    selectionNotice.textContent=openingId ? 'Opening run '+openingId+'…' : job ? 'Selected run: '+job.id : 'Choose a saved run';
    saved.insertBefore(selectionNotice,saved.querySelector('#refresh-history'));
    if(result){
      const resultPanel=root.querySelectorAll('section.panel')[1];
      resultPanel.id='selected-research-result';
      resultPanel.tabIndex=-1;
      const identity=document.createElement('p');
      identity.textContent='Results for run: '+job.id;
      resultPanel.insertBefore(identity,resultPanel.children[1]);
    }
    saved.querySelector('#refresh-history').onclick=()=>loadHistory(false);
    saved.querySelector('#history-prev').onclick=()=>{offset=Math.max(0,offset-20);loadHistory(false);};
    saved.querySelector('#history-next').onclick=()=>{offset=nextOffset;loadHistory(false);};
    saved.querySelectorAll('[data-job-id]').forEach(b=>{
      const selected=b.dataset.jobId===job?.id;
      b.setAttribute('aria-pressed',String(selected));
      b.classList.toggle('primary',selected);
      b.classList.toggle('secondary',!selected);
      if(selected)b.textContent+=' · Selected';
      b.disabled=pending;
      b.onclick=()=>openJob(b.dataset.jobId,true);
    });
    if(job?.config?.symbol==='XAU_USD'){
      const submissionPanel=root.querySelector('section.panel');
      submissionPanel.querySelector('h2').textContent='Selected XAU/USD research job';
      submissionPanel.querySelector('p').textContent='Gold session breakout · imported CSV · user-declared contract and costs.';
      submissionPanel.querySelectorAll('p')[1].textContent='Use the gold import form above to submit another gold run. The button below starts the separate EUR/USD fixture.';
      submissionPanel.querySelector('#run-research').textContent='Run EUR/USD synthetic fixture';
    }
    if(result?.symbol==='XAU_USD'){
      const panel=root.querySelector('#selected-research-result');
      panel.querySelector('h2').textContent='XAU/USD imported-data replay';
      panel.querySelectorAll('tbody tr').forEach((row,i)=>row.children[2].textContent=result.trades[i].quantity_lots+' lots');
      const note=document.createElement('p');note.textContent=result.warning;panel.prepend(note);
      panel.querySelectorAll('th')[2].textContent='Quantity (lots)';
      const metrics=document.createElement('div');metrics.className='stats';
      const m=result.metrics||{};
      const usd=value=>value===undefined?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(Number(value));
      const cards=[['Net result after costs',usd(m.net_usd)],['Closed-trade drawdown',usd(m.closed_trade_drawdown_usd)],['Commission (included in net)',usd(m.commission_usd)],['Trades / win rate',String(m.trade_count??result.trades.length)+' / '+(m.win_rate==null?'N/A':(Number(m.win_rate)*100).toFixed(1)+'%')]];
      metrics.innerHTML=cards.map(([label,value])=>`<div class="stat"><div class="stat-label">${escape(label)}</div><div class="stat-value">${escape(value)}</div></div>`).join('');
      panel.insertBefore(metrics,panel.querySelector('table').parentElement);
      if(result.closed_trade_curve){
        const curves=document.createElement('section');
        const series=result.closed_trade_curve;
        function plot(field,title,color){
          const points=series.map(p=>Number(p[field]));const lo=Math.min(0,...points),hi=Math.max(0,...points),span=hi-lo||1;
          const coords=points.map((y,i)=>`${30+i*540/Math.max(1,points.length-1)},${130-(y-lo)*100/span}`).join(' ');
          return `<h3>${title}</h3><svg viewBox="0 0 600 160" role="img" aria-label="${title}; trade index on horizontal axis, USD on vertical axis" style="width:100%;max-width:800px"><text x="30" y="16" fill="currentColor">USD ${hi.toFixed(2)} / ${lo.toFixed(2)}</text><polyline points="${coords}" fill="none" stroke="${color}" stroke-width="2"/><text x="30" y="155" fill="currentColor">Trade 0 → ${points.length-1}</text></svg>`;
        }
        curves.innerHTML='<p class="muted">Closed-trade P&amp;L only; excludes intratrade moves, deposits and account equity. Values between closes are unknown.</p>'+plot('cumulative_net_usd','Cumulative net P&L (USD)','#b7ef83')+plot('drawdown_usd','Closed-trade drawdown (USD)','#f2b47e');
        panel.append(curves);
      }
      if(!result.trades.length){const empty=document.createElement('p');empty.className='notice';empty.textContent=result.no_trade_explanation || 'No trades were recorded. This older report has no rejection diagnostics; rerun to collect them.';panel.insertBefore(empty,metrics.nextSibling);}
      if(Object.keys(result.sizing_rejections||{}).length){const diagnostics=document.createElement('p');diagnostics.textContent='Rejected sizing attempts (not unique signals): '+Object.entries(result.sizing_rejections).map(([k,v])=>k.replaceAll('_',' ')+': '+v).join('; ');panel.append(diagnostics);}
      if(result.strategy_config){
        const evidence=document.createElement('section');
        const title=document.createElement('h3');title.textContent='Why these trades were taken';evidence.append(title);
        for(const t of result.trades){const p=document.createElement('p'),s=t.signal_evidence;p.textContent=s?`${t.session}: ${t.side} — completed midpoint close ${s.signal_mid_close} broke the ${s.range_low}–${s.range_high} range with a ${s.buffer_price} buffer. Next-bar entry ${t.entry}, stop ${t.stop}, target ${t.target}; estimated stop risk $${s.estimated_stop_risk_usd}. Exit: ${t.reason}.`:'Decision evidence unavailable in this older run.';evidence.append(p);}
        const version=document.createElement('p');version.textContent='Research-only strategy configuration: '+result.strategy_config_sha256;evidence.append(version);panel.append(evidence);
      }
    }
    window.dispatchEvent(new Event('research:drawn'));
    const goldRuns=history.filter(h=>h.status==='completed' && h.config.symbol==='XAU_USD');
    const comparison=document.createElement('section');comparison.className='panel content-card';
    const options=goldRuns.map(h=>`<option value="${escape(h.id)}">${escape(h.id.slice(0,8))} · ${escape(new Date(h.created_at*1000).toISOString())}</option>`).join('');
    comparison.innerHTML=`<h2>Compare saved gold runs</h2><p>Choose two completed runs from the current history page. Exact CSV and date range must match. Contract/cost differences will be disclosed.</p><label class="field">Baseline<select id="compare-left">${options}</select></label><label class="field">Candidate<select id="compare-right">${options}</select></label><button class="btn secondary" ${goldRuns.length<2?'disabled':''}>Compare runs</button><div role="status"></div>`;
    root.append(comparison);
    comparison.querySelector('button').onclick=async()=>{
      const output=comparison.querySelector('[role=status]');output.textContent='Comparing…';
      try{
        const query=new URLSearchParams({left:comparison.querySelector('#compare-left').value,right:comparison.querySelector('#compare-right').value});
        const response=await fetch('/api/v1/research/comparison?'+query,{signal:AbortSignal.timeout(10000)});const report=await response.json();
        if(!response.ok)throw new Error(report.detail||'Comparison failed');
        output.replaceChildren();
        for(const text of ['Baseline net USD: '+report.left_metrics.net_usd,'Candidate net USD: '+report.right_metrics.net_usd,'Candidate minus baseline USD: '+report.net_delta_usd,'Baseline strategy: '+report.left_strategy+'; candidate: '+report.right_strategy,...Object.entries(report.changed_settings).map(([k,v])=>k.replaceAll('_',' ')+': '+v.left+' → '+v.right),report.warning]){const p=document.createElement('p');p.textContent=text;output.append(p);}
      }catch(err){output.textContent=err.message;}
    };
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
  async function openJob(id, reveal=false) {
    const current=++selection; clearTimeout(timer);
    openingId=id;error='';draw();
    try {const fetched=await api('/'+id);if(current!==selection)return;job=fetched;error='';}catch(e){if(current!==selection)return;error=e.message;}
    openingId=null;
    draw();schedule();
    if(reveal && !error){
      const target=document.querySelector('#selected-research-result') || document.querySelector('#research-root');
      target?.focus({preventScroll:true});
      target?.scrollIntoView({behavior:'auto',block:'start'});
    }
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
  window.addEventListener('research:created',e=>{job=e.detail;error='';draw();schedule();loadHistory(false);const target=document.querySelector('#selected-research-result') || document.querySelector('#research-root > section:not(#gold-import)');target?.scrollIntoView({block:'start'});});
  if(location.hash==='#research') {draw();schedule();loadHistory(true);}
})();
