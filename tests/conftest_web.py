"""
Web UI测试专用配置文件
包含页面超时、重试机制等配置
"""

import pytest
import allure
from playwright.sync_api import sync_playwright
from datetime import datetime
import os

@pytest.fixture(scope="function")
def page(request):
    """Web UI测试专用的页面fixture"""
    with sync_playwright() as p:
        # 从环境变量读取浏览器配置，默认为无头模式
        headless = os.getenv('BROWSER_HEADLESS', 'true').lower() == 'true'
        timeout = int(os.getenv('BROWSER_TIMEOUT', 60000))  # 增加超时时间到60秒
        viewport_width = int(os.getenv('BROWSER_VIEWPORT_WIDTH', 1920))
        viewport_height = int(os.getenv('BROWSER_VIEWPORT_HEIGHT', 1080))
        
        # 启动浏览器，增加超时和性能优化
        browser = p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # 禁用图片加载以提高速度
                '--disable-javascript',  # 可选：禁用JavaScript
                '--disable-gpu',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-default-apps'
            ]
        )
        
        # 创建上下文，设置超时和视口
        context = browser.new_context(
            viewport={'width': viewport_width, 'height': viewport_height},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
            }
        )
        
        # 设置页面超时
        context.set_default_timeout(timeout)
        context.set_default_navigation_timeout(timeout)
        
        # 创建页面
        page = context.new_page()
        
        # 设置页面级别的超时
        page.set_default_timeout(timeout)
        page.set_default_navigation_timeout(timeout)
        
        # 添加页面事件监听器
        page.on("pageerror", lambda err: allure.attach(f"页面错误: {err}", "页面错误", allure.attachment_type.TEXT))
        page.on("console", lambda msg: allure.attach(f"控制台消息: {msg.text}", "控制台日志", allure.attachment_type.TEXT))
        
        yield page
        
        # 测试失败时截图
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            try:
                screenshot_path = f"screenshots/{request.node.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                page.screenshot(path=screenshot_path)
                allure.attach_file(screenshot_path, "失败截图", allure.attachment_type.PNG)
            except Exception as e:
                allure.attach(f"截图失败: {str(e)}", "截图错误", allure.attachment_type.TEXT)
        
        # 关闭浏览器
        context.close()
        browser.close()

@pytest.fixture(scope="session")
def browser_context_args():
    """浏览器上下文参数"""
    return {
        "viewport": {
            "width": 1920,
            "height": 1080
        },
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "extra_http_headers": {
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
    }

def pytest_runtest_setup(item):
    """测试运行前的设置"""
    # 为Web UI测试添加标记
    if "test_baidu" in item.nodeid:
        item.add_marker(pytest.mark.web_ui)
        item.add_marker(pytest.mark.slow)

def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    for item in items:
        if "test_baidu" in item.nodeid:
            item.add_marker(pytest.mark.web_ui)
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.integration)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    outcome = yield
    rep = outcome.get_result()
    
    # 设置测试结果属性
    setattr(item, f"rep_{rep.when}", rep)
    
    # 处理测试失败
    if rep.when == "call" and rep.failed:
        # 这里可以添加额外的失败处理逻辑
        pass
