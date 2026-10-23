import {validateSettings,parseSettingsFile,settingsDocument,resultsCsv} from './cnn-settings.js';
const $=id=>document.getElementById(id),embedded=window.parent!==window;
if(embedded)document.documentElement.classList.add('embedded');
let latest=null,info=null,inspection=null,busy=false,serial=0,selected=0,inspectTicket=0;
const pending=new Map(),inspectionCache=new Map();
window.addEventListener('message',event=>{
  if(event.source!==window.parent||event.origin!==location.origin||event.data?.type!=='prabha-cnn-response')return;
  const job=pending.get(event.data.id);if(!job)return;
  clearTimeout(job.timer);pending.delete(event.data.id);
  event.data.error?job.reject(new Error(event.data.error)):job.resolve(event.data.result);
});
function bridge(message){return new Promise((resolve,reject)=>{
  const id=++serial,timer=setTimeout(()=>{pending.delete(id);reject(new Error('CNN request timed out. Try a smaller batch.'));},125000);
  pending.set(id,{resolve,reject,timer});window.parent.postMessage({...message,id},location.origin);
});}
async function execute(payload){return embedded?bridge({type:'prabha-cnn-request',payload}):(await import('./engine.js')).execute(payload);}
async function save(name,text,type='application/json'){
  return embedded?bridge({type:'prabha-cnn-save',name,text,mime:type}):(await import('./platform.js')).saveText(name,text,type);
}
function error(message=''){$('error').textContent=message;$('error').hidden=!message;}
function bits(id){return $(id).value==='off'?null:Number($(id).value);}
function readSettings(){
  let pixels,model;
  try{pixels=JSON.parse($('pixels').value);}catch{throw new Error('Pixel JSON must contain eight rows of eight numbers.');}
  try{model=JSON.parse($('weights').value);}catch{throw new Error('Weights JSON is invalid. Check commas and brackets.');}
  const mode=$('input-mode').value;
  return validateSettings({input:{mode,count:mode==='custom'?1:Number($('count').value),start:mode==='custom'?0:Number($('start').value),pixels,
    label:$('label').value.trim()===''?null:Number($('label').value)},model,
    converters:{dac_bits:bits('dac'),adc_bits:bits('adc'),adc_full_scale:Number($('adc-range').value),dac_rounding:$('rounding').value}});
}
function draw(canvas,pixels){
  canvas.width=8;canvas.height=8;const ctx=canvas.getContext('2d'),image=ctx.createImageData(8,8);
  pixels.flat().forEach((v,i)=>{const gray=Math.round(v/16*255);image.data.set([gray,gray,gray,255],i*4);});ctx.putImageData(image,0,0);
}
function pixelText(pixels){return '[\n'+pixels.map(row=>'  '+JSON.stringify(row)).join(',\n')+'\n]';}
function mode(){const custom=$('input-mode').value==='custom';$('heldout-controls').hidden=custom;$('custom-controls').hidden=!custom;}
function applySettings(settings){const s=validateSettings(settings),i=s.input,c=s.converters;
  $('input-mode').value=i.mode;$('count').value=String(i.count);$('start').value=String(i.start);
  $('pixels').value=pixelText(i.pixels);$('label').value=i.label===null?'':String(i.label);
  $('weights').value=JSON.stringify(s.model,null,2);$('dac').value=c.dac_bits===null?'off':String(c.dac_bits);
  $('adc').value=c.adc_bits===null?'off':String(c.adc_bits);$('adc-range').value=String(c.adc_full_scale);$('rounding').value=c.dac_rounding;
  mode();draw($('input-digit'),i.pixels);
}
function invalidate(){latest=null;inspection=null;inspectionCache.clear();inspectTicket++;
  for(const id of ['numpy-accuracy','prabha-accuracy','disagreements','images','numpy-time','prabha-time','numpy-prediction','prabha-prediction'])$(id).textContent='-';
  $('rows').replaceChildren();$('layer-values').textContent='Run inference to inspect a layer.';$('layer-stats').textContent='';
  for(const id of ['digit','layer-numpy','layer-prabha','layer-difference']){const canvas=$(id);canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);}
  $('errors').textContent='';$('operations').textContent='';$('truth').textContent='No current inference result.';$('sample-error').textContent='';
  $('numpy-bar').style.width='0';$('prabha-bar').style.width='0';
  $('slowdown').textContent='Run the comparison to measure these settings.';
  for(const id of ['download','csv','export-layer'])$(id).disabled=true;
  $('status').textContent='Settings changed. Run again for fresh results.';$('weight-status').textContent='Editable settings';
}
function changed(){if(busy)return;invalidate();mode();error();try{draw($('input-digit'),readSettings().input.pixels);}catch{/* Keep incomplete edits visible. */}}
async function task(fn){if(busy)return;busy=true;$('controls').disabled=true;error();
  try{await fn();}catch(e){error(e.message);$('status').textContent='Action failed. Correct the settings and try again.';}
  finally{busy=false;$('controls').disabled=false;}}
function profile(result){
  $('weight-status').textContent=result.weights_match_checkpoint?'Trained checkpoint weights':'Edited weights';
  const c=result.settings.converters;$('dac-status').textContent=c.dac_bits===null?'Input DAC off':c.dac_bits+'-bit input DAC';
  $('adc-status').textContent=c.adc_bits===null?'Output ADC off':c.adc_bits+'-bit MAC output ADC';
}
function plane(values,channel){if(!Array.isArray(values[0]))return [values];return Array.isArray(values[0][0])?values[channel]:values;}
function heat(canvas,matrix,low,high){const h=matrix.length,w=matrix[0].length;canvas.width=w;canvas.height=h;canvas.style.aspectRatio=w+'/'+h;
  const ctx=canvas.getContext('2d'),image=ctx.createImageData(w,h),span=high-low||1;
  matrix.flat().forEach((v,i)=>{const t=Math.max(0,Math.min(1,(v-low)/span));image.data.set([Math.round(35+200*t),Math.round(53+165*t),Math.round(65+105*t),255],i*4);});ctx.putImageData(image,0,0);
}
function showLayer(){if(!inspection)return;
  const layer=inspection.layers.find(x=>x.name===$('layer').value)||inspection.layers[0];
  const channels=layer.shape.length===3?layer.shape[0]:1,old=Number($('channel').value)||0;
  $('channel').replaceChildren();for(let i=0;i<channels;i++){const option=document.createElement('option');option.value=String(i);option.textContent='Channel '+i;$('channel').append(option);}
  $('channel').value=String(Math.min(old,channels-1));const channel=Number($('channel').value);
  const a=plane(layer.numpy,channel),b=plane(layer.prabha,channel),d=a.map((row,r)=>row.map((v,c)=>b[r][c]-v));
  const low=Math.min(layer.numpy_min,layer.prabha_min),high=Math.max(layer.numpy_max,layer.prabha_max);
  heat($('layer-numpy'),a,low,high);heat($('layer-prabha'),b,low,high);heat($('layer-difference'),d,-layer.maximum_error,layer.maximum_error);
  $('layer-stats').textContent='Shape ['+layer.shape+'] | RMS error '+layer.rms_error.toExponential(5)+' | maximum '+layer.maximum_error.toExponential(5);
  $('layer-values').textContent=JSON.stringify({shape:layer.shape,numpy:layer.numpy,prabha:layer.prabha},null,2);
  $('export-layer').disabled=false;
}
async function sample(index){if(!latest)return;const snapshot=latest,row=snapshot.rows[index];selected=index;
  inspection=null;$('export-layer').disabled=true;$('layer-stats').textContent='Computing the selected image...';$('layer-values').textContent='Computing the selected image...';
  for(const id of ['layer-numpy','layer-prabha','layer-difference']){const canvas=$(id);canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);}
  draw($('digit'),Array.from({length:8},(_,i)=>row.pixels.slice(8*i,8*i+8)));
  $('truth').textContent=(row.label===null?'True digit: unlabelled':'True digit: '+row.label)+' | '+(row.test_position===null?'Custom image':'Test image '+(row.test_position+1));
  $('numpy-prediction').textContent=String(row.numpy_prediction);$('prabha-prediction').textContent=String(row.prabha_prediction);
  $('sample-error').textContent='Maximum logit difference: '+row.maximum_logit_error.toExponential(4);
  [...$('rows').children].forEach((tr,i)=>tr.classList.toggle('selected',i===index));
  const ticket=++inspectTicket;
  try{const value=inspectionCache.get(index)||await execute({action:'cnn_inspect',settings:snapshot.settings,index});
    if(latest!==snapshot||ticket!==inspectTicket)return;inspectionCache.set(index,value);inspection=value;showLayer();
  }catch(e){if(ticket===inspectTicket)error(e.message);}
}
async function render(r){latest=r;inspectionCache.clear();inspectionCache.set(0,r.inspection);profile(r);
  $('numpy-accuracy').textContent=r.numpy_accuracy===null?'Unlabelled':(100*r.numpy_accuracy).toFixed(2)+'%';
  $('prabha-accuracy').textContent=r.prabha_accuracy===null?'Unlabelled':(100*r.prabha_accuracy).toFixed(2)+'%';
  $('disagreements').textContent=String(r.prediction_disagreements);$('images').textContent=String(r.count);
  $('numpy-time').textContent=(1000*r.numpy_seconds).toFixed(3)+' ms';$('prabha-time').textContent=r.prabha_seconds.toFixed(3)+' s';
  const max=Math.max(r.numpy_seconds,r.prabha_seconds,1e-12);$('numpy-bar').style.width=100*r.numpy_seconds/max+'%';$('prabha-bar').style.width=100*r.prabha_seconds/max+'%';
  $('slowdown').textContent='Prabha took '+r.slowdown_vs_numpy.toLocaleString(undefined,{maximumFractionDigits:0})+' times the NumPy runtime for the same '+r.count+' image(s).';
  $('rows').replaceChildren();r.rows.forEach((row,i)=>{const tr=document.createElement('tr');
    for(const value of [row.test_position===null?'Custom':row.test_position+1,row.label??'-',row.numpy_prediction,row.prabha_prediction,row.correct===null?'Unlabelled':row.correct?'Correct':'Incorrect']){
      const td=document.createElement('td');td.textContent=String(value);tr.append(td);}
    if(row.correct===false)tr.classList.add('bad');tr.addEventListener('click',()=>{if(!busy)sample(i);});$('rows').append(tr);});
  $('errors').textContent='Logit error: RMS '+r.rms_logit_error.toExponential(4)+'; maximum '+r.max_logit_error.toExponential(4);
  $('operations').textContent=r.mac_calls.toLocaleString()+' MAC calls | '+r.device_passes.toLocaleString()+' device passes | '+r.waveform_samples.toLocaleString()+' waveform samples';
  $('download').disabled=false;$('csv').disabled=false;await sample(0);
}
for(const id of ['dac','adc']){for(const value of ['off',...Array.from({length:24},(_,i)=>String(i+1))]){
  const option=document.createElement('option');option.value=value;option.textContent=value==='off'?'Off':value+' bits';$(id).append(option);}}
const editors=new Set(['input-mode','count','start','pixels','label','weights','dac','adc','adc-range','rounding']);
$('controls').addEventListener('input',event=>{if(editors.has(event.target.id))changed();});
$('input-mode').addEventListener('change',changed);
$('run').addEventListener('click',()=>task(async()=>{
  const settings=readSettings();invalidate();$('status').textContent='Computing fresh NumPy and Prabha waveform inference...';
  const r=await execute({action:'cnn',settings});await render(r);
  $('status').textContent=r.labelled_images?'Complete: NumPy '+r.numpy_correct+'/'+r.labelled_images+', Prabha '+r.prabha_correct+'/'+r.labelled_images+' correct.':'Complete: unlabelled custom image; predictions computed without an accuracy claim.';
}));
$('validate').addEventListener('click',()=>task(async()=>{const accepted=await execute({action:'cnn_validate',settings:readSettings()});profile(accepted);$('status').textContent='Settings valid. Run inference to compute predictions.';}));
$('reset').addEventListener('click',()=>{if(busy)return;applySettings(info.default_settings);invalidate();$('status').textContent='Checkpoint and reference converter settings restored. Run for fresh results.';});
$('restore-weights').addEventListener('click',()=>{if(busy)return;$('weights').value=JSON.stringify(info.default_settings.model,null,2);changed();});
$('load-digit').addEventListener('click',()=>task(async()=>{const sample=await execute({action:'cnn_info',sample_index:Number($('digit-index').value)});
  $('pixels').value=pixelText(sample.sample.pixels);$('label').value=String(sample.sample.label);$('input-mode').value='custom';invalidate();mode();draw($('input-digit'),sample.sample.pixels);$('status').textContent='Digit loaded as editable custom input. Run for fresh predictions.';}));
$('input-digit').addEventListener('pointerdown',event=>{if(busy)return;try{const pixels=JSON.parse($('pixels').value),rect=$('input-digit').getBoundingClientRect();
  const x=Math.max(0,Math.min(7,Math.floor((event.clientX-rect.left)/rect.width*8))),y=Math.max(0,Math.min(7,Math.floor((event.clientY-rect.top)/rect.height*8)));
  const brush=Number($('brush').value);if(!Number.isFinite(brush)||brush<0||brush>16)throw new Error('Brush must be between 0 and 16.');
  pixels[y][x]=brush;$('pixels').value=pixelText(pixels);$('input-mode').value='custom';changed();
}catch(e){error(e.message);}});
$('import').addEventListener('click',()=>{if(!busy)$('import-file').click();});
$('import-file').addEventListener('change',()=>task(async()=>{const file=$('import-file').files?.[0];if(!file)return;
  try{if(file.size>1_000_000)throw new Error('CNN settings imports must be smaller than 1 MB.');
    const settings=parseSettingsFile(await file.text()),accepted=await execute({action:'cnn_validate',settings});
    applySettings(accepted.settings);invalidate();profile(accepted);$('status').textContent='Settings imported. Stored results were not imported; run fresh inference.';
  }finally{$('import-file').value='';}
}));
$('export-settings').addEventListener('click',()=>task(async()=>{const accepted=await execute({action:'cnn_validate',settings:readSettings()});
  await save('prabha-cnn-settings.json',JSON.stringify(settingsDocument(accepted.settings),null,2));$('status').textContent='CNN settings exported.';
}));
$('download').addEventListener('click',()=>task(async()=>{if(!latest)return;await save('prabha-cnn-run.json',JSON.stringify({schema:'prabha.cnn-run.v2',created_at:new Date().toISOString(),settings:latest.settings,result:latest},null,2));$('status').textContent='Run JSON exported with the exact settings used.';}));
$('csv').addEventListener('click',()=>task(async()=>{if(latest)await save('prabha-cnn-results.csv',resultsCsv(latest),'text/csv');}));
$('export-layer').addEventListener('click',()=>task(async()=>{if(inspection&&latest)await save('prabha-cnn-layer.json',JSON.stringify({schema:'prabha.cnn-layer.v1',settings:latest.settings,row:selected,inspection},null,2));}));
$('layer').addEventListener('change',()=>{$('channel').value='0';showLayer();});$('channel').addEventListener('change',showLayer);
try{info=await execute({action:'cnn_info'});applySettings(info.default_settings);
  $('architecture').textContent=info.architecture+' | 410 editable parameters | checkpoint epoch '+info.selected_epoch;
  $('status').textContent='Ready. Recorded checkpoint result: 354/360 (98.33%). Run for fresh results; edited settings may change accuracy.';
  $('controls').disabled=false;
}catch(e){error(e.message);$('status').textContent='CNN assets or engine unavailable.';}
if(embedded&&typeof ResizeObserver!=='undefined')new ResizeObserver(()=>window.parent.postMessage({type:'prabha-cnn-height',height:document.documentElement.scrollHeight},location.origin)).observe(document.body);
