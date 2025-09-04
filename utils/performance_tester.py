"""
性能测试工具
支持API性能测试、负载测试和压力测试
"""
import time
import statistics
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        return 100 - self.success_rate
    
    @property
    def total_duration(self) -> float:
        """总耗时（秒）"""
        return self.end_time - self.start_time
    
    @property
    def requests_per_second(self) -> float:
        """每秒请求数"""
        if self.total_duration == 0:
            return 0.0
        return self.total_requests / self.total_duration
    
    @property
    def avg_response_time(self) -> float:
        """平均响应时间（毫秒）"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def min_response_time(self) -> float:
        """最小响应时间（毫秒）"""
        return min(self.response_times) if self.response_times else 0.0
    
    @property
    def max_response_time(self) -> float:
        """最大响应时间（毫秒）"""
        return max(self.response_times) if self.response_times else 0.0
    
    @property
    def median_response_time(self) -> float:
        """中位数响应时间（毫秒）"""
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)
    
    @property
    def percentile_95_response_time(self) -> float:
        """95百分位响应时间（毫秒）"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)]
    
    @property
    def percentile_99_response_time(self) -> float:
        """99百分位响应时间（毫秒）"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[min(index, len(sorted_times) - 1)]


class PerformanceTester:
    """性能测试器"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = None
        self.metrics = PerformanceMetrics()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送单个HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response_time = (time.time() - start_time) * 1000  # 转换为毫秒
                response_data = await response.text()
                
                return {
                    'success': True,
                    'status_code': response.status,
                    'response_time': response_time,
                    'response_data': response_data,
                    'error': None
                }
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'status_code': 0,
                'response_time': response_time,
                'response_data': None,
                'error': str(e)
            }
    
    async def _run_concurrent_requests(
        self,
        method: str,
        endpoint: str,
        concurrent_users: int,
        requests_per_user: int,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        ramp_up_time: int = 0
    ) -> PerformanceMetrics:
        """运行并发请求测试"""
        
        async def user_requests(user_id: int):
            """单个用户的请求任务"""
            # 渐进加载：根据用户ID延迟启动
            if ramp_up_time > 0:
                delay = (user_id / concurrent_users) * ramp_up_time
                await asyncio.sleep(delay)
            
            user_metrics = PerformanceMetrics()
            
            for _ in range(requests_per_user):
                result = await self._make_request(method, endpoint, headers, data, params)
                
                user_metrics.total_requests += 1
                user_metrics.response_times.append(result['response_time'])
                
                if result['success'] and 200 <= result['status_code'] < 400:
                    user_metrics.successful_requests += 1
                else:
                    user_metrics.failed_requests += 1
                    if result['error']:
                        user_metrics.error_messages.append(result['error'])
            
            return user_metrics
        
        # 创建会话
        connector = aiohttp.TCPConnector(limit=concurrent_users * 2)
        self.session = aiohttp.ClientSession(connector=connector)
        
        try:
            # 记录开始时间
            self.metrics.start_time = time.time()
            
            # 创建并发任务
            tasks = [user_requests(i) for i in range(concurrent_users)]
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 记录结束时间
            self.metrics.end_time = time.time()
            
            # 合并结果
            for result in results:
                if isinstance(result, PerformanceMetrics):
                    self.metrics.total_requests += result.total_requests
                    self.metrics.successful_requests += result.successful_requests
                    self.metrics.failed_requests += result.failed_requests
                    self.metrics.response_times.extend(result.response_times)
                    self.metrics.error_messages.extend(result.error_messages)
                else:
                    logger.error(f"任务异常: {result}")
            
            return self.metrics
            
        finally:
            await self.session.close()
    
    async def load_test(
        self,
        method: str,
        endpoint: str,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        ramp_up_time: int = 0
    ) -> PerformanceMetrics:
        """
        负载测试
        
        Args:
            method: HTTP方法
            endpoint: 接口端点
            concurrent_users: 并发用户数
            requests_per_user: 每个用户的请求数
            headers: 请求头
            data: 请求数据
            params: 请求参数
            ramp_up_time: 渐进加载时间（秒）
            
        Returns:
            性能指标
        """
        logger.info(f"开始负载测试: {concurrent_users} 并发用户，每用户 {requests_per_user} 请求")
        
        metrics = await self._run_concurrent_requests(
            method, endpoint, concurrent_users, requests_per_user,
            headers, data, params, ramp_up_time
        )
        
        logger.info(f"负载测试完成: 总请求 {metrics.total_requests}，成功率 {metrics.success_rate:.2f}%")
        return metrics
    
    async def stress_test(
        self,
        method: str,
        endpoint: str,
        max_users: int = 100,
        step_size: int = 10,
        step_duration: int = 60,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> List[PerformanceMetrics]:
        """
        压力测试（逐步增加负载）
        
        Args:
            method: HTTP方法
            endpoint: 接口端点
            max_users: 最大用户数
            step_size: 每步增加的用户数
            step_duration: 每步持续时间（秒）
            headers: 请求头
            data: 请求数据
            params: 请求参数
            
        Returns:
            各阶段的性能指标列表
        """
        results = []
        
        for users in range(step_size, max_users + 1, step_size):
            logger.info(f"压力测试阶段: {users} 并发用户")
            
            # 计算每个用户的请求数（基于持续时间）
            requests_per_user = max(1, step_duration // 2)
            
            metrics = await self._run_concurrent_requests(
                method, endpoint, users, requests_per_user,
                headers, data, params
            )
            
            results.append(metrics)
            
            # 检查是否达到系统极限
            if metrics.success_rate < 95:  # 成功率低于95%认为达到极限
                logger.warning(f"系统达到压力极限，成功率: {metrics.success_rate:.2f}%")
                break
        
        return results
    
    def generate_report(self, metrics: PerformanceMetrics, output_file: Optional[str] = None) -> str:
        """
        生成性能测试报告
        
        Args:
            metrics: 性能指标
            output_file: 输出文件路径
            
        Returns:
            报告内容
        """
        report = f"""
性能测试报告
============

测试概览:
- 总请求数: {metrics.total_requests}
- 成功请求: {metrics.successful_requests}
- 失败请求: {metrics.failed_requests}
- 成功率: {metrics.success_rate:.2f}%
- 失败率: {metrics.failure_rate:.2f}%
- 测试耗时: {metrics.total_duration:.2f} 秒
- 请求速率: {metrics.requests_per_second:.2f} req/s

响应时间统计 (毫秒):
- 平均响应时间: {metrics.avg_response_time:.2f}
- 最小响应时间: {metrics.min_response_time:.2f}
- 最大响应时间: {metrics.max_response_time:.2f}
- 中位数响应时间: {metrics.median_response_time:.2f}
- 95%响应时间: {metrics.percentile_95_response_time:.2f}
- 99%响应时间: {metrics.percentile_99_response_time:.2f}

错误信息:
"""
        
        # 添加错误统计
        if metrics.error_messages:
            error_counts = {}
            for error in metrics.error_messages:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                report += f"- {error}: {count} 次\n"
        else:
            report += "- 无错误\n"
        
        # 保存到文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # 同时保存JSON格式的详细数据
            json_file = output_path.with_suffix('.json')
            json_data = {
                'total_requests': metrics.total_requests,
                'successful_requests': metrics.successful_requests,
                'failed_requests': metrics.failed_requests,
                'success_rate': metrics.success_rate,
                'total_duration': metrics.total_duration,
                'requests_per_second': metrics.requests_per_second,
                'avg_response_time': metrics.avg_response_time,
                'min_response_time': metrics.min_response_time,
                'max_response_time': metrics.max_response_time,
                'median_response_time': metrics.median_response_time,
                'percentile_95_response_time': metrics.percentile_95_response_time,
                'percentile_99_response_time': metrics.percentile_99_response_time,
                'response_times': metrics.response_times,
                'error_messages': metrics.error_messages
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"报告已保存: {output_file} 和 {json_file}")
        
        return report


class PerformanceTestSuite:
    """性能测试套件"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.test_cases = []
    
    def add_test_case(
        self,
        name: str,
        method: str,
        endpoint: str,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ):
        """添加测试用例"""
        self.test_cases.append({
            'name': name,
            'method': method,
            'endpoint': endpoint,
            'concurrent_users': concurrent_users,
            'requests_per_user': requests_per_user,
            'headers': headers,
            'data': data,
            'params': params
        })
    
    async def run_all_tests(self, output_dir: str = "performance_results") -> Dict[str, PerformanceMetrics]:
        """运行所有测试用例"""
        results = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for test_case in self.test_cases:
            logger.info(f"运行测试用例: {test_case['name']}")
            
            tester = PerformanceTester(self.base_url)
            
            metrics = await tester.load_test(
                method=test_case['method'],
                endpoint=test_case['endpoint'],
                concurrent_users=test_case['concurrent_users'],
                requests_per_user=test_case['requests_per_user'],
                headers=test_case['headers'],
                data=test_case['data'],
                params=test_case['params']
            )
            
            results[test_case['name']] = metrics
            
            # 生成单个测试报告
            report_file = output_path / f"{test_case['name']}.txt"
            tester.generate_report(metrics, str(report_file))
        
        # 生成汇总报告
        self._generate_summary_report(results, output_path / "summary.txt")
        
        return results
    
    def _generate_summary_report(self, results: Dict[str, PerformanceMetrics], output_file: Path):
        """生成汇总报告"""
        summary = "性能测试汇总报告\n"
        summary += "=" * 50 + "\n\n"
        
        for name, metrics in results.items():
            summary += f"{name}:\n"
            summary += f"  成功率: {metrics.success_rate:.2f}%\n"
            summary += f"  平均响应时间: {metrics.avg_response_time:.2f}ms\n"
            summary += f"  请求速率: {metrics.requests_per_second:.2f} req/s\n"
            summary += f"  总请求数: {metrics.total_requests}\n\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"汇总报告已保存: {output_file}")
