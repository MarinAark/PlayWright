"""
性能测试示例
展示如何使用性能测试工具进行API性能测试
"""
import pytest
import allure
import asyncio
from utils.performance_tester import PerformanceTester, PerformanceTestSuite
from config.config_manager import get_config


@allure.epic("性能测试")
@allure.feature("API性能")
class TestAPIPerformance:
    """API性能测试类"""
    
    @pytest.fixture(scope="class")
    def performance_tester(self):
        """性能测试器fixture"""
        config = get_config()
        return PerformanceTester(
            base_url=config.api.base_url,
            timeout=config.api.timeout
        )
    
    @allure.story("基础负载测试")
    @pytest.mark.asyncio
    async def test_basic_load_test(self, performance_tester):
        """基础负载测试"""
        
        with allure.step("执行负载测试"):
            metrics = await performance_tester.load_test(
                method="GET",
                endpoint="/get",
                concurrent_users=5,
                requests_per_user=10
            )
        
        with allure.step("验证性能指标"):
            # 验证成功率
            assert metrics.success_rate >= 95.0, f"成功率过低: {metrics.success_rate:.2f}%"
            
            # 验证平均响应时间
            config = get_config()
            max_response_time = config.performance.max_response_time_ms
            assert metrics.avg_response_time <= max_response_time, \
                f"平均响应时间过高: {metrics.avg_response_time:.2f}ms"
            
            # 验证请求速率
            assert metrics.requests_per_second > 0, "请求速率应该大于0"
            
            allure.attach(
                f"总请求数: {metrics.total_requests}\n"
                f"成功率: {metrics.success_rate:.2f}%\n"
                f"平均响应时间: {metrics.avg_response_time:.2f}ms\n"
                f"请求速率: {metrics.requests_per_second:.2f} req/s",
                "性能指标",
                allure.attachment_type.TEXT
            )
        
        with allure.step("生成性能报告"):
            report = performance_tester.generate_report(
                metrics, 
                "performance_results/basic_load_test.txt"
            )
            allure.attach(report, "详细性能报告", allure.attachment_type.TEXT)
    
    @allure.story("POST请求性能测试")
    @pytest.mark.asyncio
    async def test_post_performance(self, performance_tester):
        """POST请求性能测试"""
        
        test_data = {
            "name": "performance_test",
            "data": "test_data_" * 100  # 增加数据大小
        }
        
        with allure.step("执行POST请求性能测试"):
            metrics = await performance_tester.load_test(
                method="POST",
                endpoint="/post",
                concurrent_users=3,
                requests_per_user=5,
                data=test_data
            )
        
        with allure.step("验证POST性能"):
            # POST请求通常比GET请求慢，适当调整期望值
            assert metrics.success_rate >= 90.0, f"POST成功率过低: {metrics.success_rate:.2f}%"
            
            # POST请求的响应时间限制可以更宽松
            assert metrics.avg_response_time <= 10000.0, \
                f"POST平均响应时间过高: {metrics.avg_response_time:.2f}ms"
            
            allure.attach(
                f"POST请求性能统计:\n"
                f"总请求数: {metrics.total_requests}\n"
                f"成功率: {metrics.success_rate:.2f}%\n"
                f"平均响应时间: {metrics.avg_response_time:.2f}ms\n"
                f"95%响应时间: {metrics.percentile_95_response_time:.2f}ms",
                "POST性能指标",
                allure.attachment_type.TEXT
            )
    
    @allure.story("并发用户扩展测试")
    @pytest.mark.asyncio
    async def test_concurrent_users_scaling(self, performance_tester):
        """测试不同并发用户数下的性能表现"""
        
        user_counts = [1, 5, 10, 20]
        results = {}
        
        for user_count in user_counts:
            with allure.step(f"测试{user_count}个并发用户"):
                metrics = await performance_tester.load_test(
                    method="GET",
                    endpoint="/get",
                    concurrent_users=user_count,
                    requests_per_user=5
                )
                
                results[user_count] = {
                    'success_rate': metrics.success_rate,
                    'avg_response_time': metrics.avg_response_time,
                    'requests_per_second': metrics.requests_per_second
                }
        
        with allure.step("分析扩展性"):
            # 生成扩展性报告
            scaling_report = "并发用户扩展性测试结果:\n"
            scaling_report += "用户数\t成功率\t平均响应时间\t请求速率\n"
            
            for user_count, metrics in results.items():
                scaling_report += f"{user_count}\t{metrics['success_rate']:.2f}%\t"
                scaling_report += f"{metrics['avg_response_time']:.2f}ms\t"
                scaling_report += f"{metrics['requests_per_second']:.2f} req/s\n"
            
            allure.attach(scaling_report, "扩展性分析", allure.attachment_type.TEXT)
            
            # 验证扩展性：成功率不应随用户数增加而显著下降
            success_rates = [results[count]['success_rate'] for count in user_counts]
            min_success_rate = min(success_rates)
            assert min_success_rate >= 90.0, f"在高并发下成功率过低: {min_success_rate:.2f}%"
    
    @allure.story("响应时间分布分析")
    @pytest.mark.asyncio
    async def test_response_time_distribution(self, performance_tester):
        """分析响应时间分布"""
        
        with allure.step("收集响应时间数据"):
            metrics = await performance_tester.load_test(
                method="GET",
                endpoint="/delay/1",  # 1秒延迟的端点
                concurrent_users=10,
                requests_per_user=10
            )
        
        with allure.step("分析响应时间分布"):
            response_times = metrics.response_times
            
            # 计算统计信息
            import statistics
            
            stats = {
                '最小值': min(response_times),
                '最大值': max(response_times),
                '平均值': statistics.mean(response_times),
                '中位数': statistics.median(response_times),
                '标准差': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                '95百分位': metrics.percentile_95_response_time,
                '99百分位': metrics.percentile_99_response_time
            }
            
            distribution_report = "响应时间分布统计 (毫秒):\n"
            for key, value in stats.items():
                distribution_report += f"{key}: {value:.2f}\n"
            
            allure.attach(distribution_report, "响应时间分布", allure.attachment_type.TEXT)
            
            # 验证响应时间的一致性（标准差不应过大）
            cv = stats['标准差'] / stats['平均值'] if stats['平均值'] > 0 else 0  # 变异系数
            assert cv <= 0.5, f"响应时间变异过大，变异系数: {cv:.2f}"


@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceTestSuite:
    """性能测试套件示例"""
    
    @allure.story("性能测试套件")
    @pytest.mark.asyncio
    async def test_performance_suite(self):
        """运行完整的性能测试套件"""
        
        config = get_config()
        suite = PerformanceTestSuite(config.api.base_url)
        
        with allure.step("配置测试用例"):
            # 添加不同的测试用例
            suite.add_test_case(
                name="get_endpoint_test",
                method="GET",
                endpoint="/get",
                concurrent_users=5,
                requests_per_user=10
            )
            
            suite.add_test_case(
                name="post_endpoint_test",
                method="POST",
                endpoint="/post",
                concurrent_users=3,
                requests_per_user=5,
                data={"test": "data"}
            )
            
            suite.add_test_case(
                name="json_endpoint_test",
                method="GET",
                endpoint="/json",
                concurrent_users=8,
                requests_per_user=8
            )
        
        with allure.step("执行性能测试套件"):
            results = await suite.run_all_tests("performance_results/suite_results")
        
        with allure.step("验证套件结果"):
            assert len(results) == 3, f"期望3个测试结果，实际{len(results)}个"
            
            # 验证所有测试的成功率
            for test_name, metrics in results.items():
                assert metrics.success_rate >= 90.0, \
                    f"测试{test_name}成功率过低: {metrics.success_rate:.2f}%"
            
            # 生成汇总报告
            summary_report = "性能测试套件汇总:\n"
            for test_name, metrics in results.items():
                summary_report += f"\n{test_name}:\n"
                summary_report += f"  成功率: {metrics.success_rate:.2f}%\n"
                summary_report += f"  平均响应时间: {metrics.avg_response_time:.2f}ms\n"
                summary_report += f"  请求速率: {metrics.requests_per_second:.2f} req/s\n"
            
            allure.attach(summary_report, "套件汇总报告", allure.attachment_type.TEXT)


@pytest.mark.performance
@pytest.mark.stress
class TestStressTest:
    """压力测试示例"""
    
    @allure.story("压力测试")
    @pytest.mark.asyncio
    async def test_stress_test(self):
        """执行压力测试，找到系统性能极限"""
        
        config = get_config()
        tester = PerformanceTester(config.api.base_url)
        
        with allure.step("执行压力测试"):
            # 从5个用户开始，每次增加5个，最多到30个用户
            stress_results = await tester.stress_test(
                method="GET",
                endpoint="/get",
                max_users=30,
                step_size=5,
                step_duration=30  # 每个阶段持续30秒
            )
        
        with allure.step("分析压力测试结果"):
            stress_report = "压力测试结果分析:\n"
            stress_report += "用户数\t成功率\t平均响应时间\t请求速率\n"
            
            breaking_point = None
            
            for i, metrics in enumerate(stress_results):
                user_count = (i + 1) * 5
                stress_report += f"{user_count}\t{metrics.success_rate:.2f}%\t"
                stress_report += f"{metrics.avg_response_time:.2f}ms\t"
                stress_report += f"{metrics.requests_per_second:.2f} req/s\n"
                
                # 找到性能拐点
                if metrics.success_rate < 95.0 and breaking_point is None:
                    breaking_point = user_count
            
            if breaking_point:
                stress_report += f"\n系统性能拐点: {breaking_point} 并发用户\n"
            else:
                stress_report += f"\n在测试范围内未达到性能极限\n"
            
            allure.attach(stress_report, "压力测试分析", allure.attachment_type.TEXT)
            
            # 验证系统在一定负载下仍能正常工作
            first_stage_metrics = stress_results[0]  # 第一阶段（5用户）的结果
            assert first_stage_metrics.success_rate >= 99.0, \
                f"低负载下成功率不达标: {first_stage_metrics.success_rate:.2f}%"
