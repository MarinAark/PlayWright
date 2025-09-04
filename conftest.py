import pytest
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Generator

# 可选导入
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# 导入配置管理器
from config.config_manager import get_config_manager, get_config

try:
    from utils.database_client import create_database_client
    DATABASE_CLIENT_AVAILABLE = True
except ImportError:
    DATABASE_CLIENT_AVAILABLE = False

try:
    from utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

# 全局配置
config_manager = get_config_manager()
test_config = get_config()


def pytest_configure(config):
    """pytest配置钩子"""
    # 创建必要的目录
    directories = [
        test_config.report.screenshot_dir,
        test_config.report.video_dir,
        test_config.report.allure_results_dir,
        test_config.performance.results_dir,
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 配置日志级别
    log_level = test_config.custom.get('log_level', 'INFO')
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    logger.info(f"测试环境: {test_config.environment}")
    logger.info(f"配置加载完成，日志级别: {log_level}")


def pytest_collection_modifyitems(config, items):
    """修改测试项收集"""
    # 为性能测试添加标记
    for item in items:
        if "performance" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)
        
        if "stress" in item.nodeid.lower():
            item.add_marker(pytest.mark.stress)
        
        if "database" in item.nodeid.lower():
            item.add_marker(pytest.mark.database)


@pytest.fixture(scope="session")
def config():
    """测试配置fixture"""
    return test_config


@pytest.fixture(scope="function")
def page(request) -> Generator:
    """浏览器页面fixture"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright未安装，跳过UI测试")
    
    browser_config = test_config.browser
    
    with sync_playwright() as p:
        # 选择浏览器类型
        if browser_config.browser_type == 'firefox':
            browser_launcher = p.firefox
        elif browser_config.browser_type == 'webkit':
            browser_launcher = p.webkit
        else:
            browser_launcher = p.chromium
        
        # 启动浏览器
        browser = browser_launcher.launch(
            headless=browser_config.headless,
            slow_mo=browser_config.slow_mo,
            devtools=browser_config.devtools,
            args=browser_config.args
        )
        
        # 创建浏览器上下文
        context_options = {
            'viewport': {
                'width': browser_config.viewport_width, 
                'height': browser_config.viewport_height
            },
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 如果配置了视频录制
        if test_config.report.capture_videos:
            context_options['record_video_dir'] = test_config.report.video_dir
            context_options['record_video_size'] = {
                'width': browser_config.viewport_width,
                'height': browser_config.viewport_height
            }
        
        context = browser.new_context(**context_options)
        page = context.new_page()
        page.set_default_timeout(browser_config.timeout)
        
        yield page
        
        # 测试结束后的清理
        try:
            # 如果测试失败且配置了截图，保存截图
            if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
                if test_config.report.capture_screenshots:
                    screenshot_path = Path(test_config.report.screenshot_dir) / f"{request.node.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                    page.screenshot(path=str(screenshot_path))
                    logger.info(f"失败截图已保存: {screenshot_path}")
            
        except Exception as e:
            logger.warning(f"保存截图失败: {e}")
        
        finally:
            context.close()
            browser.close()


@pytest.fixture(scope="session")
def database_client():
    """数据库客户端fixture"""
    if not DATABASE_CLIENT_AVAILABLE:
        pytest.skip("数据库客户端不可用")
        
    if not test_config.database.type:
        pytest.skip("未配置数据库")
    
    db_config = {
        'type': test_config.database.type,
        'host': test_config.database.host,
        'port': test_config.database.port,
        'database': test_config.database.database,
        'user': test_config.database.username,
        'password': test_config.database.password
    }
    
    try:
        client = create_database_client(db_config)
        logger.info(f"数据库客户端已创建: {test_config.database.type}")
        yield client
    except Exception as e:
        logger.warning(f"数据库连接失败: {e}")
        pytest.skip(f"数据库不可用: {e}")
    finally:
        if 'client' in locals():
            client.close()


@pytest.fixture(scope="function")
def api_client():
    """API客户端fixture"""
    import requests
    from utils.api_client import APIClient
    
    try:
        client = APIClient(
            base_url=test_config.api.base_url,
            timeout=test_config.api.timeout,
            max_retries=test_config.api.max_retries,
            verify_ssl=test_config.api.verify_ssl
        )
        
        # 设置默认头部
        for key, value in test_config.api.headers.items():
            client.set_header(key, value)
        
        logger.info(f"API客户端已创建: {test_config.api.base_url}")
        yield client
        
    except Exception as e:
        logger.warning(f"API客户端创建失败: {e}")
        pytest.skip(f"API不可用: {e}")
    finally:
        if 'client' in locals():
            client.close()


@pytest.fixture(scope="function")
def temp_directory(tmp_path):
    """临时目录fixture"""
    temp_dir = tmp_path / "test_temp"
    temp_dir.mkdir()
    
    yield temp_dir
    
    # 清理临时文件
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"清理临时目录失败: {e}")


@pytest.fixture(scope="function")
def performance_metrics():
    """性能指标收集fixture"""
    import time
    from utils.performance_tester import PerformanceMetrics
    
    metrics = PerformanceMetrics()
    metrics.start_time = time.time()
    
    yield metrics
    
    metrics.end_time = time.time()
    
    # 记录性能指标
    if metrics.response_times:
        logger.info(f"性能指标 - 平均响应时间: {metrics.avg_response_time:.2f}ms")
        logger.info(f"性能指标 - 成功率: {metrics.success_rate:.2f}%")


# pytest钩子函数
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """生成测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
    
    # 记录测试结果
    if rep.when == "call":
        if rep.passed:
            logger.info(f"✅ 测试通过: {item.nodeid}")
        elif rep.failed:
            logger.error(f"❌ 测试失败: {item.nodeid}")
            if rep.longrepr:
                logger.error(f"失败原因: {rep.longrepr}")
        elif rep.skipped:
            logger.info(f"⏭️  测试跳过: {item.nodeid}")


def pytest_sessionstart(session):
    """测试会话开始钩子"""
    logger.info("=" * 60)
    logger.info("测试会话开始")
    logger.info(f"测试环境: {test_config.environment}")
    logger.info(f"API地址: {test_config.api.base_url}")
    logger.info(f"数据库类型: {test_config.database.type}")
    logger.info("=" * 60)


def pytest_sessionfinish(session, exitstatus):
    """测试会话结束钩子"""
    logger.info("=" * 60)
    logger.info("测试会话结束")
    logger.info(f"退出状态: {exitstatus}")
    
    # 生成测试报告链接
    if test_config.report.generate_html and Path(test_config.report.html_report_path).exists():
        logger.info(f"HTML报告: {Path(test_config.report.html_report_path).absolute()}")
    
    if test_config.report.generate_allure and Path(test_config.report.allure_results_dir).exists():
        logger.info(f"Allure结果: {Path(test_config.report.allure_results_dir).absolute()}")
    
    logger.info("=" * 60)


# 自定义标记
# 注意：pytest_configure_node 不是有效的pytest钩子，已移除