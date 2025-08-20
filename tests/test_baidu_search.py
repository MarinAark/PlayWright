from pages.baidu_page import BaiduPage
from utils.logger import get_logger
import allure
import pytest
import time

logger = get_logger(__name__)

@allure.epic("Web UI测试")
@allure.feature("百度搜索")
@allure.story("搜索关键词")
@pytest.mark.parametrize("keyword", ["Playwright 教程", "pytest 教程"])
def test_baidu_search(page, keyword):
    """测试百度搜索功能"""
    baidu = BaiduPage(page)
    
    try:
        with allure.step(f"访问百度首页"):
            allure.attach(f"搜索关键词: {keyword}", "测试参数", allure.attachment_type.TEXT)
            baidu.goto()
            
            # 获取页面信息用于调试
            page_title = baidu.get_page_title()
            page_url = baidu.get_page_url()
            allure.attach(f"页面标题: {page_title}\n页面URL: {page_url}", "页面信息", allure.attachment_type.TEXT)
            
            # 等待页面稳定
            time.sleep(2)
        
        with allure.step(f"执行搜索: {keyword}"):
            baidu.search(keyword)
            
            # 获取搜索后页面信息
            search_page_title = baidu.get_page_title()
            search_page_url = baidu.get_page_url()
            allure.attach(f"搜索后页面标题: {search_page_title}\n搜索后页面URL: {search_page_url}", "搜索结果页面信息", allure.attachment_type.TEXT)
        
        with allure.step("检查搜索结果是否加载"):
            result_loaded = baidu.is_result_loaded()
            allure.attach(f"搜索结果加载状态: {result_loaded}", "测试结果", allure.attachment_type.TEXT)
            assert result_loaded, f"搜索结果未正确加载，关键词: {keyword}"
            
        logger.info(f"✅ 成功搜索关键词: {keyword}")
        allure.attach(f"测试通过: {keyword}", "测试结果", allure.attachment_type.TEXT)
        
    except Exception as e:
        # 捕获异常并记录详细信息
        error_msg = f"搜索测试失败，关键词: {keyword}, 错误: {str(e)}"
        logger.error(error_msg)
        allure.attach(error_msg, "测试失败", allure.attachment_type.TEXT)
        
        # 尝试截图
        try:
            screenshot_path = f"screenshots/baidu_search_failed_{keyword}_{int(time.time())}.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, "失败截图", allure.attachment_type.PNG)
        except Exception as screenshot_error:
            allure.attach(f"截图失败: {str(screenshot_error)}", "截图错误", allure.attachment_type.TEXT)
        
        # 重新抛出异常
        raise

@allure.epic("Web UI测试")
@allure.feature("百度搜索")
@allure.story("页面加载验证")
def test_baidu_page_load(page):
    """测试百度页面基本加载功能"""
    baidu = BaiduPage(page)
    
    try:
        with allure.step("访问百度首页"):
            baidu.goto()
            
            # 验证页面基本信息
            page_title = baidu.get_page_title()
            page_url = baidu.get_page_url()
            
            allure.attach(f"页面标题: {page_title}", "页面标题", allure.attachment_type.TEXT)
            allure.attach(f"页面URL: {page_url}", "页面URL", allure.attachment_type.TEXT)
            
            # 基本验证
            assert "百度" in page_title, f"页面标题不包含'百度': {page_title}"
            assert "baidu.com" in page_url, f"页面URL不包含'baidu.com': {page_url}"
            
        logger.info("✅ 百度页面加载测试通过")
        allure.attach("页面加载测试通过", "测试结果", allure.attachment_type.TEXT)
        
    except Exception as e:
        error_msg = f"页面加载测试失败: {str(e)}"
        logger.error(error_msg)
        allure.attach(error_msg, "测试失败", allure.attachment_type.TEXT)
        
        # 尝试截图
        try:
            screenshot_path = f"screenshots/baidu_page_load_failed_{int(time.time())}.png"
            page.screenshot(path=screenshot_path)
            allure.attach.file(screenshot_path, "失败截图", allure.attachment_type.PNG)
        except Exception as screenshot_error:
            allure.attach(f"截图失败: {str(screenshot_error)}", "截图错误", allure.attachment_type.TEXT)
        
        raise
