"""
配置管理系统
支持多环境配置、配置验证和动态加载
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
import logging

# 可选导入
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "test_db"
    username: str = ""
    password: str = ""
    connection_pool_size: int = 10
    timeout: int = 30


@dataclass
class APIConfig:
    """API测试配置"""
    base_url: str = "https://httpbin.org"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    verify_ssl: bool = True
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class BrowserConfig:
    """浏览器配置"""
    headless: bool = True
    timeout: int = 30000
    viewport_width: int = 1920
    viewport_height: int = 1080
    browser_type: str = "chromium"  # chromium, firefox, webkit
    slow_mo: int = 0
    devtools: bool = False
    args: list = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security'
    ])


@dataclass
class ReportConfig:
    """报告配置"""
    allure_results_dir: str = "results/allure-results"
    html_report_path: str = "results/report.html"
    screenshot_dir: str = "screenshots"
    video_dir: str = "videos"
    generate_allure: bool = True
    generate_html: bool = True
    capture_screenshots: bool = True
    capture_videos: bool = False


@dataclass
class PerformanceConfig:
    """性能测试配置"""
    default_concurrent_users: int = 10
    default_requests_per_user: int = 10
    max_response_time_ms: float = 5000.0
    min_success_rate: float = 95.0
    ramp_up_time: int = 0
    results_dir: str = "performance_results"


@dataclass
class TestConfig:
    """测试配置主类"""
    environment: str = "test"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config", env_file: str = ".env"):
        self.config_dir = Path(config_dir)
        self.env_file = Path(env_file)
        self._config = TestConfig()
        
        # 加载环境变量
        self._load_env_file()
        
        # 获取当前环境
        self.environment = os.getenv('TEST_ENV', 'test')
        self._config.environment = self.environment
        
        # 加载配置
        self._load_config()
    
    def _load_env_file(self):
        """加载环境变量文件"""
        if self.env_file.exists() and DOTENV_AVAILABLE:
            load_dotenv(self.env_file)
            logger.info(f"已加载环境变量文件: {self.env_file}")
        elif self.env_file.exists():
            logger.warning(f"环境变量文件存在但python-dotenv未安装: {self.env_file}")
    
    def _load_config(self):
        """加载配置文件"""
        # 加载基础配置
        self._load_base_config()
        
        # 加载环境特定配置
        self._load_environment_config()
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
        
        # 验证配置
        self._validate_config()
    
    def _load_base_config(self):
        """加载基础配置"""
        config_files = [
            self.config_dir / "config.yaml",
            self.config_dir / "config.yml",
            self.config_dir / "config.json"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    config_data = self._read_config_file(config_file)
                    self._merge_config(config_data)
                    logger.info(f"已加载基础配置: {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"加载配置文件失败 {config_file}: {e}")
    
    def _load_environment_config(self):
        """加载环境特定配置"""
        env_config_files = [
            self.config_dir / f"config.{self.environment}.yaml",
            self.config_dir / f"config.{self.environment}.yml",
            self.config_dir / f"config.{self.environment}.json"
        ]
        
        for config_file in env_config_files:
            if config_file.exists():
                try:
                    config_data = self._read_config_file(config_file)
                    self._merge_config(config_data)
                    logger.info(f"已加载环境配置: {config_file}")
                    break
                except Exception as e:
                    logger.warning(f"加载环境配置文件失败 {config_file}: {e}")
    
    def _read_config_file(self, config_file: Path) -> Dict[str, Any]:
        """读取配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                if not YAML_AVAILABLE:
                    logger.warning(f"YAML文件存在但PyYAML未安装，跳过: {config_file}")
                    return {}
                return yaml.safe_load(f) or {}
            elif config_file.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {config_file.suffix}")
    
    def _merge_config(self, config_data: Dict[str, Any]):
        """合并配置数据"""
        if not config_data:
            return
        
        # 数据库配置
        if 'database' in config_data:
            db_config = config_data['database']
            for key, value in db_config.items():
                if hasattr(self._config.database, key):
                    setattr(self._config.database, key, value)
        
        # API配置
        if 'api' in config_data:
            api_config = config_data['api']
            for key, value in api_config.items():
                if hasattr(self._config.api, key):
                    setattr(self._config.api, key, value)
        
        # 浏览器配置
        if 'browser' in config_data:
            browser_config = config_data['browser']
            for key, value in browser_config.items():
                if hasattr(self._config.browser, key):
                    setattr(self._config.browser, key, value)
        
        # 报告配置
        if 'report' in config_data:
            report_config = config_data['report']
            for key, value in report_config.items():
                if hasattr(self._config.report, key):
                    setattr(self._config.report, key, value)
        
        # 性能配置
        if 'performance' in config_data:
            perf_config = config_data['performance']
            for key, value in perf_config.items():
                if hasattr(self._config.performance, key):
                    setattr(self._config.performance, key, value)
        
        # 自定义配置
        if 'custom' in config_data:
            self._config.custom.update(config_data['custom'])
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 数据库配置
        if os.getenv('DB_TYPE'):
            self._config.database.type = os.getenv('DB_TYPE')
        if os.getenv('DB_HOST'):
            self._config.database.host = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            self._config.database.port = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            self._config.database.database = os.getenv('DB_NAME')
        if os.getenv('DB_USER'):
            self._config.database.username = os.getenv('DB_USER')
        if os.getenv('DB_PASSWORD'):
            self._config.database.password = os.getenv('DB_PASSWORD')
        
        # API配置
        if os.getenv('API_BASE_URL'):
            self._config.api.base_url = os.getenv('API_BASE_URL')
        if os.getenv('API_TIMEOUT'):
            self._config.api.timeout = int(os.getenv('API_TIMEOUT'))
        if os.getenv('API_MAX_RETRIES'):
            self._config.api.max_retries = int(os.getenv('API_MAX_RETRIES'))
        
        # 浏览器配置
        if os.getenv('BROWSER_HEADLESS'):
            self._config.browser.headless = os.getenv('BROWSER_HEADLESS').lower() == 'true'
        if os.getenv('BROWSER_TIMEOUT'):
            self._config.browser.timeout = int(os.getenv('BROWSER_TIMEOUT'))
        if os.getenv('BROWSER_VIEWPORT_WIDTH'):
            self._config.browser.viewport_width = int(os.getenv('BROWSER_VIEWPORT_WIDTH'))
        if os.getenv('BROWSER_VIEWPORT_HEIGHT'):
            self._config.browser.viewport_height = int(os.getenv('BROWSER_VIEWPORT_HEIGHT'))
        if os.getenv('BROWSER_TYPE'):
            self._config.browser.browser_type = os.getenv('BROWSER_TYPE')
    
    def _validate_config(self):
        """验证配置"""
        errors = []
        
        # 验证数据库配置
        if self._config.database.type not in ['sqlite', 'mysql', 'postgresql', 'mongodb']:
            errors.append(f"不支持的数据库类型: {self._config.database.type}")
        
        # 验证API配置
        if not self._config.api.base_url:
            errors.append("API base_url不能为空")
        
        if self._config.api.timeout <= 0:
            errors.append("API timeout必须大于0")
        
        # 验证浏览器配置
        if self._config.browser.browser_type not in ['chromium', 'firefox', 'webkit']:
            errors.append(f"不支持的浏览器类型: {self._config.browser.browser_type}")
        
        if self._config.browser.timeout <= 0:
            errors.append("浏览器timeout必须大于0")
        
        # 验证性能配置
        if self._config.performance.default_concurrent_users <= 0:
            errors.append("并发用户数必须大于0")
        
        if self._config.performance.min_success_rate < 0 or self._config.performance.min_success_rate > 100:
            errors.append("最小成功率必须在0-100之间")
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("配置验证通过")
    
    @property
    def config(self) -> TestConfig:
        """获取配置"""
        return self._config
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self._config.database
    
    def get_api_config(self) -> APIConfig:
        """获取API配置"""
        return self._config.api
    
    def get_browser_config(self) -> BrowserConfig:
        """获取浏览器配置"""
        return self._config.browser
    
    def get_report_config(self) -> ReportConfig:
        """获取报告配置"""
        return self._config.report
    
    def get_performance_config(self) -> PerformanceConfig:
        """获取性能配置"""
        return self._config.performance
    
    def get_custom_config(self, key: str, default: Any = None) -> Any:
        """获取自定义配置"""
        return self._config.custom.get(key, default)
    
    def update_config(self, section: str, key: str, value: Any):
        """更新配置"""
        if section == 'database' and hasattr(self._config.database, key):
            setattr(self._config.database, key, value)
        elif section == 'api' and hasattr(self._config.api, key):
            setattr(self._config.api, key, value)
        elif section == 'browser' and hasattr(self._config.browser, key):
            setattr(self._config.browser, key, value)
        elif section == 'report' and hasattr(self._config.report, key):
            setattr(self._config.report, key, value)
        elif section == 'performance' and hasattr(self._config.performance, key):
            setattr(self._config.performance, key, value)
        elif section == 'custom':
            self._config.custom[key] = value
        else:
            raise ValueError(f"未知的配置节或键: {section}.{key}")
        
        logger.info(f"配置已更新: {section}.{key} = {value}")
    
    def save_config(self, config_file: Optional[Path] = None):
        """保存配置到文件"""
        if config_file is None:
            config_file = self.config_dir / f"config.{self.environment}.yaml"
        
        config_data = {
            'database': {
                'type': self._config.database.type,
                'host': self._config.database.host,
                'port': self._config.database.port,
                'database': self._config.database.database,
                'username': self._config.database.username,
                'connection_pool_size': self._config.database.connection_pool_size,
                'timeout': self._config.database.timeout
            },
            'api': {
                'base_url': self._config.api.base_url,
                'timeout': self._config.api.timeout,
                'max_retries': self._config.api.max_retries,
                'retry_delay': self._config.api.retry_delay,
                'verify_ssl': self._config.api.verify_ssl,
                'headers': self._config.api.headers
            },
            'browser': {
                'headless': self._config.browser.headless,
                'timeout': self._config.browser.timeout,
                'viewport_width': self._config.browser.viewport_width,
                'viewport_height': self._config.browser.viewport_height,
                'browser_type': self._config.browser.browser_type,
                'slow_mo': self._config.browser.slow_mo,
                'devtools': self._config.browser.devtools,
                'args': self._config.browser.args
            },
            'report': {
                'allure_results_dir': self._config.report.allure_results_dir,
                'html_report_path': self._config.report.html_report_path,
                'screenshot_dir': self._config.report.screenshot_dir,
                'video_dir': self._config.report.video_dir,
                'generate_allure': self._config.report.generate_allure,
                'generate_html': self._config.report.generate_html,
                'capture_screenshots': self._config.report.capture_screenshots,
                'capture_videos': self._config.report.capture_videos
            },
            'performance': {
                'default_concurrent_users': self._config.performance.default_concurrent_users,
                'default_requests_per_user': self._config.performance.default_requests_per_user,
                'max_response_time_ms': self._config.performance.max_response_time_ms,
                'min_success_rate': self._config.performance.min_success_rate,
                'ramp_up_time': self._config.performance.ramp_up_time,
                'results_dir': self._config.performance.results_dir
            },
            'custom': self._config.custom
        }
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据文件扩展名选择保存格式
        if config_file.suffix.lower() in ['.yaml', '.yml'] and YAML_AVAILABLE:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, indent=2)
        else:
            # 如果YAML不可用，保存为JSON格式
            config_file = config_file.with_suffix('.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已保存: {config_file}")
    
    def print_config(self):
        """打印当前配置"""
        print(f"当前环境: {self.environment}")
        print(f"数据库配置: {self._config.database}")
        print(f"API配置: {self._config.api}")
        print(f"浏览器配置: {self._config.browser}")
        print(f"报告配置: {self._config.report}")
        print(f"性能配置: {self._config.performance}")
        print(f"自定义配置: {self._config.custom}")


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> TestConfig:
    """获取当前配置"""
    return get_config_manager().config
