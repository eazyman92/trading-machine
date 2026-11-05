'use strict';
(() => {
  const values={};let fileText='',busy=false,message='',retryKey=null;
  const fields=[['tick_usd','Price tick (USD/oz)'],['ounces_per_lot','Troy ounces per lot'],['lot_step','Lot increment'],['minimum_lots','Minimum lots'],['commission_usd_per_lot_side','Commission USD/lot/side'],['risk_budget_usd','Estimated risk budget USD'],['notional_cap_usd','Notional cap USD']];
  function mount(){
    const root=document.querySelector('#research-root');if(!root || root.querySelector('#gold-import'))return;
    const section=document.createElement('section');section.className='panel content-card';section.id='gold-import';
    section.innerHTML='<h2>XAU/USD historical CSV research</h2><p>Import your permitted one-minute bid candles with a declared constant spread per candle. Contract settings must come from your chosen gold product. No broker defaults are assumed.</p><form><label class="field">CSV file (maximum 500 KB, 3,000 rows)<input type="file" accept=".csv,text/csv" required></label><p class="muted">Columns: time,bid_open,bid_high,bid_low,bid_close,spread. UTC bar-open timestamps. Full London 07:00–16:00 sessions required.</p><label class="field">Dataset source, period, rights and product reference<textarea name="provenance" minlength="10" maxlength="2000" required></textarea></label>'+fields.map(([k,label])=>`<label class="field">${label}<input name="${k}" type="number" step="any" min="${k.startsWith('commission')?'0':'0.00000001'}" required></label>`).join('')+'<label><input name="rights_confirmed" type="checkbox" required> I have permission to use this dataset for this research.</label><p class="muted">Intraday USD research only. No financing, broker margin or intratrade drawdown model. Fixed five-tick breakout buffer; not optimized for gold.</p><button class="btn primary" type="submit">Run XAU/USD replay</button><p role="status"></p></form>';
    root.insertBefore(section,root.firstChild.nextSibling);
    const form=section.querySelector('form');
    for(const [key,value] of Object.entries(values)){if(form.elements[key]){if(key==='rights_confirmed')form.elements[key].checked=value;else form.elements[key].value=value;}}
    form.querySelector('[role=status]').textContent=message;
    form.querySelector('button').disabled=busy;
    form.querySelector('input[type=file]').required=!fileText;
    form.addEventListener('input',e=>{if(e.target.name)values[e.target.name]=e.target.type==='checkbox'?e.target.checked:e.target.value;retryKey=null;});
    form.querySelector('input[type=file]').onchange=async e=>{const file=e.target.files[0];if(!file)return;if(file.size>500000){message='File exceeds 500 KB';fileText='';}else{fileText=await file.text();message='Loaded '+file.name;}retryKey=null;form.querySelector('[role=status]').textContent=message;};
    form.onsubmit=async e=>{
      e.preventDefault();if(busy)return;busy=true;retryKey??=crypto.randomUUID();
      form.querySelector('button').disabled=true;form.querySelector('[role=status]').textContent='Submitting XAU/USD research…';
      try{
        const body={csv_text:fileText,provenance:values.provenance,rights_confirmed:values.rights_confirmed===true,spec:Object.fromEntries(fields.map(([k])=>[k,values[k]]))};
        const response=await fetch('/api/v1/research/gold/jobs',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':retryKey},body:JSON.stringify(body),signal:AbortSignal.timeout(15000)});
        if(!response.ok)throw new Error('Gold import rejected (HTTP '+response.status+'). Check CSV and contract settings.');
        const job=await response.json();retryKey=null;message='Gold job submitted: '+job.id;busy=false;window.dispatchEvent(new CustomEvent('research:created',{detail:job}));
      }catch(err){busy=false;message=err.message;form.querySelector('[role=status]').textContent=message;form.querySelector('button').disabled=false;}
    };
  }
  window.addEventListener('research:drawn',mount);mount();
})();
