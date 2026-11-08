"""UB-style mobile delivery regression without external/network permissions.
Tested in real Chromium via set_content because navigation to localhost is blocked
by this runtime. Public HTTPS and PWA installation need a separate live test.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import re

ROOT=Path(__file__).resolve().parent.parent
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
CSS=(ROOT/'assets/css/game.css').read_text(encoding='utf-8')
PWA=(ROOT/'assets/js/pwa.js').read_text(encoding='utf-8')
ART=(ROOT/'assets/js/card-gallery.js').read_text(encoding='utf-8')


def exercise(width,height):
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.set_content(HTML,wait_until='domcontentloaded',timeout=60000)
        page.add_style_tag(content=CSS)
        page.evaluate("document.head.insertAdjacentHTML('afterbegin', '<base href=\"https://epic.test/\">')")
        # Under the isolated about:blank origin, image paths are not navigable.
        # The real map is verified via disk checks in test_integrity.py.
        page.add_script_tag(content=ART)
        page.add_script_tag(content=PWA)
        page.locator('#offlineOpen').click()
        assert page.locator('#offlinePanel').is_visible()
        assert 'офлайн' in page.locator('#offlineStatus').inner_text().lower()
        assert page.locator('#offlineInstall').is_hidden(), 'Install button must be hidden without an actual browser prompt'
        page.locator('#offlineClose').click()
        assert page.locator('#offlinePanel').is_hidden()
        page.locator('#chooseChip').click()
        page.locator('[data-tab="setup"]').first.click()
        page.locator('[data-action="startBuildAll"]').click()
        assert page.locator('.startPlayer').count()==3
        page.locator('[data-tab="fast"]').first.click()
        assert page.locator('.handCard:not(button)').count()==5
        page.locator('[data-tab="strategy"]').first.click()
        assert page.locator('.planStep').count()>0
        page.locator('#chooseSwamp').click()
        assert page.locator('#swampFrame').is_visible()
        swamp=page.frame_locator('#swampFrame')
        swamp.locator('[data-act="tab"][data-v="catalog"]').first.click()
        body=swamp.locator('#view').inner_text()
        assert '178 из 178 карт' in body,body[:80]
        assert '25/25' in body
        page.locator('#offlineOpen').click()
        assert page.locator('#offlinePanel').is_visible(), 'Offline help must be accessible in the swamp iframe too'
        page.locator('#offlineClose').click()
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 3'), 'Overflow at '+str(width)
        assert not errors,errors
        page.screenshot(path=str(ROOT/f'tests/preview-{width}-v14.png'),full_page=False)
        print(f'PASS {width}px: controls, first hand, 178/178, global offline panel')
        browser.close()

if __name__=='__main__':
    for shape in [(360,800),(390,844),(1280,800)]:exercise(*shape)
