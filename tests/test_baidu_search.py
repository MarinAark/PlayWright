from pages.baidu_page import BaiduPage
from utils.logger import get_logger
import allure
import pytest

logger = get_logger(__name__)

@allure.feature("百度搜索")
@allure.story("搜索关键词")
@pytest.mark.parametrize("keyword", ["Playwright 教程", "pytest 教程"])
def test_baidu_search(page, keyword):
    baidu = BaiduPage(page)
    baidu.goto()
    baidu.search(keyword)
    with allure.step("检查搜索结果是否加载"):
        assert baidu.is_result_loaded()
    logger.info(f"成功搜索关键词: {keyword}")
