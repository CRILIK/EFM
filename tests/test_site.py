"""Offline Chromium smoke + behavioral tests without external network.

The execution environment may block navigating to http://localhost and file://, so
we inject the built HTML with set_content, then inject static assets explicitly.
This still exercises the actual DOM and JS in Chromium. The PWA worker is tested
by static assertions separately because service workers require HTTPS/localhost.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,re
ROOT=Path(__file__).resolve().parent.parent
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
ARTJS=(ROOT/'assets/js/card-gallery.js').read_text(encoding='utf-8')
CSS=(ROOT/'assets/css/game.css').read_text(encoding='utf-8')

def exercise(width,height):
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=browser.new_page(viewport={'width':width,'height':height}, device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(HTML,wait_until='domcontentloaded',timeout=60000)
  page.add_style_tag(content=CSS)
  # Images cannot be fetched from disk inside this sandbox browser. Replace only
  # the image URLs for this isolated UI test; separately assert shipped files exist.
  png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+iV0YAAAAASUVORK5CYII='
  script=re.sub(r'assets/images/cards/[^"\\]+?\.webp',png,ARTJS)
  page.add_script_tag(content=script)
  page.wait_for_timeout(250)
  assert page.locator('#editionPicker').is_visible(), 'Missing game mode chooser'
  page.locator('#chooseChip').click()
  page.locator('[data-tab="setup"]').first.click()
  assert '6 «Знаков»' in page.locator('.startIntro').inner_text()
  page.locator('[data-action="startBuildAll"]').click()
  assert page.locator('.startPlayer').count()==3
  assert all('5 карт' in t or 'Первая рука сформирована' in t for t in page.locator('.startPlayer').all_inner_texts())
  page.locator('[data-tab="fast"]').first.click()
  assert page.locator('.handCard:not(button)').count()==5
  page.locator('[data-tab="library"]').first.click()
  assert page.locator('.libcard').count()>=100
  assert page.locator('.libcard img.cardArt').count()>25
  page.locator('[data-tab="strategy"]').first.click()
  assert page.locator('.planStep').count()>0
  page.locator('#chooseSwamp').click()
  assert page.locator('#swampFrame').is_visible()
  swamp=page.frame_locator('#swampFrame')
  swamp.locator('[data-act="tab"][data-v="catalog"]').first.click()
  page.wait_for_timeout(200)
  assert swamp.locator('.swampCardArt').count()>=10, 'No swamp gallery images in catalog'
  assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 3'), 'Horizontal overflow'
  assert not errors,errors
  page.screenshot(path=str(ROOT/f'tests/screenshot-{width}.png'),full_page=False)
  print('OK',width,height,'library images',page.locator('.libcard img.cardArt').count())
  browser.close()

if __name__=='__main__':
 for dims in [(390,844),(1280,800)]:exercise(*dims)
 data=json.loads((ROOT/'assets/data/krutagidon-catalog.json').read_text())
 assert len(data['cards'])>=130
 assert (ROOT/'assets/images/cards').exists()
 assert len(list((ROOT/'assets/images/cards').glob('*.webp')))>125
 assert 'fetch' in (ROOT/'sw.js').read_text()
 print('OK static catalog and PWA smoke')
