"""Regenerate the block catalogue and documentation page. Requires pandoc on PATH.

The checked-in HTML/MathML page works without pandoc during normal web builds.
Edit docs/manual/Prabha_User_Manual.md above 'Current block catalogue', then run:
  python scripts/build_manual.py
"""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / 'docs/manual/Prabha_User_Manual.md'

def main():
    prefix, marker, tail = MANUAL.read_text(encoding='utf-8').partition('\n# Current block catalogue\n')
    if not marker:
        raise ValueError('The manual must contain a Current block catalogue heading.')
    text = prefix + marker + tail.split('\n## ', 1)[0].rstrip() + '\n'
    catalogue = ''
    for file in sorted((ROOT/'spec/blocks').glob('model_*.json')):
        block = json.loads(file.read_text(encoding='utf-8'))
        catalogue += '\n## ' + block['title'] + '\n\n`' + block['id'] + '` · `' + block['implementation'] + '`\n\n' + block['description'] + '\n\n'
        def ports(direction):
            return ', '.join('`'+p['name']+'` ('+p['kind']+')' for p in block['ports'][direction]) or 'none'
        catalogue += 'Inputs: '+ports('inputs')+'. Outputs: '+ports('outputs')+'.\n\n'
        if not block['params']:
            catalogue += 'No editable parameters.\n'
            continue
        catalogue += '| Parameter | Default / unit | Meaning |\n|:--|:--|:--|\n'
        for p in block['params']:
            value = str(p['default']).lower() if isinstance(p['default'], bool) else str(p['default'])
            if p['name'] == 'bias_rad':
                value = '1.5707963268'
            meaning = p.get('description', '')
            if 'options' in p:
                meaning += ' Options: '+', '.join(map(str,p['options']))+'.'
            if 'min' in p and 'max' in p:
                meaning += f" Allowed: {p['min']:g} to {p['max']:g}."
            catalogue += f"| `{p['name']}` | {value} {p.get('unit', '')} | {meaning.replace('|',' / ')} |\n"
    MANUAL.write_text(text+catalogue, encoding='utf-8')
    guide = ROOT/'docs/site/designer.md'
    guide.write_text(guide.read_text(encoding='utf-8').split('## Model catalogue')[0] + '## Model catalogue\n\nThe defaults below come from the current block definitions. Read the [extended user manual](user-manual.md) for the full mathematical derivation, demonstrations and interpretation.\n' + catalogue.replace('\n## ', '\n### '), encoding='utf-8')
    html = subprocess.check_output(['pandoc',str(MANUAL),'-f','markdown','-t','html5','--mathml','--toc','--standalone','--metadata','pagetitle=Prabha manual'], text=True, encoding='utf-8')
    body = html.split('<body>')[1].split('</body>')[0]
    (ROOT/'docs/site/user-manual.md').write_text('<!-- Generated from docs/manual/Prabha_User_Manual.md using pandoc --mathml. -->\n\n'+body, encoding='utf-8')
    print('Updated model catalogue and documentation page.')

if __name__ == '__main__':
    main()
