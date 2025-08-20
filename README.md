# PlayWright 自动化测试项目

这是一个基于 **Playwright** 和 **pytest** 的自动化测试项目，支持 Web UI 测试和 API 测试。

## 🚀 项目特性

### Web UI 测试
- 基于 Playwright 的浏览器自动化测试
- 页面对象模型 (POM) 设计模式
- 支持截图和错误捕获
- 多浏览器支持

### API 测试
- 完整的 HTTP 客户端封装
- 数据驱动测试支持
- 多种数据源支持 (JSON, Excel)
- 性能测试和响应时间监控
- 自动重试机制
- 详细的测试报告

### 测试框架
- pytest 测试框架
- Allure 测试报告
- HTML 测试报告
- 参数化测试
- 测试标记和分类

## 📁 项目结构

```
play_wright/
├── config/                 # 配置文件
│   └── api_config.py      # API测试配置
├── pages/                  # 页面对象
│   ├── baidu_page.py      # 百度页面对象
│   └── api_pages.py       # API页面对象
├── tests/                  # 测试用例
│   ├── test_baidu_search.py    # 百度搜索测试
│   ├── test_api_basic.py       # 基础API测试
│   ├── test_api_data_driven.py # 数据驱动API测试
│   └── conftest.py             # 测试配置
├── utils/                  # 工具类
│   ├── api_client.py      # API客户端
│   ├── test_data.py       # 测试数据管理
│   └── logger.py          # 日志工具
├── test_data/              # 测试数据
│   └── sample_users.json  # 示例用户数据
├── results/                # 测试结果
├── conftest.py             # 全局测试配置
├── pytest.ini             # pytest配置
├── requirements.txt        # 依赖包
├── run_api_tests.py       # API测试运行脚本
└── README.md              # 项目说明
```

## 🛠️ 环境要求

- Python 3.8+
- pip
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

## 📦 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

## 🚀 使用方法

### 运行 Web UI 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_baidu_search.py

# 运行特定测试用例
pytest tests/test_baidu_search.py::test_baidu_search
```

### 运行 API 测试

```bash
# 使用运行脚本（推荐）
python run_api_tests.py

# 运行所有API测试
pytest tests/ -m api

# 运行特定API测试
pytest tests/test_api_basic.py

# 并行运行测试
pytest tests/ -n auto

# 生成HTML报告
pytest tests/ --html=results/report.html --self-contained-html

# 生成Allure报告
pytest tests/ --alluredir=results/allure-results
allure serve results/allure-results
```

### 运行脚本参数

```bash
# 指定测试环境
python run_api_tests.py --env test

# 运行特定标记的测试
python run_api_tests.py --markers "slow"

# 并行运行
python run_api_tests.py --parallel

# 生成HTML报告
python run_api_tests.py --html

# 生成Allure报告
python run_api_tests.py --allure

# 清理测试结果
python run_api_tests.py --clean
```

## 🔧 配置说明

### 环境配置

复制 `env.example` 为 `.env` 并修改配置：

```bash
# API测试环境
API_ENV=test

# API地址配置
TEST_API_URL=https://httpbin.org
DEV_API_URL=https://dev-api.example.com
PROD_API_URL=https://api.example.com

# 超时和重试配置
API_TIMEOUT=30
API_MAX_RETRIES=3
API_RETRY_DELAY=1
```

### 测试标记

```python
@pytest.mark.api          # API测试
@pytest.mark.slow         # 慢速测试
@pytest.mark.integration  # 集成测试
@pytest.mark.unit         # 单元测试
```

## 📊 测试报告

### Allure 报告
```bash
# 生成报告
pytest --alluredir=results/allure-results

# 查看报告
allure serve results/allure-results
```

### HTML 报告
```bash
# 生成HTML报告
pytest --html=results/report.html --self-contained-html
```

## 📝 编写测试用例

### API 测试示例

```python
import pytest
import allure
from pages.api_pages import UserAPI

@allure.epic("用户管理")
@allure.feature("用户CRUD")
class TestUserManagement:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.api = UserAPI()
        yield
        self.api.close()
    
    @allure.story("创建用户")
    def test_create_user(self):
        user_data = {"username": "testuser", "email": "test@example.com"}
        response = self.api.create_user(user_data)
        
        self.api.assert_status_code(response, 201)
        created_user = response.json()
        assert created_user["username"] == user_data["username"]
```

### 数据驱动测试

```python
@pytest.mark.parametrize("user_data", [
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
])
def test_create_multiple_users(self, user_data):
    response = self.api.create_user(user_data)
    self.api.assert_status_code(response, 201)
```

## 🔄 CI/CD 集成

项目包含 Jenkins 流水线配置，支持：

- 自动代码拉取
- 环境设置
- 测试执行
- 报告生成
- 邮件通知

## 📈 扩展功能

### 已实现功能
- ✅ Web UI 自动化测试
- ✅ API 接口测试
- ✅ 数据驱动测试
- ✅ 性能测试
- ✅ 测试报告生成
- ✅ 错误重试机制
- ✅ 日志记录

### 可扩展功能
- 🔄 移动端测试
- 🔄 视觉回归测试
- 🔄 安全测试
- 🔄 负载测试
- 🔄 数据库测试
- 🔄 邮件测试

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。
