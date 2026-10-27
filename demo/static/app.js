'use strict';
const $=id=>document.getElementById(id);
let currentRun=null,currentProject=null,conversationId=null,busy=false,projectEpoch=0;
let projectList=[];
const fmt=n=>Number(n).toLocaleString('de-DE',{maximumFractionDigits:2});
function el(tag,text,parent){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(parent)parent.append(e);return e;}
async function api(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const data=await r.json();if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:'Ungültige Anfrage. Bitte verwende die angebotenen Optionen.');return data;}
function projectPath(suffix='',projectId=currentProject){return `/api/projects/${encodeURIComponent(projectId)}${suffix}`;}
function setBusy(value){
 busy=value;
 ['project','run-history','run','agent-send','decision-save'].forEach(id=>$(id).disabled=value||!currentProject);
 document.querySelectorAll('.suggestion,.approve-decision').forEach(b=>b.disabled=value||!currentProject);
}
function active(projectId,epoch){return currentProject===projectId&&projectEpoch===epoch;}
function clearProjectView(){
 currentRun=null;conversationId=null;$('results').hidden=true;$('comparison').hidden=true;
 for(const id of ['metrics','coefficients','timeseries','residuals','comparison-rows','response-curves','warnings','dataset-preview','conversation','decisions','execution-history'])$(id).replaceChildren();
 for(const id of ['interpretation','formula','truth','diagnostics','identity','comparison-summary','agent-answer','tool-output','project-metadata'])$(id).textContent='';
 $('report-export').removeAttribute('href');$('tool-details').hidden=true;
 $('run-history').replaceChildren(new Option('Noch kein Ergebnis ausgewählt',''));
 $('agent-input').value='';$('decision-text').value='';$('decision-kind').value='decision';
 $('agent-status').textContent='Bereit. Keine Shell, freien Datenabrufe oder selbständigen Modelländerungen.';
 $('decision-status').textContent='Keine automatische Ausführung.';
 $('history-status').textContent='Ein gespeichertes Ergebnis wird vor dem Öffnen erneut geprüft.';
}
const messageKinds={user_statement:'Aussage / Notiz',acknowledgement:'Regelbasierte Bestätigung',tool_result:'Echte Tool-Ausgabe',error:'Fehler / nicht ausgeführt',context:'Gespeicherter Projektkontext'};
const roles={user:'Nutzer',assistant:'Assistent',system:'System'};
function renderWorkspace(state){
 conversationId=state.conversation_id;
 const project=state.project,runs=state.runs||[],messages=state.messages||[],decisions=state.decisions||[],executions=state.executions||[];
 $('workspace-context').textContent=`${project.name} · ${runs.length} zuletzt gespeicherte Ergebnisse · ${decisions.filter(d=>d.status==='proposed').length} offene Vorschläge. Beide Projekte nutzen denselben synthetischen Monatsdatensatz.`;
 $('project-metadata').textContent=JSON.stringify({project_id:project.id,dataset_id:project.dataset_id,frequency:project.frequency,target:project.target,default_model:project.default_model,provenance:project.provenance,conversation_id:conversationId},null,2);
 $('conversation-limit').textContent='Ansicht: letzte 40 Nachrichten und letzte 20 Ergebnisse, Entscheidungen und Tool-Ausführungen. Ältere Einträge bleiben gespeichert.';
 const selected=currentRun?.id||'';
 $('run-history').replaceChildren(new Option('Gespeichertes Ergebnis öffnen …',''));
 for(const run of runs)$('run-history').add(new Option(`${run.created_at} · ${run.model} · ${run.id.slice(0,8)}`,run.id));
 if(selected&&!runs.some(r=>r.id===selected))$('run-history').add(new Option(`Ausgewähltes älteres Ergebnis · ${selected.slice(0,8)}`,selected));
 $('run-history').value=selected;
 $('conversation').replaceChildren();
 if(!messages.length)el('li','Noch keine Nachrichten in diesem Projekt.',$('conversation')).className='empty-state';
 for(const message of messages){
  const item=el('li',undefined,$('conversation'));item.className='message';item.dataset.kind=message.kind;item.dataset.role=message.role;
  el('small',`${roles[message.role]||message.role} · ${messageKinds[message.kind]||message.kind} · ${message.created_at}`,item);
  el('p',message.text,item);
  if(message.execution_id)el('small',`Ausführungsreferenz: ${message.execution_id}`,item);
 }
 $('conversation').scrollTop=$('conversation').scrollHeight;
 $('decisions').replaceChildren();
 if(!decisions.length)el('li','Noch keine Entscheidungsvorschläge.',$('decisions')).className='empty-state';
 for(const decision of decisions){
  const item=el('li',undefined,$('decisions'));item.dataset.status=decision.status;item.dataset.decisionId=decision.id;
  el('small',`${decision.kind==='development_workorder'?'Entwicklungsauftrag':'Entscheidung'} · ${decision.status==='approved'?'ausdrücklich freigegeben':'Vorschlag, nicht freigegeben'}`,item);
  el('p',decision.text,item);
  if(decision.status==='proposed'){
   const button=el('button','Ausdrücklich freigeben',item);button.type='button';button.className='approve-decision';button.disabled=busy;
   const projectId=currentProject,epoch=projectEpoch;
   button.addEventListener('click',()=>approveDecision(projectId,epoch,decision.id));
  }else el('small',`Freigabe: ${decision.approved_at||'gespeicherte menschliche Aktion'} · Keine Ausführung.`,item);
 }
 $('execution-history').replaceChildren();
 if(!executions.length)el('li','Noch keine Tool-Ausführungen.',$('execution-history'));
 for(const execution of executions)el('li',`${execution.tool} · ${execution.status} · ${execution.started_at||execution.created_at||''}${execution.error_code?' · '+execution.error_code:''}`,$('execution-history'));
}
async function refreshWorkspace(projectId=currentProject,epoch=projectEpoch){
 const state=await api(projectPath('/workspace',projectId));
 if(active(projectId,epoch))renderWorkspace(state);
 return state;
}
async function showFailure(statusId,error,projectId,epoch){
 if(!active(projectId,epoch))return;
 $(statusId).textContent=error.message;
 try{await refreshWorkspace(projectId,epoch);}
 catch{if(active(projectId,epoch))$('workspace-context').textContent='Projektkontext konnte nicht erneut geladen werden. Es wird kein neuer Erfolg behauptet.';}
}
async function loadRun(runId,projectId=currentProject,epoch=projectEpoch){
 const value=await api(projectPath(`/runs/${encodeURIComponent(runId)}`,projectId));
 if(active(projectId,epoch)){
  render(value);$('history-status').textContent=`Gespeichertes Ergebnis ${runId.slice(0,8)} geöffnet · Artefakte erneut validiert.`;
  $('run-history').value=runId;
 }
}
async function selectProject(projectId){
 if(busy)return;
 currentProject=projectId;const epoch=++projectEpoch;clearProjectView();setBusy(true);
 const url=new URL(window.location.href);url.searchParams.set('project',projectId);window.history.replaceState(null,'',url);
 $('workspace-context').textContent='Projektkontext wird geladen …';$('status').textContent='Projekt wird geöffnet …';
 const project=projectList.find(p=>p.id===projectId);if(project)$('model').value=project.default_model;
 try{
  const state=await refreshWorkspace(projectId,epoch);
  if(active(projectId,epoch)&&state.runs?.length)await loadRun(state.runs[0].id,projectId,epoch);
  if(active(projectId,epoch))$('status').textContent='Projekt geöffnet · SYNTHETIC / NOT EMPIRICAL';
 }catch(error){if(active(projectId,epoch)){$('status').textContent=error.message;$('workspace-context').textContent='Projekt konnte nicht vollständig geöffnet werden.';}}
 finally{if(active(projectId,epoch))setBusy(false);}
}
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
 $('model').value=data.model;currentRun=data;$('comparison').hidden=true;$('report-export').href=projectPath(`/runs/${data.id}/report`);
 $('results').hidden=false;const r=data.result;$('metrics').replaceChildren();
 [['Holdout RMSE',r.metrics.test.rmse,'12 Monate · count-equivalent'],['Media-Koeffizient',r.coefficients.media.estimate,'Geschätzt · feste Oracle-Transformation'],['Media-Beitrag',r.contribution.total.estimate,'Geschätzte Summe · Holdout 2023']].forEach(([title,value,note])=>{const c=el('div',undefined,$('metrics'));c.className='card';el('small',title,c);el('strong',fmt(value),c);el('span',note,c);});
 $('interpretation').textContent=data.interpretation;$('formula').textContent=data.formula;$('coefficients').replaceChildren();
 Object.entries(r.coefficients).filter(([,v])=>v!==null).forEach(([name,v])=>{const tr=el('tr',undefined,$('coefficients'));[name,v.estimate,v.standard_error,v.lower,v.upper].forEach(x=>el('td',typeof x==='number'?fmt(x):x,tr));});
 $('truth').textContent=`Separater Ground-Truth-Vergleich: β = ${fmt(data.ground_truth.media_coefficient)}. Nicht als Estimator-Eingabe verwendet.`;
 $('warnings').replaceChildren();data.warnings.forEach(w=>el('li',w,$('warnings')));$('identity').textContent=JSON.stringify({seed:data.dataset.seed,hashes:data.hashes,software:data.software},null,2);
 chart($('timeseries'),data.series.periods,[{name:'Synthetisches Outcome',values:data.series.outcome,color:'#255f93'},{name:'Geschätzte Vorhersage',values:data.series.prediction,color:'#d88537'},{name:'Geschätzte Baseline',values:data.series.estimated_baseline,color:'#879a91'},{name:'Geschätzter Media-Beitrag',values:data.series.estimated_media,color:'#178074'},{name:'Ground Truth: Referenz',values:data.series.synthetic_reference,color:'#6973b7'},{name:'Ground Truth: Media',values:data.series.simulated_media,color:'#b65c91'}]);
 chart($('residuals'),data.series.periods,[{name:'Residuen (Train und Holdout)',values:data.series.residual,color:'#255f93'}]);
 $('diagnostics').textContent=`Train n=${r.metrics.train.n}, Holdout n=${r.metrics.test.n}; Rang ${r.diagnostics.rank}/${r.diagnostics.design_columns}; skalierte Konditionszahl ${fmt(r.diagnostics.scaled_condition_number)}. Flags: ${r.diagnostics.flags.join(', ')||'keine nach der technischen Regel'}.`;
}
function renderComparison(data){
 $('comparison').hidden=false;$('comparison-rows').replaceChildren();
 for(const [name,v]of Object.entries(data.variants)){
  const r=v.result,b=r.coefficients.media,tr=el('tr',undefined,$('comparison-rows'));
  [name,fmt(r.metrics.test.rmse),fmt(r.metrics.test.mae),`${fmt(b.estimate)} [${fmt(b.lower)}; ${fmt(b.upper)}]`,fmt(v.evaluation.media_coefficient_error),fmt(r.contribution.total.estimate)].forEach(x=>el('td',x,tr));
 }
 const c=data.comparison;
 $('comparison-summary').textContent=`Ohne minus mit Quartalsende: Holdout-RMSE Δ=${fmt(c.test_rmse_delta_right_minus_left)}; Media-Beitrag Δ=${fmt(c.contribution_delta_right_minus_left)}. Flags: ${c.flags.join(', ')||'keine nach der technischen Regel'}. Relative Kurvenänderung ${fmt(c.relative_curve_change)} bei technischer Grenze ${fmt(c.stability_rule.relative_curve_change_limit)}; keine kalibrierte wissenschaftliche Nachweisgrenze.`;
 chart($('response-curves'),c.response_grid.spend.map(fmt),[{name:'Geschätzt: mit Quartalsende',values:data.variants['with-quarter'].result.response_curve.estimate,color:'#255f93'},{name:'Geschätzt: ohne Quartalsende',values:data.variants['without-quarter'].result.response_curve.estimate,color:'#d88537'},{name:'Ground Truth: Response',values:data.ground_truth.response,color:'#178074'}],99);
}
$('compare').addEventListener('click',()=>{if(currentRun)renderComparison(currentRun);});
$('run-form').addEventListener('submit',async e=>{
 e.preventDefault();if(busy||!currentProject)return;const projectId=currentProject,epoch=projectEpoch;
 currentRun=null;setBusy(true);$('results').hidden=true;$('status').textContent='Analyse läuft: generieren, isoliert schätzen, Verträge und Hashes prüfen …';
 try{const data=await api(projectPath('/runs',projectId),{dataset:$('dataset').value,model:$('model').value});if(active(projectId,epoch))render(data);await refreshWorkspace(projectId,epoch);if(active(projectId,epoch))$('status').textContent='Analyse abgeschlossen · Ergebnis validiert und gespeichert · SYNTHETIC / NOT EMPIRICAL';}
 catch(err){await showFailure('status',err,projectId,epoch);}
 finally{if(active(projectId,epoch))setBusy(false);}
});
$('project').addEventListener('change',()=>selectProject($('project').value));
$('run-history').addEventListener('change',async()=>{
 if(busy||!$('run-history').value)return;const projectId=currentProject,epoch=projectEpoch;setBusy(true);
 try{await loadRun($('run-history').value,projectId,epoch);}catch(error){if(active(projectId,epoch)){currentRun=null;$('results').hidden=true;$('history-status').textContent=error.message;}}
 finally{if(active(projectId,epoch))setBusy(false);}
});

async function askAgent(message){
 if(busy||!currentProject||!conversationId)return;const projectId=currentProject,epoch=projectEpoch;setBusy(true);
 $('agent-status').textContent='Tool-Anfrage läuft …';$('agent-answer').textContent='';$('dataset-preview').replaceChildren();$('tool-details').hidden=true;
 try{
  const answer=await api(projectPath('/messages',projectId),{message,conversation_id:conversationId,run_id:currentRun?.id||null});
  if(!active(projectId,epoch))return;
  $('agent-answer').textContent=answer.text;
  $('agent-status').textContent=answer.executed?`Tool ausgeführt: ${answer.tool}`:answer.status==='note_saved'?'Freie Anfrage nicht unterstützt · als Notiz gespeichert; kein Tool ausgeführt.':`Kein Tool ausgeführt: ${answer.tool||'keines'}`;
  if(answer.executed){$('tool-details').hidden=false;$('tool-output').textContent=JSON.stringify(answer.output,null,2);}
  if(answer.executed && answer.tool==='run_demo_analysis'){
   render(answer.output);$('status').textContent='Analyse abgeschlossen · über run_demo_analysis · SYNTHETIC / NOT EMPIRICAL';
  }
  if(answer.executed && answer.tool==='compare_runs' && currentRun)renderComparison(currentRun);
  if(answer.executed && answer.tool==='describe_dataset'){
   const table=el('table',undefined,$('dataset-preview')),head=el('thead',undefined,table),tr=el('tr',undefined,head);
   const names=['period','synthetic_media','semi_synthetic_outcome'];names.forEach(n=>el('th',n,tr));
   const body=el('tbody',undefined,table);answer.output.preview.forEach(row=>{const r=el('tr',undefined,body);names.forEach(n=>el('td',n==='period'?row[n]:fmt(row[n]),r));});
  }
  await refreshWorkspace(projectId,epoch);
 }catch(err){await showFailure('agent-status',err,projectId,epoch);}
 finally{if(active(projectId,epoch))setBusy(false);}
}
$('agent-form').addEventListener('submit',e=>{e.preventDefault();askAgent($('agent-input').value);});
document.querySelectorAll('.suggestion').forEach(b=>b.addEventListener('click',()=>{$('agent-input').value=b.textContent;askAgent(b.textContent);}));

async function approveDecision(projectId,epoch,decisionId){
 if(busy||!active(projectId,epoch))return;setBusy(true);
 try{await api(projectPath(`/decisions/${encodeURIComponent(decisionId)}/approve`,projectId),{});await refreshWorkspace(projectId,epoch);if(active(projectId,epoch))$('decision-status').textContent='Menschliche Freigabe gespeichert. Kein Auftrag wurde ausgeführt.';}
 catch(error){if(active(projectId,epoch))$('decision-status').textContent=error.message;}
 finally{if(active(projectId,epoch))setBusy(false);}
}
$('decision-form').addEventListener('submit',async event=>{
 event.preventDefault();if(busy||!currentProject)return;const projectId=currentProject,epoch=projectEpoch;setBusy(true);
 try{await api(projectPath('/decisions',projectId),{text:$('decision-text').value,kind:$('decision-kind').value});if(active(projectId,epoch))$('decision-text').value='';await refreshWorkspace(projectId,epoch);if(active(projectId,epoch))$('decision-status').textContent='Vorschlag gespeichert · nicht freigegeben und nicht ausgeführt.';}
 catch(error){if(active(projectId,epoch))$('decision-status').textContent=error.message;}
 finally{if(active(projectId,epoch))setBusy(false);}
});
async function initialize(){
 setBusy(true);
 try{
  const [projects,datasets]=await Promise.all([api('/api/projects'),api('/api/datasets')]);
  projectList=projects;
  $('project').replaceChildren(...projects.map(p=>new Option(p.name,p.id)));
  if(!projects.length)throw new Error('Kein Projekt verfügbar.');
  const requested=new URL(window.location.href).searchParams.get('project');
  const selected=projects.find(p=>p.id===requested)||projects[0];$('project').value=selected.id;
  busy=false;await selectProject(selected.id);
  $('dataset-description').textContent=datasets[0].description;
 }catch(error){$('status').textContent=error.message;$('workspace-context').textContent='Arbeitsbereich nicht verfügbar.';}
}
initialize();
