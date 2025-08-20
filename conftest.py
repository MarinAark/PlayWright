import pytest
import os
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@pytest.fixture(scope="function")
def page(request):
    with sync_playwright() as p:
        # 从环境变量读取浏览器配置，默认为无头模式
        headless = os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true'
        timeout = int(os.getenv('BROWSER_TIMEOUT', 30000))
        viewport_width = int(os.getenv('BROWSER_VIEWPORT_WIDTH', 1920))
        viewport_height = int(os.getenv('BROWSER_VIEWPORT_HEIGHT', 1080))
        
        # 启动浏览器
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # 创建浏览器上下文
        context = browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = context.new_page()
        page.set_default_timeout(timeout)
        
        yield page
        
        # 如果测试失败，保存截图
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