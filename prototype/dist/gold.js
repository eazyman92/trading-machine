'use strict';
(() => {
  const values={};let fileText='',busy=false,message='',retryKey=null,preview=null;
  let datasetId=null,datasets=[];
  const fields=[['tick_usd','Price tick (USD/oz)'],['ounces_per_lot','Troy ounces per lot'],['lot_step','Lot increment'],['minimum_lots','Minimum lots'],['commission_usd_per_lot_side','Commission USD/lot/side'],['risk_budget_usd','Estimated risk budget USD'],['notional_cap_usd','Notional cap USD']];
  function mount(){
    const root=document.querySelector('#research-root');if(!root || root.querySelector('#gold-import'))return;
    const section=document.createElement('section');section.className='panel content-card';section.id='gold-import';
    section.innerHTML='<h2>XAU/USD historical CSV research</h2><p>Import your permitted one-minute bid candles with a declared constant spread per candle. Contract settings must come from your chosen gold product. No broker defaults are assumed.</p><form><label class="field">CSV file (up to 20 MB for registration; direct runs remain 500 KB / 3,000 rows)<input type="file" accept=".csv,text/csv" required></label><p class="muted">Columns: time,bid_open,bid_high,bid_low,bid_close,spread. UTC bar-open timestamps. Full London 07:00–16:00 sessions required.</p><label class="field">Dataset source, period, rights and product reference<textarea name="provenance" minlength="10" maxlength="2000" required></textarea></label>'+fields.map(([k,label])=>`<label class="field">${label}<input name="${k}" type="number" step="any" min="${k.startsWith('commission')?'0':'0.00000001'}" required></label>`).join('')+'<label><input name="rights_confirmed" type="checkbox" required> I have permission to use this dataset for this research.</label><p class="muted">Intraday USD research only. No financing, broker margin or intratrade drawdown model. Fixed five-tick breakout buffer; not optimized for gold.</p><button class="btn primary" type="submit">Run XAU/USD replay</button><p role="status"></p></form>';
    root.insertBefore(section,root.firstChild.nextSibling);
    const form=section.querySelector('form');
    const library=document.createElement('fieldset');
    library.innerHTML='<legend>Persistent dataset library</legend><p>Register a permitted CSV once (up to 20 MB / 200,000 candles), then run research by its content ID. Source and prices remain unverified.</p><label class="field">Permission / terms reference<input name="rights_reference" maxlength="2000"></label><button type="button" id="register-dataset" class="btn secondary">Register selected CSV</button> <button type="button" id="load-datasets" class="btn secondary">Refresh dataset library</button><label class="field">Saved dataset<select id="dataset-choice"><option value="">Use selected file directly (3,000-row limit)</option></select></label><button type="button" id="split-dataset" class="btn secondary">Create chronological split plan</button><div id="dataset-feedback" role="status"></div>';
    form.insertBefore(library,form.querySelector('label'));
    const choice=library.querySelector('select');
    function options(){choice.replaceChildren(new Option('Use selected file directly (3,000-row limit)',''));for(const d of datasets){choice.add(new Option(d.source.slice(0,70)+' · '+d.id.slice(0,8),d.id));}choice.value=datasetId||'';}
    options();
    choice.onchange=()=>{datasetId=choice.value||null;retryKey=null;preview=null;form.querySelector('input[type=file]').required=!datasetId&&!fileText;const selected=datasets.find(d=>d.id===datasetId);if(selected){values.provenance=selected.source;values.rights_reference=selected.rights_reference;form.elements.provenance.value=selected.source;form.elements.rights_reference.value=selected.rights_reference;}};
    async function refreshLibrary(){const response=await fetch('/api/v1/research/datasets');if(!response.ok)throw new Error('Dataset library unavailable');datasets=(await response.json()).items;options();}
    library.querySelector('#load-datasets').onclick=async()=>{try{await refreshLibrary();}catch(e){library.querySelector('[role=status]').textContent=e.message;}};
    library.querySelector('#register-dataset').onclick=async()=>{
      const feedback=library.querySelector('[role=status]');feedback.textContent='Validating and registering…';
      try{
        const response=await fetch('/api/v1/research/datasets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({csv_text:fileText,source:form.elements.provenance.value,rights_reference:form.elements.rights_reference.value,rights_confirmed:form.elements.rights_confirmed.checked}),signal:AbortSignal.timeout(120000)});
        const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Registration rejected');datasetId=data.id;await refreshLibrary();feedback.textContent='Registered dataset '+data.id+' · '+data.quality.selected_rows+' rows';form.querySelector('input[type=file]').required=false;
      }catch(e){feedback.textContent=e.message;}
    };
    library.querySelector('#split-dataset').onclick=async()=>{
      const feedback=library.querySelector('[role=status]');
      try{if(!datasetId)throw new Error('Choose or register a saved dataset first');const response=await fetch('/api/v1/research/datasets/'+datasetId+'/split-plan');const report=await response.json();if(!response.ok)throw new Error(report.detail);feedback.textContent=Object.entries(report.periods).map(([k,v])=>`${k}: ${v.start_date} to ${v.end_date} (${v.eligible_sessions} sessions)`).join(' | ')+' · Plan '+report.plan_sha256+'. Keep holdout independent.';}catch(e){feedback.textContent=e.message;}
    };
    form.noValidate=true;
    form.querySelector('p[role=status]').setAttribute('data-gold-status','');
    function status(text){
      message=text;
      const current=document.querySelector('#gold-import [data-gold-status]');
      if(current)current.textContent=text;
    }
    const strategy=document.createElement('fieldset');
    strategy.innerHTML='<legend>Research strategy rules</legend><p>These are hypotheses to test, not approved trading settings. Sessions stay fixed to London time.</p><label class="field">Breakout buffer (price ticks)<input name="buffer_ticks" type="number" min="0" max="10000" step="1" value="5" required></label><label class="field">Target / entry-to-stop price distance<input name="reward_multiple" type="number" min="0.25" max="10" step="0.25" value="2" required></label><label class="field">Maximum entry spread USD/oz (optional)<input name="max_spread_usd" type="number" min="0.00000001" max="100" step="any"></label>';
    form.insertBefore(strategy,form.querySelector('button[type=submit]'));
    if(datasetId){const selected=datasets.find(d=>d.id===datasetId);if(selected){values.provenance??=selected.source;values.rights_reference??=selected.rights_reference;}}
    form.querySelectorAll('p').forEach(p=>{if(p.textContent.includes('Fixed five-tick'))p.textContent='Intraday USD research only. No financing, broker margin or intratrade drawdown model. Strategy rule changes require independent evaluation before any promotion.';});
    const range=document.createElement('div');
    range.innerHTML='<label class="field">First London session date (optional)<input type="date" name="start_date"></label><label class="field">Last London session date (inclusive, optional)<input type="date" name="end_date"></label><button type="button" class="btn secondary" id="validate-gold">Preview dataset quality</button><div id="gold-quality" role="status"></div>';
    form.insertBefore(range,form.querySelector('input[type=file]').closest('label').nextSibling);
    function showQuality(){
      const output=range.querySelector('#gold-quality');output.replaceChildren();
      if(!preview)return;
      const summary=document.createElement('p');summary.textContent=`${preview.selected_rows} of ${preview.input_rows} rows selected · ${preview.eligible_sessions} complete weekday sessions · spread $${preview.minimum_spread_usd}–$${preview.maximum_spread_usd}/oz. ${preview.first_utc} to ${preview.last_utc}. Source remains unverified.`;output.append(summary);
      for(const s of preview.sessions){const line=document.createElement('p');line.textContent=s.date+': '+(s.eligible?'Eligible session':s.missing_session_minutes+' missing minutes or closed weekend');output.append(line);}
    }
    range.querySelector('button').onclick=async()=>{
      const output=range.querySelector('#gold-quality');output.textContent='Validating dataset…';
      try{const params=new URLSearchParams();if(values.start_date)params.set('start_date',values.start_date);if(values.end_date)params.set('end_date',values.end_date);
        const response=datasetId?await fetch('/api/v1/research/datasets/'+datasetId+'/quality?'+params,{signal:AbortSignal.timeout(120000)}):await fetch('/api/v1/research/gold/validate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({csv_text:fileText,start_date:values.start_date||null,end_date:values.end_date||null}),signal:AbortSignal.timeout(15000)});
        const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Invalid CSV/date range');preview=data;showQuality();
      }catch(err){output.textContent=err.message;}
    };
    showQuality();
    form.addEventListener('change',e=>{if(e.target.type==='file'){preview=null;showQuality();}});
    for(const [key,value] of Object.entries(values)){if(form.elements[key]){if(key==='rights_confirmed')form.elements[key].checked=value;else form.elements[key].value=value;}}
    form.querySelector('[data-gold-status]').textContent=message;
    form.querySelector('button[type=submit]').disabled=busy;
    form.querySelector('input[type=file]').required=!fileText&&!datasetId;
    form.addEventListener('input',e=>{if(e.target.name)values[e.target.name]=e.target.type==='checkbox'?e.target.checked:e.target.value;if(['start_date','end_date'].includes(e.target.name)){preview=null;showQuality();}retryKey=null;});
    form.querySelector('input[type=file]').onchange=async e=>{const file=e.target.files[0];if(!file)return;datasetId=null;options();if(file.size>20000000){message='File exceeds 20 MB';fileText='';}else{fileText=await file.text();message='Loaded '+file.name;}retryKey=null;form.querySelector('[data-gold-status]').textContent=message;};
    form.onsubmit=async e=>{
      e.preventDefault();if(busy){status('A submission is already in progress. Please wait.');return;}
      const invalid=[...form.elements].filter(el=>el.willValidate && !el.checkValidity());
      if(invalid.length){
        status('Check these fields: '+invalid.map(el=>el.labels?.[0]?.textContent.trim() || el.name || 'CSV file').join('; '));
        invalid[0].focus();invalid[0].scrollIntoView({block:'center'});return;
      }
      if(!fileText&&!datasetId){status('Choose a CSV or saved dataset before submitting.');return;}
      // Read the actual controls at submission rather than relying on input-event history.
      for(const el of form.elements){if(el.name)values[el.name]=el.type==='checkbox'?el.checked:el.value;}
      busy=true;retryKey??=crypto.randomUUID();
      const submittedKey=retryKey;
      form.querySelector('button[type=submit]').disabled=true;form.querySelector('[data-gold-status]').textContent='Submitting XAU/USD research…';
      try{
        const body={csv_text:fileText,start_date:values.start_date||null,end_date:values.end_date||null,provenance:values.provenance,rights_confirmed:values.rights_confirmed===true,spec:Object.fromEntries(fields.map(([k])=>[k,values[k]]))};
        body.rules={buffer_ticks:Number(values.buffer_ticks??5),reward_multiple:values.reward_multiple||'2',max_spread_usd:values.max_spread_usd||null};
        if(datasetId){body.dataset_id=datasetId;delete body.csv_text;delete body.provenance;delete body.rights_confirmed;}
        const response=await fetch('/api/v1/research/gold/'+(datasetId?'stored-jobs':'jobs'),{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':retryKey},body:JSON.stringify(body),signal:AbortSignal.timeout(120000)});
        if(!response.ok){
          let reason='Check CSV, selected dates and contract settings.';
          try{const rejected=await response.json();if(typeof rejected.detail==='string')reason=rejected.detail;else if(Array.isArray(rejected.detail))reason=rejected.detail.map(d=>d.loc.filter(x=>x!=='body').join('.')+': '+d.msg).join('; ');}catch{/* Non-JSON proxy response. */}
          throw new Error('Gold import rejected (HTTP '+response.status+'): '+reason);
        }
        const job=await response.json();retryKey=null;message='Gold job submitted: '+job.id;busy=false;window.dispatchEvent(new CustomEvent('research:created',{detail:job}));
      }catch(err){
        if(err.name==='TimeoutError' || err.name==='AbortError' || err instanceof TypeError){
          message='Response interrupted. Checking whether your job was saved…';
          form.querySelector('[data-gold-status]').textContent=message;
          try{
            const recovered=await fetch('/api/v1/research/requests/'+submittedKey,{signal:AbortSignal.timeout(10000)});
            if(recovered.ok){const job=await recovered.json();retryKey=null;busy=false;message='Recovered saved job: '+job.id;window.dispatchEvent(new CustomEvent('research:created',{detail:job}));return;}
          }catch{/* Unknown outcome: preserve the original retry key. */}
          message='Submission outcome is not confirmed. Retry unchanged settings to reuse the same request key; do not create a new submission.';
        }else message=err.message;
        busy=false;const current=document.querySelector('#gold-import form');
        if(current){current.querySelector('[data-gold-status]').textContent=message;current.querySelector('button[type=submit]').disabled=false;}
      }
    };
  }
  window.addEventListener('research:drawn',mount);mount();
})();
