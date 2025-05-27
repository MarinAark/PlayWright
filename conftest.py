import pytest
import os
from playwright.sync_api import sync_playwright
from datetime import datetime

@pytest.fixture(scope="function")
def page(request):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        yield page
        if request.node.rep_call.failed:
            screenshot_path = f"screenshots/{request.node.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            page.screenshot(path=screenshot_path)
        context.close()
        browser.close()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)