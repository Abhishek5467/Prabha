"""Build the browser's source bundle, evidence catalogue, designer and docs."""
from pathlib import Path
import json, shutil, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'frontend/studio/public'
PUBLIC.mkdir(parents=True, exist_ok=True)
version = json.loads((ROOT/'frontend/studio/package.json').read_text())['version']
(PUBLIC/'build-info.json').write_text(json.dumps({'version': version}, indent=2)+'\n', encoding='utf-8')
evidence = PUBLIC / 'evidence'
evidence.mkdir(exist_ok=True)
catalog = []
for f in sorted((ROOT/'core-py').glob('*')):
    if f.suffix not in {'.png', '.csv'}: continue
    shutil.copy2(f, evidence/f.name)
    if f.suffix == '.png':
        group = ('ANN' if f.name.startswith('ann_') else 'Perceptron' if f.name.startswith('complete_') else 'Converters' if f.name.startswith('dac_') else 'Photodetector' if f.name.startswith('photodetector_') else 'Optical link')
        catalog.append({'file': f.name, 'title': f.stem.replace('_',' ').capitalize(), 'group': group})
(evidence/'catalog.json').write_text(json.dumps(catalog, indent=2), encoding='utf-8')
with zipfile.ZipFile(PUBLIC/'prabha-python.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths = list((ROOT/'core-py/prabha').rglob('*.py')) + list((ROOT/'spec').rglob('*.json')) + list((ROOT/'blocks-lib').glob('*.json')) + [ROOT/'peman.prabha']
    paths += [ROOT/'results/cnn_digits/trained_cnn.npz', ROOT/'results/cnn_digits/training_metadata.json', ROOT/'validation/datasets/digits_8x8_split.npz']
    for f in sorted(paths): z.write(f, f.relative_to(ROOT))
shim = '''
<script type="module">
const originalFetch=window.fetch.bind(window);window.__PRABHA_FETCH=originalFetch;
const engine=import('./engine.js');
import('./platform.js').then(module=>module.installNavigation());
window.prabhaDownload=async function(link){
 try{
  const platform=await import('./platform.js');
  if(!platform.isDesktop()){link.click();return;}
  const response=await originalFetch(link.href);
  await platform.saveBlob(link.download,await response.blob());
 }catch(error){alert(error.message||String(error));}
};
window.fetch=async function(input,options={}){
 const path=typeof input==='string'?input:input.url;
 if(path==='/api/blocks'||path==='/api/run'||path==='/api/execute'){
  try {const {execute}=await engine;
   const payload=path==='/api/blocks'?{action:'blocks'}:path==='/api/run'?{...JSON.parse(options.body),action:'graph'}:JSON.parse(options.body);
   const result=await execute(payload);
   return new Response(JSON.stringify(path==='/api/blocks'?result:path==='/api/run'?{ok:true,...result}:{ok:true,result}),{headers:{'Content-Type':'application/json'}});
  } catch(e) {return new Response(JSON.stringify({ok:false,error:e.message,violations:e.violations||[]}),{status:422,headers:{'Content-Type':'application/json'}});}
 }
 return originalFetch(input,options);
};
</script>
'''
# A module is deferred; use a blocking shim that awaits its own lazy import instead.
shim=shim.replace('type="module"','').replace("const engine=import('./engine.js');", "const engine=import('./engine.js');")
html=(ROOT/'frontend/web/index.html').read_text(encoding='utf-8')
html=html.replace('a.click();','window.prabhaDownload(a);')
html=html.replace('</head>',shim+'</head>').replace('<body>','<body><a href="./" style="position:fixed;right:12px;bottom:12px;z-index:10000;background:#173b42;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none">← Prabha Studio</a>')
(PUBLIC/'designer.html').write_text(html, encoding='utf-8')
subprocess.run([sys.executable,'-m','mkdocs','build','--strict','-f',str(ROOT/'mkdocs.yml')],check=True,cwd=ROOT)
print(f'Prepared {len(catalog)} figures, Python bundle, designer and documentation.')

subprocess.run([sys.executable,str(ROOT/"scripts/package_source.py"),"--output",str(PUBLIC/"prabha-source.zip")],check=True)
