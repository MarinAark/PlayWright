import requests
import time
import json
import allure
from typing import Dict, Any, Optional, Union
from config.api_config import APIConfig
from utils.logger import get_logger

logger = get_logger(__name__)

class APIClient:
    """API测试客户端基类"""
    
    def __init__(self, base_url: str = None, headers: Dict = None):
        self.base_url = base_url or APIConfig.get_base_url()
        self.headers = headers or APIConfig.get_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.timeout = APIConfig.TIMEOUT
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # 记录请求信息
        with allure.step(f"发送 {method.upper()} 请求到 {url}"):
            allure.attach(
                json.dumps(kwargs, indent=2, ensure_ascii=False),
                "请求参数",
                allure.attachment_type.JSON
            )
            
            logger.info(f"发送 {method.upper()} 请求: {url}")
            logger.info(f"请求参数: {kwargs}")
            
            # 重试机制
            for attempt in range(APIConfig.MAX_RETRIES):
                try:
                    response = self.session.request(method, url, **kwargs)
                    
                    # 记录响应信息
                    allure.attach(
                        json.dumps({
                            'status_code': response.status_code,
                            'headers': dict(response.headers),
                            'body': response.text[:1000]  # 限制响应体长度
                        }, indent=2, ensure_ascii=False),
                        "响应信息",
                        allure.attachment_type.JSON
                    )
                    
                    logger.info(f"响应状态码: {response.status_code}")
                    logger.info(f"响应内容: {response.text[:200]}...")
                    
                    return response
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"请求失败 (尝试 {attempt + 1}/{APIConfig.MAX_RETRIES}): {e}")
                    if attempt < APIConfig.MAX_RETRIES - 1:
                        time.sleep(APIConfig.RETRY_DELAY)
                    else:
                        raise
                        
    def get(self, endpoint: str, params: Dict = None, **kwargs) -> requests.Response:
        """发送GET请求"""
        return self._make_request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Any = None, json_data: Any = None, **kwargs) -> requests.Response:
        """发送POST请求"""
        return self._make_request('POST', endpoint, data=data, json=json_data, **kwargs)
    
    def put(self, endpoint: str, data: Any = None, json_data: Any = None, **kwargs) -> requests.Response:
        """发送PUT请求"""
        return self._make_request('PUT', endpoint, data=data, json=json_data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """发送DELETE请求"""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Any = None, json_data: Any = None, **kwargs) -> requests.Response:
        """发送PATCH请求"""
        return self._make_request('PATCH', endpoint, data=data, json=json_data, **kwargs)
    
    def assert_status_code(self, response: requests.Response, expected_code: int):
        """断言响应状态码"""
        assert response.status_code == expected_code, \
            f"期望状态码 {expected_code}, 实际状态码 {response.status_code}"
    
    def assert_response_contains(self, response: requests.Response, expected_text: str):
        """断言响应内容包含指定文本"""
        assert expected_text in response.text, \
            f"响应内容不包含 '{expected_text}'"
    
    def assert_json_schema(self, response: requests.Response, schema: Dict):
        """断言JSON响应符合指定schema"""
        try:
            from jsonschema import validate
            validate(instance=response.json(), schema=schema)
        except ImportError:
            logger.warning("jsonschema 未安装，跳过schema验证")
        except Exception as e:
            assert False, f"JSON Schema 验证失败: {e}"
    
    def assert_response_time(self, response: requests.Response, max_time: float):
        """断言响应时间在指定范围内"""
        assert response.elapsed.total_seconds() <= max_time, \
            f"响应时间 {response.elapsed.total_seconds()}s 超过限制 {max_time}s"
    
    def close(self):
        """关闭会话"""
        self.session.close()
