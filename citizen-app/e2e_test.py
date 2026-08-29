import sys
import time
import json
import requests
from playwright.sync_api import sync_playwright

API = "http://127.0.0.1:8000/api/v1"
APP = "http://127.0.0.1:5500"

errors = []

def log(msg):
    print(f"[e2e] {msg}")

def on_console(msg):
    if msg.type == "error":
        # tile.openstreetmap.org is blocked by this sandbox's own network
        # egress policy (confirmed via direct curl — returns 403 for any
        # tool here, not just the browser). This is an environment
        # restriction, not an app bug: any Leaflet+OSM app needs outbound
        # access to the OSM tile CDN, which a normal demo venue will have.
        if "openstreetmap" in msg.text.lower() or (msg.location and "openstreetmap" in json.dumps(msg.location).lower()):
            log(f"(ignored sandbox-only OSM tile block) {msg.text}")
            return
        errors.append(msg.text)
        log(f"CONSOLE ERROR: {msg.text}")

def on_page_error(exc):
    errors.append(str(exc))
    log(f"PAGE ERROR: {exc}")

# Reset backend to a clean baseline before the run.
requests.post(f"{API}/admin/simulate-normal")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 420, "height": 860})
    page.on("console", on_console)
    page.on("pageerror", on_page_error)

    log("1. Load app")
    page.goto(APP, wait_until="networkidle")
    page.screenshot(path="/tmp/e2e_01_entry.png")
    assert page.is_visible("#screen-entry"), "entry screen not visible"

    log("2. Enter Demo (login)")
    page.click("#btn-enter-demo")
    page.wait_for_selector("#app-shell:not([hidden])", timeout=8000)
    page.wait_for_selector("#risk-body:not([hidden])", timeout=8000)
    page.screenshot(path="/tmp/e2e_02_home_low.png")

    risk_level = page.inner_text("#risk-level-label")
    risk_pct = page.inner_text("#risk-percent")
    log(f"   risk label='{risk_level}' pct='{risk_pct}'")
    assert "LOW" in risk_level, f"expected LOW baseline, got {risk_level}"

    log("3. Open Why sheet")
    page.click("#btn-why")
    page.wait_for_selector(".factor-card", timeout=8000)
    factor_count = page.locator(".factor-card").count()
    log(f"   factor cards: {factor_count}")
    assert factor_count == 4
    page.wait_for_timeout(350)  # let the sheet slide/fade-in animation settle
    page.screenshot(path="/tmp/e2e_03_why.png")
    page.click("[data-lang='hi']")
    time.sleep(0.3)
    page.screenshot(path="/tmp/e2e_03b_why_hindi.png")
    page.click("#btn-close-why")

    log("4. Open Map")
    page.click('.nav-btn[data-nav="map"]')
    page.wait_for_timeout(1500)
    page.screenshot(path="/tmp/e2e_04_map.png")
    leaflet_present = page.evaluate("() => !!document.querySelector('.leaflet-container')")
    assert leaflet_present, "leaflet map did not render"

    log("5. Open Safest Route")
    page.click("text=Safest Route")
    page.wait_for_selector(".route-card", timeout=8000)
    route_count = page.locator(".route-card").count()
    log(f"   route cards: {route_count}")
    assert route_count == 3
    page.wait_for_timeout(350)
    page.screenshot(path="/tmp/e2e_05_routes_before_block.png")
    recommended_before = page.locator(".route-card.is-recommended .route-name").inner_text()
    log(f"   recommended before block: {recommended_before}")
    assert recommended_before.startswith("Route A")
    page.click("#btn-close-routes")

    log("6. Trigger flood via admin API")
    resp = requests.post(f"{API}/admin/simulate-flood")
    log(f"   simulate-flood -> {resp.status_code} {resp.json().get('risk_level')} {resp.json().get('risk_score')}")

    log("   back to Home, waiting for citizen app to poll and pick up CRITICAL...")
    page.click('.nav-btn[data-nav="home"]')
    page.wait_for_function(
        "document.querySelector('#risk-level-label').textContent.includes('CRITICAL')",
        timeout=10000
    )
    page.wait_for_timeout(700)  # let the 0.6s ring-colour CSS transition settle before screenshotting
    page.screenshot(path="/tmp/e2e_06_home_critical.png")
    risk_level2 = page.inner_text("#risk-level-label")
    risk_pct2 = page.inner_text("#risk-percent")
    log(f"   risk label='{risk_level2}' pct='{risk_pct2}'")
    assert "CRITICAL" in risk_level2
    assert "87" in risk_pct2

    alert_banner_visible = page.is_visible("#home-alert-banner")
    log(f"   alert banner visible: {alert_banner_visible}")
    assert alert_banner_visible

    log("7. Open Alerts screen")
    page.click('.nav-btn[data-nav="alerts"]')
    page.wait_for_selector(".alert-card", timeout=8000)
    page.screenshot(path="/tmp/e2e_07_alerts.png")

    log("8. Block a road via admin API")
    resp = requests.post(f"{API}/admin/simulate-blocked-road")
    log(f"   simulate-blocked-road -> {resp.status_code} {resp.json()}")

    log("9. Open Map + Safest Route again, confirm recommendation changed")
    page.click('.nav-btn[data-nav="map"]')
    page.wait_for_timeout(1200)
    page.screenshot(path="/tmp/e2e_09_map_flood.png")
    page.click("text=Safest Route")
    page.wait_for_function(
        "document.querySelectorAll('.route-card.is-recommended .route-name').length > 0 && "
        "!document.querySelector('.route-card.is-recommended .route-name').textContent.startsWith('Route A')",
        timeout=10000
    )
    recommended_after = page.locator(".route-card.is-recommended .route-name").inner_text()
    log(f"   recommended after block: {recommended_after}")
    assert not recommended_after.startswith("Route A")
    page.wait_for_timeout(1300)  # let the just-changed flash animation settle for the screenshot
    page.screenshot(path="/tmp/e2e_09b_routes_after_block.png")
    page.click("#btn-close-routes")

    log("10. Emergency screen: I'm Safe")
    page.click('.nav-btn[data-nav="emergency"]')
    page.wait_for_selector("#screen-emergency.is-visible")
    page.click("#btn-im-safe-2")
    page.wait_for_selector("#emergency-result:not([hidden])", timeout=8000)
    safe_msg = page.inner_text("#emergency-result")
    log(f"   im-safe result: {safe_msg}")
    assert "Safety status recorded" in safe_msg
    page.screenshot(path="/tmp/e2e_10_imsafe.png")

    log("11. Emergency screen: Need Help")
    page.click("#btn-need-help-2")
    page.wait_for_function(
        "document.querySelector('#emergency-result').textContent.includes('Emergency request recorded')",
        timeout=8000
    )
    help_msg = page.inner_text("#emergency-result")
    log(f"   need-help result: {help_msg}")
    assert "Emergency request recorded" in help_msg
    page.screenshot(path="/tmp/e2e_11_needhelp.png")

    distress = requests.get(f"{API}/admin/distress-signals").json()
    log(f"   admin distress-signals: {distress}")
    assert len(distress) >= 1

    log("12. Submit citizen report")
    page.click('.nav-btn[data-nav="report"]')
    page.wait_for_selector("#screen-report.is-visible")
    page.select_option("#report-category", "ROAD_BLOCKED")
    page.fill("#report-description", "Playwright e2e test report - road impassable")
    page.click("#btn-submit-report")
    page.wait_for_selector("#report-result:not([hidden])", timeout=8000)
    report_msg = page.inner_text("#report-result")
    log(f"   report submit result: {report_msg}")
    assert "Report submitted for verification" in report_msg
    page.screenshot(path="/tmp/e2e_12_report.png")

    admin_reports = requests.get(f"{API}/admin/reports").json()
    found = any("Playwright e2e test report" in (r.get("description") or "") for r in admin_reports)
    log(f"   report visible in admin/reports: {found}")
    assert found

    log("13. Restore normal via admin API, confirm citizen app returns to LOW")
    requests.post(f"{API}/admin/simulate-normal")
    page.click('.nav-btn[data-nav="home"]')
    page.wait_for_function(
        "document.querySelector('#risk-level-label').textContent.includes('LOW')",
        timeout=10000
    )
    page.screenshot(path="/tmp/e2e_13_home_restored.png")
    final_level = page.inner_text("#risk-level-label")
    log(f"   final risk label: {final_level}")
    assert "LOW" in final_level

    browser.close()

if errors:
    print("\n=== CONSOLE/PAGE ERRORS DETECTED ===")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("\n=== ALL E2E STEPS PASSED, NO CONSOLE ERRORS ===")
