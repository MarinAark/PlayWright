import pytest
from utils.api_client import APIClient
from utils.test_data import TestDataManager

# 可选导入allure
try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

@pytest.fixture(scope="session")
def api_client():
    """全局API客户端"""
    client = APIClient()
    yield client
    client.close()

@pytest.fixture(scope="session")
def test_data_manager():
    """测试数据管理器"""
    return TestDataManager()

@pytest.fixture(scope="function")
def clean_test_data():
    """清理测试数据"""
    yield
    # 这里可以添加测试后的清理逻辑
    pass

@pytest.fixture(scope="function")
def api_test_context():
    """API测试上下文"""
    context = {
        "test_id": None,
        "start_time": None,
        "end_time": None,
        "request_count": 0,
        "response_times": []
    }
    yield context
    
    # 测试结束后记录统计信息
    if context["start_time"] and context["end_time"] and ALLURE_AVAILABLE:
        duration = context["end_time"] - context["start_time"]
        avg_response_time = sum(context['response_times']) / len(context['response_times']) if context['response_times'] else 0
        allure.attach(
            f"测试统计:\n"
            f"请求次数: {context['request_count']}\n"
            f"平均响应时间: {avg_response_time:.2f}s\n"
            f"总耗时: {duration:.2f}s",
            "测试统计",
            allure.attachment_type.TEXT
        )

def pytest_collection_modifyitems(config, items):
    """修改测试项，添加标记"""
    for item in items:
        # 为API测试添加标记
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # 为慢速测试添加标记
        if "performance" in item.nodeid or "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # 为集成测试添加标记
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    
    # 设置测试结果属性
    setattr(item, f"rep_{rep.when}", rep)
    
    # 为失败的测试添加额外信息
    if rep.when == "call" and rep.failed:
        # 这里可以添加失败时的额外处理逻辑
        pass
