#!/bin/bash

# 本地测试Allure报告生成的脚本
# 用于验证Jenkins配置前的本地测试

set -e

echo "🧪 开始本地Allure报告生成测试..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip install -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install

# 清理之前的测试结果
echo "🧹 清理之前的测试结果..."
rm -rf results/
rm -rf screenshots/
mkdir -p results
mkdir -p screenshots

# 运行测试
echo "🚀 运行测试用例..."
pytest tests/ -v --alluredir=results/allure-results --html=results/report.html --self-contained-html

# 检查Allure结果
echo "📊 检查Allure结果..."
if [ -d "results/allure-results" ]; then
    echo "✅ Allure结果目录已生成"
    ls -la results/allure-results/
    
    # 尝试生成Allure报告
    if command -v allure &> /dev/null; then
        echo "📈 生成Allure报告..."
        allure generate results/allure-results --clean -o results/allure-report
        
        if [ -d "results/allure-report" ]; then
            echo "🎉 Allure报告生成成功！"
            echo "📍 报告位置: results/allure-report/"
            echo "🌐 查看报告: allure open results/allure-results"
        else
            echo "❌ Allure报告生成失败"
        fi
    else
        echo "⚠️  Allure命令行工具未安装，跳过报告生成"
        echo "💡 可以使用以下命令安装Allure:"
        echo "   brew install allure (macOS)"
        echo "   或运行: scripts/install_allure_jenkins.sh"
    fi
else
    echo "❌ Allure结果目录未生成"
    exit 1
fi

# 检查HTML报告
echo "📄 检查HTML报告..."
if [ -f "results/report.html" ]; then
    echo "✅ HTML报告已生成: results/report.html"
    echo "📏 文件大小: $(du -h results/report.html | cut -f1)"
else
    echo "❌ HTML报告未生成"
fi

# 检查测试数据
echo "📁 检查测试数据..."
if [ -d "test_data" ]; then
    echo "✅ 测试数据目录存在"
    ls -la test_data/
else
    echo "❌ 测试数据目录不存在"
fi

echo ""
echo "🎯 本地测试完成！"
echo "📋 如果所有检查都通过，说明Jenkins配置应该能正常工作"
echo "🚀 现在可以将代码推送到Git并配置Jenkins任务了"
