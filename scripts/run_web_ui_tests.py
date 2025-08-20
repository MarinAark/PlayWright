#!/usr/bin/env python3
"""
Web UI测试运行脚本
专门用于运行和调试Web UI测试用例
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(command, description):
    """运行命令并处理结果"""
    print(f"🚀 {description}")
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
    parser = argparse.ArgumentParser(description="运行Web UI测试")
    parser.add_argument("--headless", action="store_true", help="无头模式运行")
    parser.add_argument("--debug", action="store_true", help="调试模式（有头模式）")
    parser.add_argument("--timeout", type=int, default=60, help="浏览器超时时间（秒）")
    parser.add_argument("--viewport", default="1920x1080", help="浏览器视口大小")
    parser.add_argument("--test", help="运行特定测试")
    parser.add_argument("--clean", action="store_true", help="清理测试结果")
    parser.add_argument("--screenshot", action="store_true", help="启用截图")
    
    args = parser.parse_args()
    
    # 设置环境变量
    if args.headless:
        os.environ["BROWSER_HEADLESS"] = "true"
    elif args.debug:
        os.environ["BROWSER_HEADLESS"] = "false"
    
    os.environ["BROWSER_TIMEOUT"] = str(args.timeout * 1000)  # 转换为毫秒
    
    # 解析视口大小
    try:
        width, height = args.viewport.split("x")
        os.environ["BROWSER_VIEWPORT_WIDTH"] = width
        os.environ["BROWSER_VIEWPORT_HEIGHT"] = height
    except ValueError:
        print("⚠️  视口格式错误，使用默认值 1920x1080")
        os.environ["BROWSER_VIEWPORT_WIDTH"] = "1920"
        os.environ["BROWSER_VIEWPORT_HEIGHT"] = "1080"
    
    # 创建必要的目录
    Path("screenshots").mkdir(exist_ok=True)
    Path("results").mkdir(exist_ok=True)
    
    if args.clean:
        print("🧹 清理测试结果...")
        subprocess.run("rm -rf screenshots/*", shell=True)
        subprocess.run("rm -rf results/*", shell=True)
        subprocess.run("rm -rf .pytest_cache", shell=True)
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装依赖"):
        sys.exit(1)
    
    # 安装Playwright浏览器
    if not run_command("playwright install", "安装Playwright浏览器"):
        sys.exit(1)
    
    # 构建测试命令
    test_command = "pytest"
    
    if args.test:
        test_command += f" {args.test}"
    else:
        test_command += " tests/test_baidu_search.py"
    
    # 添加测试选项
    test_command += " -v --tb=short"
    
    if args.screenshot:
        test_command += " --capture=no"
    
    # 设置环境变量用于调试
    if args.debug:
        os.environ["PYTEST_ADDOPTS"] = "--capture=no --tb=long"
        print("🔍 调试模式已启用")
    
    # 显示配置信息
    print("\n📋 测试配置:")
    print(f"  浏览器模式: {'无头' if args.headless else '有头' if args.debug else '默认'}")
    print(f"  超时时间: {args.timeout}秒")
    print(f"  视口大小: {os.environ['BROWSER_VIEWPORT_WIDTH']}x{os.environ['BROWSER_VIEWPORT_HEIGHT']}")
    print(f"  测试文件: {args.test if args.test else 'tests/test_baidu_search.py'}")
    print(f"  截图功能: {'启用' if args.screenshot else '禁用'}")
    
    # 运行测试
    print(f"\n🧪 开始运行Web UI测试...")
    if not run_command(test_command, "运行Web UI测试"):
        print("\n❌ 测试执行失败")
        print("💡 调试建议:")
        print("1. 使用 --debug 参数查看详细错误信息")
        print("2. 检查网络连接和百度页面可访问性")
        print("3. 查看 screenshots/ 目录中的失败截图")
        print("4. 检查浏览器是否正常启动")
        sys.exit(1)
    
    print("\n🎉 Web UI测试完成!")
    print("\n📁 测试结果:")
    print(f"  截图目录: screenshots/")
    print(f"  结果目录: results/")
    
    if args.debug:
        print("\n💡 调试模式提示:")
        print("  浏览器窗口已打开，可以观察测试执行过程")
        print("  如果测试失败，请检查页面元素和网络状态")

if __name__ == "__main__":
    main()
