"""Build a native Python sidecar; invoke on each target operating system."""
from pathlib import Path
import argparse, json, os, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--target-triple')
args=parser.parse_args()
triple=args.target_triple
if not triple:
    info=subprocess.check_output(['rustc','-vV'],text=True)
    triple=next(x.split(': ',1)[1] for x in info.splitlines() if x.startswith('host: '))
work=ROOT/'build/sidecar'; work.mkdir(parents=True,exist_ok=True)
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--name','prabha-engine',
     '--paths',str(ROOT/'core-py'),'--distpath',str(work/'dist'),'--workpath',str(work/'work'),
     '--specpath',str(work)]
for name in ['spec','blocks-lib','peman.prabha']:
    destination='.' if name=='peman.prabha' else name
    cmd.extend(['--add-data',str(ROOT/name)+os.pathsep+destination])
cmd.append(str(ROOT/'scripts/desktop_entry.py'))
subprocess.run(cmd,check=True,cwd=ROOT)
ext='.exe' if sys.platform=='win32' else ''
source=work/'dist'/('prabha-engine'+ext)
dest=ROOT/'desktop/src-tauri/binaries'/f'prabha-engine-{triple}{ext}'
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
result=json.loads(subprocess.check_output([str(dest),json.dumps({'action':'batch','count':100})],text=True))
assert result['ok'], result
assert abs(result['result']['rms_error']-7.864411795585e-5)<1e-12, result
assert result['result']['winner_mismatches']==0
print('Native sidecar reference batch passed:',dest)
