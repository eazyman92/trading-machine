'use strict';
(() => {
  const values={};let fileText='',busy=false,message='',retryKey=null,preview=null;
  const fields=[['tick_usd','Price tick (USD/oz)'],['ounces_per_lot','Troy ounces per lot'],['lot_step','Lot increment'],['minimum_lots','Minimum lots'],['commission_usd_per_lot_side','Commission USD/lot/side'],['risk_budget_usd','Estimated risk budget USD'],['notional_cap_usd','Notional cap USD']];
  function mount(){
    const root=document.querySelector('#research-root');if(!root || root.querySelector('#gold-import'))return;
    const section=document.createElement('section');section.className='panel content-card';section.id='gold-import';
    section.innerHTML='<h2>XAU/USD historical CSV research</h2><p>Import your permitted one-minute bid candles with a declared constant spread per candle. Contract settings must come from your chosen gold product. No broker defaults are assumed.</p><form><label class="field">CSV file (maximum 500 KB, 3,000 rows)<input type="file" accept=".csv,text/csv" required></label><p class="muted">Columns: time,bid_open,bid_high,bid_low,bid_close,spread. UTC bar-open timestamps. Full London 07:00–16:00 sessions required.</p><label class="field">Dataset source, period, rights and product reference<textarea name="provenance" minlength="10" maxlength="2000" required></textarea></label>'+fields.map(([k,label])=>`<label class="field">${label}<input name="${k}" type="number" step="any" min="${k.startsWith('commission')?'0':'0.00000001'}" required></label>`).join('')+'<label><input name="rights_confirmed" type="checkbox" required> I have permission to use this dataset for this research.</label><p class="muted">Intraday USD research only. No financing, broker margin or intratrade drawdown model. Fixed five-tick breakout buffer; not optimized for gold.</p><button class="btn primary" type="submit">Run XAU/USD replay</button><p role="status"></p></form>';
    root.insertBefore(section,root.firstChild.nextSibling);
    const form=section.querySelector('form');
    const strategy=document.createElement('fieldset');
    strategy.innerHTML='<legend>Research strategy rules</legend><p>These are hypotheses to test, not approved trading settings. Sessions stay fixed to London time.</p><label class="field">Breakout buffer (price ticks)<input name="buffer_ticks" type="number" min="0" max="10000" step="1" value="5" required></label><label class="field">Target / entry-to-stop price distance<input name="reward_multiple" type="number" min="0.25" max="10" step="0.25" value="2" required></label><label class="field">Maximum entry spread USD/oz (optional)<input name="max_spread_usd" type="number" min="0.00000001" max="100" step="any"></label>';
    form.insertBefore(strategy,form.querySelector('button'));
    form.querySelectorAll('p').forEach(p=>{if(p.textContent.includes('Fixed five-tick'))p.textContent='Intraday USD research only. No financing, broker margin or intratrade drawdown model. Strategy rule changes require independent evaluation before any promotion.';});
    const range=document.createElement('div');
    range.innerHTML='<label class="field">First London session date (optional)<input type="date" name="start_date"></label><label class="field">Last London session date (inclusive, optional)<input type="date" name="end_date"></label><button type="button" class="btn secondary" id="validate-gold">Preview dataset quality</button><div id="gold-quality" role="status"></div>';
    form.insertBefore(range,form.querySelector('label').nextSibling);
    function showQuality(){
      const output=range.querySelector('#gold-quality');output.replaceChildren();
      if(!preview)return;
      const summary=document.createElement('p');summary.textContent=`${preview.selected_rows} of ${preview.input_rows} rows selected · ${preview.eligible_sessions} complete weekday sessions · spread $${preview.minimum_spread_usd}–$${preview.maximum_spread_usd}/oz. ${preview.first_utc} to ${preview.last_utc}. Source remains unverified.`;output.append(summary);
      for(const s of preview.sessions){const line=document.createElement('p');line.textContent=s.date+': '+(s.eligible?'Eligible session':s.missing_session_minutes+' missing minutes or closed weekend');output.append(line);}
    }
    range.querySelector('button').onclick=async()=>{
      const output=range.querySelector('#gold-quality');output.textContent='Validating dataset…';
      try{const response=await fetch('/api/v1/research/gold/validate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({csv_text:fileText,start_date:values.start_date||null,end_date:values.end_date||null}),signal:AbortSignal.timeout(15000)});
        const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Invalid CSV/date range');preview=data;showQuality();
      }catch(err){output.textContent=err.message;}
    };
    showQuality();
    form.addEventListener('change',e=>{if(e.target.type==='file'){preview=null;showQuality();}});
    for(const [key,value] of Object.entries(values)){if(form.elements[key]){if(key==='rights_confirmed')form.elements[key].checked=value;else form.elements[key].value=value;}}
    form.querySelector('[role=status]').textContent=message;
    form.querySelector('button').disabled=busy;
    form.querySelector('input[type=file]').required=!fileText;
    form.addEventListener('input',e=>{if(e.target.name)values[e.target.name]=e.target.type==='checkbox'?e.target.checked:e.target.value;if(['start_date','end_date'].includes(e.target.name)){preview=null;showQuality();}retryKey=null;});
    form.querySelector('input[type=file]').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(file.size>500000){message='File exceeds 500 KB';fileText='';}else{fileText=await file.text();message='Loaded '+file.name;}retryKey=null;form.querySelector('[role=status]').textContent=message;};
    form.onsubmit=async e=>{
      e.preventDefault();if(busy)return;busy=true;retryKey??=crypto.randomUUID();
      const submittedKey=retryKey;
      form.querySelector('button').disabled=true;form.querySelector('[role=status]').textContent='Submitting XAU/USD research…';
      try{
        const body={csv_text:fileText,start_date:values.start_date||null,end_date:values.end_date||null,provenance:values.provenance,rights_confirmed:values.rights_confirmed===true,spec:Object.fromEntries(fields.map(([k])=>[k,values[k]]))};
        body.rules={buffer_ticks:Number(values.buffer_ticks??5),reward_multiple:values.reward_multiple||'2',max_spread_usd:values.max_spread_usd||null};
        const response=await fetch('/api/v1/research/gold/jobs',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':retryKey},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)});
        if(!response.ok)throw new Error('Gold import rejected (HTTP '+response.status+'). Check CSV and contract settings.');
        const job=await response.json();retryKey=null;message='Gold job submitted: '+job.id;busy=false;window.dispatchEvent(new CustomEvent('research:created',{detail:job}));
      }catch(err){
        if(err.name==='TimeoutError' || err.name==='AbortError' || err instanceof TypeError){
          message='Response interrupted. Checking whether your job was saved…';
          form.querySelector('[role=status]').textContent=message;
          try{
            const recovered=await fetch('/api/v1/research/requests/'+submittedKey,{signal:AbortSignal.timeout(10000)});
            if(recovered.ok){const job=await recovered.json();retryKey=null;busy=false;message='Recovered saved job: '+job.id;window.dispatchEvent(new CustomEvent('research:created',{detail:job}));return;}
          }catch{/* Unknown outcome: preserve the original retry key. */}
          message='Submission outcome is not confirmed. Retry unchanged settings to reuse the same request key; do not create a new submission.';
        }else message=err.message;
        busy=false;const current=document.querySelector('#gold-import form');
        if(current){current.querySelector('[role=status]').textContent=message;current.querySelector('button').disabled=false;}
      }
    };
  }
  window.addEventListener('research:drawn',mount);mount();
})();
