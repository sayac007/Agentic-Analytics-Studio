'use strict';
const $=id=>document.getElementById(id);
const fmt=n=>Number(n).toLocaleString('de-DE',{maximumFractionDigits:2});
function el(tag,text,parent){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(parent)parent.append(e);return e;}
async function api(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:'Ungültige Anfrage. Bitte verwende die angebotenen Optionen.');return data;}
function chart(container,periods,lines,split=60){
 const ns='http://www.w3.org/2000/svg';const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 1000 350');svg.setAttribute('role','img');svg.setAttribute('aria-label',lines.map(l=>l.name).join(', '));
 const node=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))e.setAttribute(k,v);if(text!==undefined)e.textContent=text;svg.append(e);return e;};
 const all=lines.flatMap(l=>l.values),lo=Math.min(0,...all),hi=Math.max(...all),span=Math.max(hi-lo,1),x=i=>65+i*905/Math.max(periods.length-1,1),y=v=>260-(v-lo)*225/span;
 for(let j=0;j<=4;j++){const v=lo+span*j/4;node('line',{x1:65,x2:970,y1:y(v),y2:y(v),stroke:'#e0e9e4'});node('text',{x:55,y:y(v)+4,'text-anchor':'end',fill:'#687d75','font-size':11},fmt(v));}
 if(split<periods.length)node('line',{x1:x(split),x2:x(split),y1:30,y2:265,stroke:'#8c9c97','stroke-dasharray':'4 4'});
 lines.forEach((l,i)=>{node('polyline',{points:l.values.map((v,j)=>`${x(j)},${y(v)}`).join(' '),fill:'none',stroke:l.color,'stroke-width':2});node('text',{x:65+(i%3)*300,y:310+Math.floor(i/3)*21,fill:l.color,'font-size':12},l.name);});
 [0,Math.floor((periods.length-1)/2),periods.length-1].forEach(i=>node('text',{x:x(i),y:285,'text-anchor':'middle',fill:'#687d75','font-size':11},periods[i]));
 container.replaceChildren(svg);
}
function render(data){
 $('results').hidden=false;const r=data.result;$('metrics').replaceChildren();
 [['Holdout RMSE',r.metrics.test.rmse,'12 Monate · count-equivalent'],['Media-Koeffizient',r.coefficients.media.estimate,'Geschätzt · feste Oracle-Transformation'],['Media-Beitrag',r.contribution.total.estimate,'Geschätzte Summe · Holdout 2023']].forEach(([title,value,note])=>{const c=el('div',undefined,$('metrics'));c.className='card';el('small',title,c);el('strong',fmt(value),c);el('span',note,c);});
 $('interpretation').textContent=data.interpretation;$('formula').textContent=data.formula;$('coefficients').replaceChildren();
 Object.entries(r.coefficients).filter(([,v])=>v!==null).forEach(([name,v])=>{const tr=el('tr',undefined,$('coefficients'));[name,v.estimate,v.standard_error,v.lower,v.upper].forEach(x=>el('td',typeof x==='number'?fmt(x):x,tr));});
 $('truth').textContent=`Separater Ground-Truth-Vergleich: β = ${fmt(data.ground_truth.media_coefficient)}. Nicht als Estimator-Eingabe verwendet.`;
 $('warnings').replaceChildren();data.warnings.forEach(w=>el('li',w,$('warnings')));$('identity').textContent=JSON.stringify({seed:data.dataset.seed,hashes:data.hashes,software:data.software},null,2);
 chart($('timeseries'),data.series.periods,[{name:'Synthetisches Outcome',values:data.series.outcome,color:'#255f93'},{name:'Geschätzte Vorhersage',values:data.series.prediction,color:'#d88537'},{name:'Geschätzte Baseline',values:data.series.estimated_baseline,color:'#879a91'},{name:'Geschätzter Media-Beitrag',values:data.series.estimated_media,color:'#178074'}]);
}
$('run-form').addEventListener('submit',async e=>{e.preventDefault();$('run').disabled=true;$('results').hidden=true;$('status').textContent='Analyse läuft: generieren, isoliert schätzen, Verträge und Hashes prüfen …';try{const data=await api('/api/runs',{dataset:$('dataset').value,model:$('model').value});render(data);$('status').textContent='Analyse abgeschlossen · Ergebnis validiert · SYNTHETIC / NOT EMPIRICAL';}catch(err){$('status').textContent=err.message;}finally{$('run').disabled=false;}});
api('/api/datasets').then(d=>{$('dataset-description').textContent=d[0].description;}).catch(e=>{$('status').textContent=e.message;});
