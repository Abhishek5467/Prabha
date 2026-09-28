const nativeFetch=globalThis.__PRABHA_FETCH||globalThis.fetch.bind(globalThis);
let worker,ready,id=0,mode='',onStatus=()=>{};
const pending=new Map();
export const engineStatus=callback=>{onStatus=callback;if(mode)callback(mode);};
async function initialize(){
 if(globalThis.__TAURI__?.core?.invoke){mode='Desktop Python';onStatus(mode);return;}
 try{const r=await nativeFetch('/api/health',{signal:AbortSignal.timeout(1500)});if(r.ok&&(await r.json()).engine==='native-python'){mode='Python API';onStatus(mode);return;}}catch{}
 onStatus('Loading Python in your browser…');
 worker=new Worker(new URL('./python-worker.js',import.meta.url));
 await new Promise((resolve,reject)=>{
  const timer=setTimeout(()=>reject(new Error('Python download timed out. Check your connection and reload.')),120000);
  worker.onmessage=({data})=>{if(data.status){onStatus(data.status);return;}if(data.ready){clearTimeout(timer);mode='Browser Python';onStatus(mode);resolve();return;}if(data.initError){clearTimeout(timer);reject(new Error(data.initError));return;}const p=pending.get(data.id);if(p){pending.delete(data.id);data.error?p.reject(new Error(data.error)):p.resolve(data.result);}};
  worker.onerror=e=>{clearTimeout(timer);reject(new Error(e.message||'Python worker failed.'));};
 });
}
export async function execute(payload){
 if(!ready)ready=initialize().catch(e=>{ready=null;worker?.terminate();throw e;});await ready;let r;
 if(mode==='Desktop Python')r=await globalThis.__TAURI__.core.invoke('simulate',{payload});
 else if(mode==='Python API')r=await(await nativeFetch('/api/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})).json();
 else r=await new Promise((resolve,reject)=>{const next=++id;pending.set(next,{resolve,reject});worker.postMessage({id:next,payload});});
 if(!r.ok)throw new Error(r.error||'Simulation failed.');return r.result;
}
