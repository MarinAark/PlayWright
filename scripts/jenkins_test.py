#!/usr/bin/env python3
"""
Jenkins专用测试执行脚本
解决CI/CD环境中的兼容性问题
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """检查测试环境"""
    logger.info("🔍 检查测试环境...")
    
    # 检查Python版本
    python_version = sys.version
    logger.info(f"Python版本: {python_version}")
    
    # 检查必要的包
    required_packages = ['pytest', 'playwright', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} 未安装")
    
    # 检查可选包
    optional_packages = {
        'allure': 'allure-pytest',
        'pytest_html': 'pytest-html',
        'yaml': 'PyYAML',
        'pandas': 'pandas'
    }
    
    for module, package in optional_packages.items():
        try:
            __import__(module)
            logger.info(f"✅ {package} 已安装（可选）")
        except ImportError:
            logger.info(f"⚠️ {package} 未安装（可选）")
    
    return len(missing_packages) == 0

def run_basic_tests():
    """运行基础测试"""
    logger.info("🚀 运行基础测试...")
    
    cmd = [
        'python3', '-m', 'pytest', 
        'tests/', 
        '-v', 
        '--tb=short',
        '--maxfail=10'  # 最多失败10个就停止
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 总超时30分钟
        
        logger.info("📊 测试执行完成")
        logger.info(f"返回码: {result.returncode}")
        
        if result.stdout:
            logger.info("标准输出:")
            print(result.stdout)
        
        if result.stderr:
            logger.warning("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("❌ 测试执行超时")
        return False
    except Exception as e:
        logger.error(f"❌ 测试执行异常: {e}")
        return False

def run_tests_with_reports():
    """运行测试并生成报告"""
    logger.info("📊 运行测试并生成报告...")
    
    # 确保结果目录存在
    os.makedirs('results', exist_ok=True)
    os.makedirs('results/allure-results', exist_ok=True)
    
    # 构建命令
    cmd = ['python3', '-m', 'pytest', 'tests/', '-v', '--tb=short']
    
    # 检查是否可以使用allure
    try:
        import allure
        cmd.extend(['--alluredir=results/allure-results'])
        logger.info("✅ 将生成Allure报告")
    except ImportError:
        logger.info("⚠️ Allure不可用，跳过Allure报告")
    
    # 检查是否可以使用pytest-html
    try:
        import pytest_html
        cmd.extend(['--html=results/report.html', '--self-contained-html'])
        logger.info("✅ 将生成HTML报告")
    except ImportError:
        logger.info("⚠️ pytest-html不可用，跳过HTML报告")
    
    try:
        result = subprocess.run(cmd, timeout=1800)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        logger.error("❌ 报告生成超时")
        return False
    except Exception as e:
        logger.error(f"❌ 报告生成异常: {e}")
        return False

def generate_test_summary():
    """生成测试摘要"""
    logger.info("📋 生成测试摘要...")
    
    summary = {
        "timestamp": str(subprocess.check_output(['date'], text=True).strip()),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "PATH": os.environ.get("PATH", ""),
            "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        }
    }
    
    # 保存摘要
    with open('results/test_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info("✅ 测试摘要已保存到 results/test_summary.json")

def main():
    """主函数"""
    logger.info("🎯 开始Jenkins测试执行...")
    
    # 检查环境
    if not check_environment():
        logger.error("❌ 环境检查失败，某些必要的包未安装")
        return 1
    
    # 运行基础测试
    basic_success = run_basic_tests()
    if not basic_success:
        logger.error("❌ 基础测试失败")
        return 1
    
    # 生成报告
    report_success = run_tests_with_reports()
    if not report_success:
        logger.warning("⚠️ 报告生成可能有问题，但基础测试通过")
    
    # 生成摘要
    generate_test_summary()
    
    logger.info("🎉 Jenkins测试执行完成！")
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
