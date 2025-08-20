import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class APIConfig:
    """API测试配置类"""
    
    # 基础URL配置
    BASE_URLS = {
        'dev': os.getenv('DEV_API_URL', 'https://httpbin.org'),
        'test': os.getenv('TEST_API_URL', 'https://httpbin.org'),
        'prod': os.getenv('PROD_API_URL', 'https://httpbin.org')
    }
    
    # 当前环境
    CURRENT_ENV = os.getenv('API_ENV', 'test')
    
    # 超时配置
    TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    
    # 重试配置
    MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', 3))
    RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', 1))
    
    # 请求头配置
    DEFAULT_HEADERS = {
        'Content-Type': 'application/json',
        'User-Agent': 'PlayWright-API-Test/1.0'
    }
    
    # 认证配置
    AUTH_TOKEN = os.getenv('API_AUTH_TOKEN', '')
    
    @classmethod
    def get_base_url(cls):
        """获取当前环境的基础URL"""
        return cls.BASE_URLS.get(cls.CURRENT_ENV, cls.BASE_URLS['test'])
    
    @classmethod
    def get_headers(cls):
        """获取请求头"""
        headers = cls.DEFAULT_HEADERS.copy()
        if cls.AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {cls.AUTH_TOKEN}'
        return headers
