# Jenkins 集成配置指南

## 🎯 目标
确保Jenkins能正确运行测试并生成Allure测试报告

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

## ⚙️ Jenkins系统配置

### 1. 配置Allure命令行工具
1. 进入 "Manage Jenkins" → "Configure System"
2. 找到 "Allure Commandline" 部分
3. 添加Allure安装路径：
   - **Name**: `Allure`
   - **Home**: `/usr/local/bin/allure` 或 `/opt/allure/bin/allure`

### 2. 配置邮件服务器
1. 进入 "Manage Jenkins" → "Configure System"
2. 找到 "Extended E-mail Notification" 部分
3. 配置SMTP服务器信息

### 3. 配置Python环境
1. 确保Jenkins服务器已安装Python 3.8+
2. 确保Jenkins用户有权限创建虚拟环境

## 🚀 创建Jenkins任务

### 1. 新建流水线任务
1. 点击 "New Item"
2. 选择 "Pipeline"
3. 输入任务名称，如：`playwright-api-test`

### 2. 配置流水线
1. 在 "Pipeline" 部分选择 "Pipeline script from SCM"
2. **Repository URL**: 输入您的Git仓库地址
3. **Credentials**: 选择Git认证信息
4. **Branch Specifier**: `*/main` 或 `*/master`
5. **Script Path**: `Jenkinsfile`

### 3. 配置构建触发器
- **Poll SCM**: `H/5 * * * *` (每5分钟检查一次)
- **GitHub hook trigger for GITScm polling** (如果使用GitHub)

## 🔧 故障排除

### 问题1: Allure报告未生成
**症状**: 测试执行成功，但没有Allure报告
**解决方案**:
1. 检查Allure命令行工具是否正确安装
2. 验证Jenkins系统配置中的Allure路径
3. 检查测试是否生成了 `results/allure-results/` 目录

### 问题2: 测试执行失败
**症状**: 测试阶段失败，无法生成报告
**解决方案**:
1. 检查Jenkins控制台输出
2. 验证Python环境和依赖是否正确安装
3. 检查Playwright浏览器是否已安装

### 问题3: 邮件发送失败
**症状**: 构建成功但邮件未发送
**解决方案**:
1. 检查邮件服务器配置
2. 验证收件人邮箱地址
3. 检查Jenkins邮件插件配置

## 📊 验证配置

### 1. 手动触发构建
1. 在Jenkins任务页面点击 "Build Now"
2. 观察构建过程
3. 检查是否生成了Allure报告

### 2. 查看测试报告
1. 构建完成后，点击构建编号
2. 在左侧菜单中应该能看到 "Allure Report" 链接
3. 点击查看详细的测试报告

### 3. 检查归档文件
1. 在构建页面查看 "Build Artifacts"
2. 应该包含HTML报告、测试数据等文件

## 🎉 成功标志

当配置正确时，您应该能看到：
- ✅ 测试执行成功
- ✅ 生成了 `results/allure-results/` 目录
- ✅ Jenkins显示 "Allure Report" 链接
- ✅ 邮件通知包含报告链接
- ✅ 测试结果被正确归档

## 📞 获取帮助

如果遇到问题：
1. 检查Jenkins控制台输出
2. 查看Jenkins系统日志
3. 验证所有必需插件已安装
4. 确认系统配置正确
