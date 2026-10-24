"""Optional actual Chromium smoke; start `python -m demo` first.

Install requirements-demo-browser.lock. Uses system Chromium by default; set
DEMO_CHROMIUM to its executable path. No browser/empirical screenshots committed.
"""
import os
from playwright.sync_api import sync_playwright, expect


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('DEMO_CHROMIUM', '/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1365, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8000')
        expect(page.locator("#dataset-description")).not_to_contain_text("geladen")
        page.get_by_role('button', name='Run analysis', exact=True).click()
        expect(page.locator("#status")).to_contain_text("abgeschlossen", timeout=90000)
        assert page.locator('#coefficients tr').count() == 6
        assert page.locator('#timeseries svg polyline').count() == 6
        page.get_by_role('button', name='Modelle vergleichen', exact=True).click()
        assert page.locator('#comparison-rows tr').count() == 2
        assert page.locator('#response-curves svg polyline').count() == 3
        with page.expect_download() as download:
            page.locator('#report-export').click()
        assert download.value.suggested_filename == 'synthetic-mmm-report.md'
        assert page.locator('#residuals svg polyline').count() == 1
        first = page.locator('#interpretation').inner_text()
        page.select_option('#model', 'without-quarter')
        page.get_by_role('button', name='Run analysis', exact=True).click()
        expect(page.locator("#status")).to_contain_text("abgeschlossen", timeout=90000)
        assert page.locator('#coefficients tr').count() == 5
        assert first != page.locator('#interpretation').inner_text()
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.locator('body').evaluate('(e)=>e.scrollWidth <= window.innerWidth')
        assert not errors, errors
        print('PASS: actual Chromium form, real fits, changed model, coefficients, SVG plot and mobile layout; no JavaScript page errors')
        browser.close()


if __name__ == '__main__':
    main()
