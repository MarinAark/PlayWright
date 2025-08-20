#!/usr/bin/env python3
"""
API测试运行脚本
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并处理结果"""
    print(f"\n🚀 {description}")
    print(f"执行命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print("标准输出:", e.stdout)
        if e.stderr:
            print("错误输出:", e.stderr)
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行API测试")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="test", 
                       help="测试环境 (默认: test)")
    parser.add_argument("--markers", help="运行特定标记的测试")
    parser.add_argument("--parallel", action="store_true", help="并行运行测试")
    parser.add_argument("--html", action="store_true", help="生成HTML报告")
    parser.add_argument("--allure", action="store_true", help="生成Allure报告")
    parser.add_argument("--clean", action="store_true", help="清理测试结果")
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["API_ENV"] = args.env
    print(f"🌍 测试环境: {args.env}")
    
    # 创建必要的目录
    Path("test_data").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    
    # 清理测试结果
    if args.clean:
        print("\n🧹 清理测试结果...")
        subprocess.run("rm -rf results/*", shell=True)
        subprocess.run("rm -rf .pytest_cache", shell=True)
        print("✅ 清理完成")
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装依赖"):
        print("❌ 依赖安装失败，请检查 requirements.txt 文件")
        sys.exit(1)
    
    # 构建测试命令
    test_command = "pytest tests/ -v"
    
    if args.markers:
        test_command += f" -m {args.markers}"
    
    if args.parallel:
        test_command += " -n auto"
    
    if args.html:
        test_command += " --html=results/report.html --self-contained-html"
    
    if args.allure:
        test_command += " --alluredir=results/allure-results"
    
    # 运行测试
    if not run_command(test_command, "运行API测试"):
        print("❌ 测试执行失败")
        sys.exit(1)
    
    # 生成Allure报告
    if args.allure:
        allure_command = "allure serve results/allure-results"
        print(f"\n📊 生成Allure报告...")
        print(f"执行命令: {allure_command}")
        print("请在浏览器中查看报告")
    
    # 显示结果文件位置
    print("\n📁 测试结果文件位置:")
    if args.html:
        print(f"  HTML报告: results/report.html")
    if args.allure:
        print(f"  Allure结果: results/allure-results/")
    print(f"  日志文件: 控制台输出")
    
    print("\n🎉 API测试完成!")

if __name__ == "__main__":
    main()
