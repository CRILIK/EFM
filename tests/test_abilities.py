"""Behavioral regression of character ability's starting-deck modification."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from test_site import HTML,ARTJS,CSS
import re
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':390,'height':844})
 errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
 page.on('dialog',lambda d:d.accept())
 page.set_content(HTML,wait_until='domcontentloaded',timeout=60000)
 page.add_style_tag(content=CSS)
 png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+iV0YAAAAASUVORK5CYII='
 page.add_script_tag(content=re.sub(r'assets/images/cards/[^"\\]+?\.webp',png,ARTJS))
 page.locator('#chooseChip').click()
 page.locator('[data-tab="setup"]').first.click()
 print('before deck',page.locator('.startPlayer').first.inner_text()[:350])
 page.locator('.startPlayer [data-photo-compare="ability"]').first.click()
 print('modal visible',page.locator('#modal').is_visible())
 print('options',page.locator('#pc1 option').all_text_contents())
 try:
  page.locator('#pc1').select_option(label='Главный приз')
  page.locator('#pc2').select_option(label='Усиленная палочка')
  page.locator('[data-photo-result]').click()
  print('result',page.locator('.photoCompareCard').count())
  page.locator('[data-photo-pick="ability"]').last.click()
  print('after deck',page.locator('.startPlayer').first.inner_text()[:370])
  page.locator('[data-action="startBuildAll"]').click()
  print('after hand',page.locator('.startPlayer').first.inner_text()[:600])
  assert '×5' in page.locator('.startPlayer').first.inner_text()
  assert 'Палочка-хреналочка' in page.locator('.startPlayer').first.inner_text()
  assert not errors,errors
 except Exception as ex:
  print('exception',repr(ex))
  raise
 b.close()
