#!/bin/bash

# Jenkins服务器上安装Allure命令行工具的脚本
# 适用于Ubuntu/Debian系统

set -e

echo "🚀 开始安装Allure命令行工具..."

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  检测到root用户，建议使用普通用户运行此脚本"
fi

# 检查系统类型
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ 检测到Linux系统"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ 检测到macOS系统"
else
    echo "❌ 不支持的操作系统: $OSTYPE"
    exit 1
fi

# 安装Java (Allure需要Java 8+)
echo "📦 检查Java环境..."
if ! command -v java &> /dev/null; then
    echo "📥 安装Java..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y openjdk-11-jdk
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install openjdk@11
    fi
else
    echo "✅ Java已安装: $(java -version 2>&1 | head -n 1)"
fi

# 下载并安装Allure
echo "📥 下载Allure..."
ALLURE_VERSION="2.24.1"
ALLURE_DIR="/opt/allure"
ALLURE_BIN="/usr/local/bin/allure"

# 创建安装目录
sudo mkdir -p $ALLURE_DIR

# 下载Allure
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    wget -O /tmp/allure-$ALLURE_VERSION.tgz "https://github.com/allure-framework/allure2/releases/download/$ALLURE_VERSION/allure-$ALLURE_VERSION.tgz"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    curl -L -o /tmp/allure-$ALLURE_VERSION.tgz "https://github.com/allure-framework/allure2/releases/download/$ALLURE_VERSION/allure-$ALLURE_VERSION.tgz"
fi

# 解压并安装
echo "📦 解压Allure..."
sudo tar -xzf /tmp/allure-$ALLURE_VERSION.tgz -C $ALLURE_DIR --strip-components=1

# 创建软链接
echo "🔗 创建软链接..."
sudo ln -sf $ALLURE_DIR/bin/allure $ALLURE_BIN

# 设置权限
sudo chmod +x $ALLURE_BIN

# 清理临时文件
rm -f /tmp/allure-$ALLURE_VERSION.tgz

# 验证安装
echo "✅ 验证Allure安装..."
if command -v allure &> /dev/null; then
    echo "🎉 Allure安装成功！"
    echo "📊 版本信息:"
    allure --version
    echo ""
    echo "📍 安装路径: $ALLURE_DIR"
    echo "🔗 可执行文件: $ALLURE_BIN"
    echo ""
    echo "📋 在Jenkins中配置Allure:"
    echo "1. 进入 'Manage Jenkins' → 'Configure System'"
    echo "2. 找到 'Allure Commandline' 部分"
    echo "3. 添加配置："
    echo "   - Name: Allure"
    echo "   - Home: $ALLURE_DIR"
    echo ""
    echo "🎯 现在可以在Jenkins中使用Allure生成测试报告了！"
else
    echo "❌ Allure安装失败"
    exit 1
fi
