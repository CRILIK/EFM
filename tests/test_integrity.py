"""UB Mode data and delivery contracts: verify actual files, not UI decorations."""
from pathlib import Path
import json,re,subprocess
ROOT=Path(__file__).resolve().parent.parent
catalog=json.loads((ROOT/'assets/data/krutagidon-catalog.json').read_text(encoding='utf-8'))
arts=json.loads((ROOT/'assets/data/photo-map.json').read_text(encoding='utf-8'))
chips=catalog['cards']
assert len(chips)==134,len(chips)
assert sum(int(c['copies']) for c in chips)==245
assert len(set(c['name'] for c in chips))==len(chips)
assert all(c['name'] in arts for c in chips),'Card illustration unavailable'
assert all((ROOT/path).is_file() for path in arts.values()),'Image path points nowhere'
assert len(list((ROOT/'assets/images/cards').glob('*.webp')))>=220
assert (ROOT/'index.html').is_file()
assert (ROOT/'manifest.webmanifest').is_file()
manifest=json.loads((ROOT/'manifest.webmanifest').read_text(encoding='utf-8'))
assert manifest['display']=='standalone'
for icon in manifest['icons']:assert (ROOT/icon['src']).is_file()
assert './index.html' in (ROOT/'sw.js').read_text(encoding='utf-8')
assert 'Нельзя гарантировать' in (ROOT/'README.md').read_text(encoding='utf-8') or 'не гарантия' in (ROOT/'README.md').read_text(encoding='utf-8')
subprocess.run(['node','--check',str(ROOT/'assets/js/card-gallery.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'sw.js')],check=True)
subprocess.run(['node','--check',str(ROOT/'assets/js/pwa.js')],check=True)
print('PASS catalog: 245/245, chip images: 134/134, static assets: all valid')
