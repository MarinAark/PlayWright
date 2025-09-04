# PlayWright 自动化测试项目

这是一个功能完整、企业级的自动化测试框架，基于 **Playwright** 和 **pytest** 构建，支持 Web UI 测试、API 测试、性能测试、数据库测试等多种测试类型。

## 🚀 项目特性

### 🌐 Web UI 测试
- 基于 Playwright 的现代浏览器自动化测试
- 页面对象模型 (POM) 设计模式
- 多浏览器支持 (Chromium, Firefox, WebKit)
- 智能截图和视频录制
- 自动错误捕获和报告

### 🔌 API 测试
- 完整的 HTTP/HTTPS 客户端封装
- 同步和异步请求支持
- 数据驱动测试支持
- 多种数据源支持 (JSON, Excel, YAML)
- 自动重试和错误处理机制
- 详细的请求/响应日志

### 🏃 性能测试
- 并发负载测试
- 压力测试和容量规划
- 响应时间分析和统计
- 性能基准测试
- 自动化性能报告生成
- 性能回归检测

### 🗄️ 数据库测试
- 多数据库支持 (SQLite, MySQL, PostgreSQL, MongoDB)
- 数据完整性验证
- 测试数据管理和清理
- 数据库性能测试
- 事务处理测试

### 🛠️ 实用工具集
- 文件批量下载工具
- 图片压缩工具
- 文件重命名工具
- 统一命令行接口
- 配置管理系统

### 📊 测试框架
- pytest 测试框架
- Allure 详细测试报告
- HTML 测试报告
- 参数化测试
- 测试标记和分类
- 并行测试执行
- 自动化CI/CD集成

## 📁 项目结构

```
play_wright/
├── config/                      # 配置管理
│   ├── __init__.py
│   ├── config_manager.py        # 配置管理器
│   ├── config.yaml              # 基础配置
│   ├── config.test.yaml         # 测试环境配置
│   └── config.prod.yaml         # 生产环境配置
├── pages/                       # 页面对象模型
│   ├── __init__.py
│   ├── baidu_page.py           # 百度页面对象
│   └── api_pages.py            # API页面对象
├── tests/                       # 测试用例
│   ├── __init__.py
│   ├── conftest.py             # 测试配置
│   ├── test_baidu_search.py    # Web UI测试
│   ├── test_api_basic.py       # 基础API测试
│   ├── test_api_data_driven.py # 数据驱动API测试
│   ├── test_database_integration.py # 数据库测试
│   ├── test_performance.py     # 性能测试
│   └── results/                # 测试结果
├── tools/                       # 实用工具集
│   ├── __init__.py
│   ├── cli.py                  # 命令行工具入口
│   ├── file_renamer.py         # 文件重命名工具
│   ├── image_compressor.py     # 图片压缩工具
│   └── file_downloader.py      # 文件下载工具
├── utils/                       # 核心工具类
│   ├── __init__.py
│   ├── api_client.py           # API客户端
│   ├── database_client.py      # 数据库客户端
│   ├── performance_tester.py   # 性能测试工具
│   ├── test_data.py            # 测试数据管理
│   └── logger.py               # 日志工具
├── test_data/                   # 测试数据
│   ├── sample_users.json       # 示例用户数据
│   ├── performance_results.json
│   └── batch_user_creation_*.json
├── results/                     # 测试结果
│   ├── allure-results/         # Allure报告数据
│   └── report.html             # HTML测试报告
├── performance_results/         # 性能测试结果
├── screenshots/                 # 测试截图
├── videos/                      # 测试视频
├── logs/                        # 日志文件
├── scripts/                     # 脚本文件
├── docs/                        # 文档
├── conftest.py                  # 全局pytest配置
├── pytest.ini                  # pytest配置
├── requirements.txt             # Python依赖
├── .env.example                 # 环境变量示例
├── run_api_tests.py            # API测试运行脚本
├── Jenkinsfile                 # Jenkins CI/CD配置
└── README.md                   # 项目文档
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

## ⚙️ 浏览器配置

项目默认使用**无头模式**运行浏览器测试，以提高执行效率。如需修改配置，可以通过环境变量控制：

```bash
# 设置为有头模式（显示浏览器窗口）
export BROWSER_HEADLESS=false

# 设置浏览器超时时间（毫秒）
export BROWSER_TIMEOUT=30000

# 设置浏览器视口大小
export BROWSER_VIEWPORT_WIDTH=1920
export BROWSER_VIEWPORT_HEIGHT=1080
```

### 浏览器配置选项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `BROWSER_HEADLESS` | `true` | 是否使用无头模式 |
| `BROWSER_TIMEOUT` | `30000` | 页面操作超时时间（毫秒） |
| `BROWSER_VIEWPORT_WIDTH` | `1920` | 浏览器视口宽度 |
| `BROWSER_VIEWPORT_HEIGHT` | `1080` | 浏览器视口高度 |
```

## 🚀 使用方法

### 🌐 Web UI 测试

```bash
# 运行所有UI测试
pytest tests/test_baidu_search.py

# 运行特定测试用例
pytest tests/test_baidu_search.py::test_baidu_search

# 使用不同浏览器
TEST_ENV=test BROWSER_TYPE=firefox pytest tests/test_baidu_search.py

# 有头模式运行（显示浏览器）
BROWSER_HEADLESS=false pytest tests/test_baidu_search.py
```

### 🔌 API 测试

```bash
# 使用运行脚本（推荐）
python run_api_tests.py

# 运行所有API测试
pytest tests/ -m api

# 运行特定API测试
pytest tests/test_api_basic.py

# 数据驱动测试
pytest tests/test_api_data_driven.py

# 并行运行测试
pytest tests/ -n auto
```

### 🗄️ 数据库测试

```bash
# 运行数据库集成测试
pytest tests/test_database_integration.py

# 运行数据库性能测试
pytest tests/test_database_integration.py -m slow

# 跳过数据库测试（如果没有数据库）
pytest tests/ -m "not database"
```

### 🏃 性能测试

```bash
# 运行基础性能测试
pytest tests/test_performance.py::TestAPIPerformance::test_basic_load_test

# 运行压力测试
pytest tests/test_performance.py -m stress

# 运行完整性能测试套件
pytest tests/test_performance.py::TestPerformanceTestSuite

# 生成性能报告
pytest tests/test_performance.py --alluredir=performance_results/allure
```

### 🛠️ 工具使用

```bash
# 文件重命名工具
python tools/cli.py rename /path/to/files --dry-run

# 图片压缩工具
python tools/cli.py compress /path/to/images -s 2.0 --recursive

# 文件批量下载
python tools/cli.py download data.xlsx -d ./downloads

# 查看工具帮助
python tools/cli.py --help
```

### 📊 报告生成

```bash
# 生成HTML报告
pytest tests/ --html=results/report.html --self-contained-html

# 生成Allure报告
pytest tests/ --alluredir=results/allure-results
allure serve results/allure-results

# 生成性能报告
pytest tests/test_performance.py --alluredir=performance_results/allure
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

### 🚀 Jenkins集成

#### 必需的Jenkins插件
- **Allure Jenkins Plugin** - 生成Allure测试报告
- **HTML Publisher Plugin** - 发布HTML测试报告  
- **Email Extension Plugin** - 发送邮件通知
- **Git Plugin** - Git代码管理
- **Pipeline Plugin** - 流水线支持

#### 快速配置
1. **安装Allure命令行工具**：
   ```bash
   # 在Jenkins服务器上运行
   chmod +x scripts/install_allure_jenkins.sh
   sudo ./scripts/install_allure_jenkins.sh
   ```

2. **Jenkins系统配置**：
   - 进入 "Manage Jenkins" → "Configure System"
   - 找到 "Allure Commandline" 部分
   - 添加配置：Name=`Allure`, Home=`/opt/allure`

3. **创建流水线任务**：
   - 新建Pipeline任务
   - 选择 "Pipeline script from SCM"
   - Script Path: `Jenkinsfile`

#### 本地测试
在推送代码前，可以先本地验证Allure报告生成：
```bash
chmod +x scripts/test_allure_local.sh
./scripts/test_allure_local.sh
```

#### 故障排除
如果Jenkins无法生成Allure报告，请检查：
1. Allure命令行工具是否正确安装
2. Jenkins系统配置中的Allure路径
3. 测试是否生成了 `results/allure-results/` 目录
4. 查看详细的Jenkins配置指南：`docs/JENKINS_SETUP.md`

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
