# 测试最佳实践指南

本文档提供了使用本测试框架的最佳实践建议，帮助团队编写高质量、可维护的测试代码。

## 📋 目录

- [测试设计原则](#测试设计原则)
- [代码组织](#代码组织)
- [数据管理](#数据管理)
- [错误处理](#错误处理)
- [性能优化](#性能优化)
- [CI/CD集成](#cicd集成)
- [维护和监控](#维护和监控)

## 🎯 测试设计原则

### 1. FIRST原则

**Fast (快速)**
```python
# ✅ 好的做法：使用内存数据库进行快速测试
@pytest.fixture(scope="function")
def in_memory_db():
    return DatabaseClient('sqlite', {'database': ':memory:'})

# ❌ 避免：每个测试都连接真实数据库
def test_slow_db_operation():
    db = DatabaseClient('mysql', real_db_config)  # 慢
```

**Independent (独立)**
```python
# ✅ 好的做法：每个测试独立清理数据
@pytest.fixture(autouse=True)
def cleanup_test_data(db_client):
    yield
    db_client.execute_update("DELETE FROM test_users WHERE username LIKE 'test_%'")

# ❌ 避免：测试之间有依赖关系
def test_create_user():
    # 依赖前一个测试的数据
    pass
```

**Repeatable (可重复)**
```python
# ✅ 好的做法：使用固定的测试数据
@pytest.fixture
def test_user_data():
    return {
        "username": f"test_user_{int(time.time())}",
        "email": "test@example.com"
    }

# ❌ 避免：使用随机数据导致不可重现的失败
def test_with_random_data():
    user_id = random.randint(1, 1000000)  # 不可预测
```

### 2. 测试金字塔

```
    /\
   /  \    E2E Tests (少量)
  /____\   
 /      \   Integration Tests (适量)
/__________\ Unit Tests (大量)
```

**单元测试 (70%)**
```python
# 测试单个函数或方法
def test_user_validation():
    user_data = {"username": "test", "email": "invalid-email"}
    validator = UserValidator()
    assert not validator.is_valid(user_data)
```

**集成测试 (20%)**
```python
# 测试组件之间的交互
def test_user_creation_flow(api_client, db_client):
    # 创建用户
    response = api_client.post("/users", {"username": "test", "email": "test@example.com"})
    assert response.status_code == 201
    
    # 验证数据库中的数据
    users = db_client.execute_query("SELECT * FROM users WHERE username = 'test'")
    assert len(users) == 1
```

**端到端测试 (10%)**
```python
# 测试完整的用户场景
def test_complete_user_journey(page):
    # 注册 -> 登录 -> 使用功能 -> 注销
    pass
```

## 📂 代码组织

### 1. 页面对象模型 (POM)

```python
# pages/login_page.py
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator("#username")
        self.password_input = page.locator("#password")
        self.login_button = page.locator("#login-btn")
    
    def login(self, username: str, password: str):
        """执行登录操作"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        
        # 等待登录完成
        self.page.wait_for_url("**/dashboard")
    
    def is_error_displayed(self) -> bool:
        """检查是否显示错误信息"""
        return self.page.locator(".error-message").is_visible()
```

### 2. API客户端封装

```python
# pages/user_api.py
class UserAPI:
    def __init__(self, api_client):
        self.client = api_client
        self.base_path = "/api/v1/users"
    
    def create_user(self, user_data: dict) -> dict:
        """创建用户"""
        response = self.client.post(self.base_path, json=user_data)
        self.client.assert_status_code(response, 201)
        return response.json()
    
    def get_user(self, user_id: int) -> dict:
        """获取用户信息"""
        response = self.client.get(f"{self.base_path}/{user_id}")
        self.client.assert_status_code(response, 200)
        return response.json()
```

### 3. 测试数据工厂

```python
# utils/test_data_factory.py
class UserDataFactory:
    @staticmethod
    def create_valid_user(username: str = None) -> dict:
        """创建有效的用户数据"""
        timestamp = int(time.time())
        return {
            "username": username or f"user_{timestamp}",
            "email": f"user_{timestamp}@example.com",
            "password": "ValidPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
    
    @staticmethod
    def create_invalid_user() -> dict:
        """创建无效的用户数据"""
        return {
            "username": "",  # 空用户名
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 弱密码
        }
```

## 💾 数据管理

### 1. 测试数据隔离

```python
# ✅ 好的做法：使用唯一标识符
@pytest.fixture
def test_user(api_client):
    user_data = UserDataFactory.create_valid_user(f"test_user_{uuid.uuid4()}")
    user = api_client.create_user(user_data)
    
    yield user
    
    # 清理
    api_client.delete_user(user["id"])

# ❌ 避免：硬编码的测试数据
def test_with_hardcoded_data():
    user_data = {"username": "testuser", "email": "test@example.com"}  # 可能冲突
```

### 2. 数据库事务管理

```python
@pytest.fixture
def db_transaction(db_client):
    """数据库事务fixture，自动回滚"""
    # 开始事务
    db_client.execute_update("BEGIN TRANSACTION")
    
    yield db_client
    
    # 回滚事务
    db_client.execute_update("ROLLBACK")
```

### 3. 外部数据源管理

```python
# test_data/users.yaml
test_users:
  valid_admin:
    username: "admin_user"
    email: "admin@example.com"
    role: "admin"
  
  valid_regular:
    username: "regular_user"
    email: "user@example.com"
    role: "user"

# 在测试中使用
@pytest.fixture
def user_data():
    with open("test_data/users.yaml") as f:
        return yaml.safe_load(f)["test_users"]
```

## 🚨 错误处理

### 1. 异常处理策略

```python
# ✅ 好的做法：具体的异常处理
def test_api_error_handling(api_client):
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        api_client.get("/nonexistent-endpoint")
    
    assert exc_info.value.response.status_code == 404
    assert "not found" in exc_info.value.response.text.lower()

# ❌ 避免：捕获所有异常
def test_bad_error_handling():
    try:
        # 一些操作
        pass
    except Exception:  # 太宽泛
        pass
```

### 2. 重试机制

```python
import tenacity

@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    retry=tenacity.retry_if_exception_type(requests.exceptions.RequestException)
)
def test_with_retry(api_client):
    """带重试机制的测试"""
    response = api_client.get("/unstable-endpoint")
    assert response.status_code == 200
```

### 3. 软断言

```python
def test_multiple_assertions(api_client):
    """使用软断言收集多个错误"""
    errors = []
    
    response = api_client.get("/user/1")
    
    # 收集所有错误
    if response.status_code != 200:
        errors.append(f"Expected status 200, got {response.status_code}")
    
    data = response.json()
    if "username" not in data:
        errors.append("Missing username field")
    
    if "email" not in data:
        errors.append("Missing email field")
    
    # 一次性报告所有错误
    if errors:
        pytest.fail("Multiple assertion failures:\n" + "\n".join(errors))
```

## ⚡ 性能优化

### 1. 并行执行

```python
# pytest.ini
[tool:pytest]
addopts = -n auto  # 自动并行

# 或者在命令行
pytest tests/ -n 4  # 使用4个进程
```

### 2. 测试标记和分组

```python
# 标记慢速测试
@pytest.mark.slow
def test_heavy_operation():
    pass

# 标记集成测试
@pytest.mark.integration
def test_database_integration():
    pass

# 运行时过滤
# pytest tests/ -m "not slow"  # 跳过慢速测试
# pytest tests/ -m integration  # 只运行集成测试
```

### 3. Fixture作用域优化

```python
# ✅ 好的做法：合适的作用域
@pytest.fixture(scope="session")  # 整个测试会话只创建一次
def database_connection():
    return create_connection()

@pytest.fixture(scope="class")  # 每个测试类创建一次
def test_data_setup():
    return setup_test_data()

@pytest.fixture(scope="function")  # 每个测试函数创建一次
def user_session():
    return create_user_session()
```

## 🔄 CI/CD集成

### 1. 环境配置

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install
    
    - name: Run tests
      run: |
        pytest tests/ --html=report.html --alluredir=allure-results
      env:
        TEST_ENV: ci
        BROWSER_HEADLESS: true
```

### 2. 测试报告集成

```python
# conftest.py
def pytest_configure(config):
    """配置测试环境"""
    if config.getoption("--alluredir"):
        # 添加环境信息到Allure报告
        allure.environment(
            Environment="CI",
            Python_Version=sys.version,
            Platform=platform.platform()
        )
```

### 3. 失败重试

```python
# pytest.ini
[tool:pytest]
addopts = --reruns 2 --reruns-delay 1  # 失败时重试2次，间隔1秒
```

## 📊 维护和监控

### 1. 测试覆盖率

```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest tests/ --cov=utils --cov=pages --cov-report=html
```

### 2. 测试稳定性监控

```python
# utils/test_monitor.py
class TestMonitor:
    def __init__(self):
        self.failure_counts = {}
    
    def record_failure(self, test_name: str):
        """记录测试失败"""
        self.failure_counts[test_name] = self.failure_counts.get(test_name, 0) + 1
    
    def get_flaky_tests(self, threshold: int = 5) -> list:
        """获取不稳定的测试"""
        return [test for test, count in self.failure_counts.items() if count >= threshold]
```

### 3. 性能基线

```python
# 设置性能基线
PERFORMANCE_BASELINES = {
    "api_response_time": 500,  # 毫秒
    "page_load_time": 3000,    # 毫秒
    "database_query_time": 100  # 毫秒
}

def test_performance_regression(api_client, performance_metrics):
    """检查性能回归"""
    start_time = time.time()
    response = api_client.get("/api/users")
    response_time = (time.time() - start_time) * 1000
    
    baseline = PERFORMANCE_BASELINES["api_response_time"]
    assert response_time <= baseline, f"Response time {response_time}ms exceeds baseline {baseline}ms"
```

## 🎯 测试策略建议

### 1. 测试优先级

**高优先级**
- 核心业务流程
- 用户注册和登录
- 支付流程
- 数据安全

**中优先级**
- 功能特性
- API端点
- 用户界面交互

**低优先级**
- 边缘案例
- 错误处理
- 性能优化

### 2. 测试环境管理

```python
# config/environments.py
ENVIRONMENTS = {
    "dev": {
        "api_url": "https://dev-api.example.com",
        "database": "dev_db",
        "debug": True
    },
    "staging": {
        "api_url": "https://staging-api.example.com",
        "database": "staging_db",
        "debug": False
    },
    "prod": {
        "api_url": "https://api.example.com",
        "database": "prod_db",
        "debug": False,
        "read_only": True  # 生产环境只读
    }
}
```

### 3. 测试数据生命周期

```python
class TestDataLifecycle:
    def setup(self):
        """测试开始前的数据准备"""
        self.create_base_data()
    
    def teardown(self):
        """测试结束后的数据清理"""
        self.cleanup_test_data()
    
    def create_base_data(self):
        """创建基础测试数据"""
        pass
    
    def cleanup_test_data(self):
        """清理测试数据"""
        pass
```

## 📚 参考资源

- [Playwright官方文档](https://playwright.dev/)
- [pytest官方文档](https://docs.pytest.org/)
- [Allure报告](https://docs.qameta.io/allure/)
- [测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)
- [页面对象模型](https://selenium-python.readthedocs.io/page-objects.html)

---

**记住：好的测试不仅要验证功能的正确性，还要易于维护、快速执行，并能提供有价值的反馈。**
