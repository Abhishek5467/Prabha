"""Build a native Python sidecar; invoke on each target operating system."""
from pathlib import Path
import argparse, os, platform, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--target-triple')
args=parser.parse_args()
info=subprocess.check_output(['rustc','-vV'],text=True)
host=next(x.split(': ',1)[1] for x in info.splitlines() if x.startswith('host: '))
triple=args.target_triple or host
if triple != host:
    parser.error('Build the sidecar on its native Rust host; cross-compilation is not supported.')
machine=platform.machine().lower()
expected='aarch64' if machine in {'arm64', 'aarch64'} else 'x86_64' if machine in {'amd64', 'x86_64'} else machine
if triple.split('-')[0] != expected:
    parser.error('Python architecture does not match the Rust host. Install native Python for this runner.')
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
subprocess.run([sys.executable, str(ROOT/'scripts/check_sidecar.py'), str(dest)], check=True)
print('Native sidecar ready:',dest)
