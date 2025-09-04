"""
重试装饰器
用于处理网络不稳定和外部服务不可用的情况
"""
import time
import logging
from functools import wraps
from typing import Callable, Tuple, Type, Union
import pytest

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    skip_on_final_failure: bool = True,
    skip_message: str = "服务不可用，跳过测试"
):
    """
    重试装饰器，用于处理测试中的网络不稳定问题
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟递增倍数
        exceptions: 需要重试的异常类型
        skip_on_final_failure: 最终失败时是否跳过测试
        skip_message: 跳过测试时的消息
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 第{attempt+1}次执行失败: {e}, "
                            f"{current_delay:.1f}秒后重试..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"函数 {func.__name__} 在{max_retries}次重试后仍然失败")
                        
                        if skip_on_final_failure:
                            pytest.skip(f"{skip_message}: {e}")
                        else:
                            raise e
                            
                except Exception as e:
                    # 对于不在重试范围内的异常，直接抛出
                    logger.error(f"函数 {func.__name__} 遇到不可重试的异常: {e}")
                    raise e
            
            # 理论上不会到达这里，但为了安全起见
            if last_exception and not skip_on_final_failure:
                raise last_exception
                
        return wrapper
    return decorator


def retry_on_http_error(
    max_retries: int = 3,
    delay: float = 1.0,
    retry_status_codes: Tuple[int, ...] = (500, 502, 503, 504),
    skip_on_final_failure: bool = True
):
    """
    专门用于HTTP错误的重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟时间
        retry_status_codes: 需要重试的HTTP状态码
        skip_on_final_failure: 最终失败时是否跳过测试
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import requests
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # 如果返回的是requests.Response对象，检查状态码
                    if hasattr(result, 'status_code'):
                        if result.status_code in retry_status_codes:
                            if attempt < max_retries:
                                logger.warning(
                                    f"HTTP {result.status_code} 错误，第{attempt+1}次重试..."
                                )
                                time.sleep(delay)
                                continue
                            else:
                                if skip_on_final_failure:
                                    pytest.skip(f"HTTP服务不可用 (状态码: {result.status_code})")
                                else:
                                    return result
                    
                    return result
                    
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries:
                        logger.warning(f"网络请求异常，第{attempt+1}次重试: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        if skip_on_final_failure:
                            pytest.skip(f"网络连接问题: {e}")
                        else:
                            raise e
                            
                except Exception as e:
                    logger.error(f"函数 {func.__name__} 遇到异常: {e}")
                    raise e
                    
        return wrapper
    return decorator


def network_dependent_test(
    max_retries: int = 2,
    delay: float = 1.0,
    service_name: str = "外部服务"
):
    """
    标记依赖网络的测试的装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 重试延迟
        service_name: 服务名称，用于错误消息
    """
    return retry_on_failure(
        max_retries=max_retries,
        delay=delay,
        exceptions=(ConnectionError, TimeoutError, OSError),
        skip_on_final_failure=True,
        skip_message=f"{service_name}不可用，跳过网络依赖测试"
    )


# 使用示例
if __name__ == "__main__":
    import requests
    
    @retry_on_http_error(max_retries=3, delay=1.0)
    def test_unreliable_api():
        response = requests.get("https://httpbin.org/status/502")
        return response
    
    @network_dependent_test(service_name="HTTPBin")
    def test_network_service():
        response = requests.get("https://httpbin.org/get")
        assert response.status_code == 200
        return response
    
    # 这些函数在实际使用中会自动重试和跳过
