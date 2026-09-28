let py;
async function boot(){
 importScripts('https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js');
 py=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.29.0/full/'});
 postMessage({status:'Loading NumPy and the Prabha models…'});
 await py.loadPackage(['numpy','jsonschema']);
 const r=await fetch(new URL('./prabha-python.zip',self.location.href));if(!r.ok)throw new Error('Prabha model bundle is unavailable.');
 py.unpackArchive(await r.arrayBuffer(),'zip',{extractDir:'/prabha'});
 py.runPython("import sys, json\nsys.path.insert(0, '/prabha/core-py')\nfrom prabha.product import dispatch");postMessage({ready:true});
}
const ready=boot().catch(e=>{postMessage({initError:e.message});throw e;});
onmessage=async({data})=>{try{await ready;py.globals.set('_request',JSON.stringify(data.payload));const result=JSON.parse(py.runPython('json.dumps(dispatch(json.loads(_request)), allow_nan=False)'));postMessage({id:data.id,result});}catch(e){postMessage({id:data.id,error:e.message});}};
