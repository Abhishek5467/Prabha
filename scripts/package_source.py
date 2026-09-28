"""Produce a clean, reproducible source distribution without environments/builds."""
from pathlib import Path
import argparse, zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.venv','.pytest_cache','__pycache__','node_modules','build','dist','target','.vscode','.openai'}
GENERATED={'frontend/studio/public/docs','frontend/studio/public/evidence','frontend/studio/public/designer.html','frontend/studio/public/prabha-python.zip','frontend/studio/public/prabha-source.zip'}
def package(output):
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    count=0
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(ROOT.rglob('*')):
            rel=f.relative_to(ROOT);name=rel.as_posix()
            if not f.is_file() or f.is_symlink() or f.resolve()==output:continue
            if any(part in EXCLUDED for part in rel.parts):continue
            if any(name==g or name.startswith(g+'/') for g in GENERATED):continue
            if name.startswith('desktop/src-tauri/binaries/prabha-engine-'):continue
            if (f.name=='.env' or f.name.startswith('.env.')) and f.name!='.env.example':continue
            if f.suffix in {'.pyc','.pem','.key','.exe'} or f.name=='Thumbs.db':continue
            info=zipfile.ZipInfo('Prabha-v0.1/'+name,date_time=(2026,9,28,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,f.read_bytes());count+=1
    print(f'Source package: {count} files -> {output.name}')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    package(parser.parse_args().output)
