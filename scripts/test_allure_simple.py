#!/usr/bin/env python3
"""
简单的Allure测试脚本
用于验证Jenkins中的Allure报告生成
"""

import pytest
import allure
import time
import os

@allure.epic("Jenkins集成测试")
@allure.feature("Allure报告生成")
class TestAllureGeneration:
    
    @allure.story("基础测试")
    @allure.severity(allure.severity_level.NORMAL)
    def test_basic_functionality(self):
        """基础功能测试"""
        with allure.step("执行基础测试"):
            assert 1 + 1 == 2
            allure.attach("测试结果", "基础测试通过", allure.attachment_type.TEXT)
    
    @allure.story("参数化测试")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("input_value,expected", [
        (1, 1),
        (2, 4),
        (3, 9)
    ])
    def test_parameterized(self, input_value, expected):
        """参数化测试"""
        with allure.step(f"测试输入值 {input_value}"):
            result = input_value ** 2
            assert result == expected
            allure.attach(
                f"输入: {input_value}, 期望: {expected}, 实际: {result}",
                "参数化测试结果",
                allure.attachment_type.TEXT
            )
    
    @allure.story("失败测试")
    @allure.severity(allure.severity_level.MINOR)
    def test_expected_failure(self):
        """预期失败的测试"""
        with allure.step("执行预期失败的测试"):
            # 这个测试会失败，用于验证Allure如何处理失败用例
            assert False, "这是预期的失败"
    
    @allure.story("长时间运行测试")
    @allure.severity(allure.severity_level.LOW)
    def test_long_running(self):
        """长时间运行的测试"""
        with allure.step("开始长时间运行测试"):
            time.sleep(2)  # 模拟长时间运行
            with allure.step("执行计算"):
                result = sum(range(1000))
                assert result == 499500
            allure.attach(f"计算结果: {result}", "长时间运行测试完成", allure.attachment_type.TEXT)

@allure.epic("系统信息")
@allure.feature("环境检查")
class TestEnvironment:
    
    @allure.story("Python环境")
    def test_python_environment(self):
        """检查Python环境"""
        import sys
        import platform
        
        with allure.step("获取Python版本"):
            python_version = sys.version
            allure.attach(python_version, "Python版本信息", allure.attachment_type.TEXT)
        
        with allure.step("获取平台信息"):
            platform_info = platform.platform()
            allure.attach(platform_info, "平台信息", allure.attachment_type.TEXT)
        
        with allure.step("获取当前目录"):
            current_dir = os.getcwd()
            allure.attach(current_dir, "当前工作目录", allure.attachment_type.TEXT)
        
        assert True  # 环境检查总是通过
    
    @allure.story("文件系统")
    def test_file_system(self):
        """检查文件系统"""
        with allure.step("检查当前目录文件"):
            files = os.listdir('.')
            allure.attach(str(files), "当前目录文件列表", allure.attachment_type.TEXT)
        
        with allure.step("检查results目录"):
            if os.path.exists('results'):
                results_files = os.listdir('results')
                allure.attach(str(results_files), "results目录内容", allure.attachment_type.TEXT)
            else:
                allure.attach("results目录不存在", "目录状态", allure.attachment_type.TEXT)
        
        assert True  # 文件系统检查总是通过

if __name__ == "__main__":
    # 直接运行时的配置
    pytest.main([
        __file__,
        "-v",
        "--alluredir=results/allure-results",
        "--tb=short"
    ])
