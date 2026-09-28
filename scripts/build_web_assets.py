"""Build the browser's source bundle, evidence catalogue, designer and docs."""
from pathlib import Path
import json, shutil, subprocess, sys, zipfile
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'frontend/studio/public'
PUBLIC.mkdir(parents=True, exist_ok=True)
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
    for f in sorted(paths): z.write(f, f.relative_to(ROOT))
shim = '''
<script type="module">
const originalFetch=window.fetch.bind(window);window.__PRABHA_FETCH=originalFetch;
const engine=import('./engine.js');
window.fetch=async function(input,options={}){
 const path=typeof input==='string'?input:input.url;
 if(path==='/api/blocks'||path==='/api/run'){
  try {const {execute}=await engine;
   const payload=path==='/api/blocks'?{action:'blocks'}:{...JSON.parse(options.body),action:'graph'};
   const result=await execute(payload);
   return new Response(JSON.stringify(path==='/api/blocks'?result:{ok:true,...result}),{headers:{'Content-Type':'application/json'}});
  } catch(e) {return new Response(JSON.stringify({ok:false,error:e.message}),{status:422,headers:{'Content-Type':'application/json'}});}
 }
 return originalFetch(input,options);
};
</script>
'''
# A module is deferred; use a blocking shim that awaits its own lazy import instead.
shim=shim.replace('type="module"','').replace("const engine=import('./engine.js');", "const engine=import('./engine.js');")
html=(ROOT/'frontend/web/index.html').read_text(encoding='utf-8')
html=html.replace('</head>',shim+'</head>').replace('<body>','<body><a href="./" style="position:fixed;right:12px;bottom:12px;z-index:10000;background:#173b42;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none">← Prabha Studio</a>')
(PUBLIC/'designer.html').write_text(html, encoding='utf-8')
subprocess.run([sys.executable,'-m','mkdocs','build','--strict','-f',str(ROOT/'mkdocs.yml')],check=True,cwd=ROOT)
print(f'Prepared {len(catalog)} figures, Python bundle, designer and documentation.')

subprocess.run([sys.executable,str(ROOT/"scripts/package_source.py"),"--output",str(PUBLIC/"prabha-source.zip")],check=True)
