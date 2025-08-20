# Jenkins 系统配置指南

## 🎯 配置目标
确保Jenkins能正确生成Allure测试报告

## 📋 必需的Jenkins插件

### 核心插件
1. **Allure Jenkins Plugin** - 生成Allure测试报告
2. **HTML Publisher Plugin** - 发布HTML测试报告
3. **Email Extension Plugin** - 发送邮件通知
4. **Git Plugin** - Git代码管理
5. **Pipeline Plugin** - 流水线支持
6. **Workspace Cleanup Plugin** - 工作空间清理

### 安装步骤
1. 登录Jenkins管理界面
2. 进入 "Manage Jenkins" → "Manage Plugins"
3. 在 "Available" 标签页搜索并安装上述插件
4. 重启Jenkins

## ⚙️ 系统配置

### 1. 配置Allure命令行工具

#### 步骤
1. 进入 "Manage Jenkins" → "Configure System"
2. 找到 "Allure Commandline" 部分
3. 点击 "Add Allure Commandline"
4. 填写配置信息：
   - **Name**: `Allure`
   - **Home**: `/opt/allure` (或您的Allure安装路径)

#### 配置示例
```
Name: Allure
Home: /opt/allure
```

### 2. 配置邮件服务器

#### 步骤
1. 进入 "Manage Jenkins" → "Configure System"
2. 找到 "Extended E-mail Notification" 部分
3. 填写SMTP服务器信息：
   - **SMTP server**: `smtp.gmail.com` (或其他SMTP服务器)
   - **SMTP Port**: `587` (或 `465`)
   - **User Name**: `your-email@gmail.com`
   - **Password**: `your-app-password`
   - **Use SSL**: 勾选
   - **Use TLS**: 勾选

#### 配置示例
```
SMTP server: smtp.gmail.com
SMTP Port: 587
User Name: your-email@gmail.com
Password: your-app-password
Use SSL: ✓
Use TLS: ✓
```

### 3. 配置全局工具

#### Python配置
1. 进入 "Manage Jenkins" → "Global Tool Configuration"
2. 找到 "Python installations" 部分
3. 添加Python安装：
   - **Name**: `Python3`
   - **Home**: `/usr/bin/python3` (或您的Python路径)

#### Git配置
1. 在 "Global Tool Configuration" 中找到 "Git installations"
2. 添加Git安装：
   - **Name**: `Default`
   - **Home**: `/usr/bin/git` (或您的Git路径)

## 🔧 环境变量配置

### 系统环境变量
在Jenkins服务器上设置以下环境变量：

```bash
# Python环境
export PYTHON_VERSION=3.8
export VENV_DIR=.venv

# Allure环境
export ALLURE_RESULTS=results/allure-results
export ALLURE_HOME=/opt/allure

# 测试环境
export API_ENV=test
export BROWSER_HEADLESS=true
```

### Jenkins环境变量
在Jenkins任务中添加环境变量：

```groovy
environment {
    VENV_DIR = '.venv'
    ALLURE_RESULTS = 'results/allure-results'
    PYTHON_VERSION = '3.8'
    API_ENV = 'test'
    BROWSER_HEADLESS = 'true'
}
```

## 📊 验证配置

### 1. 检查Allure安装
在Jenkins服务器上运行：
```bash
allure --version
```

### 2. 检查Python环境
```bash
python3 --version
pip3 --version
```

### 3. 检查Git配置
```bash
git --version
```

### 4. 测试邮件发送
在Jenkins中配置测试邮件地址，发送测试邮件验证配置是否正确。

## 🚨 常见问题

### 问题1: Allure报告未生成
**原因**: Allure命令行工具未正确配置
**解决**: 检查系统配置中的Allure路径是否正确

### 问题2: 邮件发送失败
**原因**: SMTP服务器配置错误
**解决**: 检查邮件服务器配置和认证信息

### 问题3: Python环境问题
**原因**: Python路径配置错误
**解决**: 检查Python安装路径和权限

### 问题4: Git认证失败
**原因**: Git凭据配置错误
**解决**: 检查Git凭据ID和权限设置

## 📞 获取帮助

如果遇到配置问题：
1. 检查Jenkins系统日志
2. 查看构建控制台输出
3. 验证所有必需插件已安装
4. 确认系统配置正确
5. 参考详细的配置指南：`docs/JENKINS_SETUP.md`
