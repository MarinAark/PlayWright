#!/usr/bin/env python3
"""
项目改进验证脚本
用于验证所有新增和改进的功能是否正常工作
"""
import os
import sys
import subprocess
import importlib.util
from pathlib import Path
import time
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ImprovementVerifier:
    """改进验证器"""
    
    def __init__(self):
        self.results = {}
        self.total_checks = 0
        self.passed_checks = 0
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        self.total_checks += 1
        if success:
            self.passed_checks += 1
            print(f"✅ {test_name}: 通过")
        else:
            print(f"❌ {test_name}: 失败 - {message}")
        
        self.results[test_name] = {
            'success': success,
            'message': message
        }
    
    def verify_project_structure(self):
        """验证项目结构"""
        print("\n🔍 验证项目结构...")
        
        required_dirs = [
            "config", "tools", "utils", "tests", "pages",
            "test_data", "results", "docs"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.log_result(
                f"目录存在检查: {dir_name}",
                dir_path.exists(),
                f"目录 {dir_path} 不存在" if not dir_path.exists() else ""
            )
        
        # 检查关键文件
        key_files = [
            "config/config_manager.py",
            "tools/cli.py",
            "tools/file_renamer.py",
            "tools/image_compressor.py",
            "tools/file_downloader.py",
            "utils/database_client.py",
            "utils/performance_tester.py",
            "docs/BEST_PRACTICES.md",
            "IMPROVEMENT_SUMMARY.md"
        ]
        
        for file_path in key_files:
            full_path = project_root / file_path
            self.log_result(
                f"文件存在检查: {file_path}",
                full_path.exists(),
                f"文件 {full_path} 不存在" if not full_path.exists() else ""
            )
    
    def verify_dependencies(self):
        """验证依赖安装"""
        print("\n📦 验证依赖安装...")
        
        # 核心依赖
        core_deps = [
            "playwright", "pytest", "requests", "pandas", 
            "Pillow", "python-dotenv"
        ]
        
        for dep in core_deps:
            try:
                importlib.import_module(dep.replace("-", "_"))
                self.log_result(f"依赖检查: {dep}", True)
            except ImportError:
                self.log_result(f"依赖检查: {dep}", False, f"模块 {dep} 未安装")
        
        # 可选依赖（不影响核心功能）
        optional_deps = ["yaml", "aiohttp", "mysql.connector", "psycopg2", "pymongo"]
        
        for dep in optional_deps:
            try:
                importlib.import_module(dep.replace("-", "_"))
                self.log_result(f"可选依赖: {dep}", True)
            except ImportError:
                self.log_result(f"可选依赖: {dep}", False, f"可选模块 {dep} 未安装（不影响核心功能）")
    
    def verify_config_system(self):
        """验证配置系统"""
        print("\n⚙️ 验证配置系统...")
        
        try:
            from config.config_manager import ConfigManager, get_config
            
            # 测试配置管理器创建
            config_manager = ConfigManager()
            self.log_result("配置管理器创建", True)
            
            # 测试配置获取
            config = get_config()
            self.log_result("配置获取", config is not None)
            
            # 测试配置项访问
            self.log_result(
                "数据库配置访问", 
                hasattr(config, 'database') and hasattr(config.database, 'type')
            )
            
            self.log_result(
                "API配置访问",
                hasattr(config, 'api') and hasattr(config.api, 'base_url')
            )
            
            self.log_result(
                "浏览器配置访问",
                hasattr(config, 'browser') and hasattr(config.browser, 'headless')
            )
            
        except Exception as e:
            self.log_result("配置系统", False, str(e))
    
    def verify_database_client(self):
        """验证数据库客户端"""
        print("\n🗄️ 验证数据库客户端...")
        
        try:
            from utils.database_client import DatabaseClient, DatabaseTestHelper
            
            # 测试SQLite（内置支持）
            db_config = {'type': 'sqlite', 'database': ':memory:'}
            client = DatabaseClient('sqlite', {'database': ':memory:'})
            
            self.log_result("数据库客户端创建", True)
            
            # 测试连接
            connection_ok = client.test_connection()
            self.log_result("数据库连接测试", connection_ok)
            
            if connection_ok:
                # 测试基本操作
                client.execute_update("CREATE TABLE test (id INTEGER, name TEXT)")
                client.execute_update("INSERT INTO test VALUES (1, 'test')")
                result = client.execute_query("SELECT * FROM test")
                
                self.log_result("数据库基本操作", len(result) == 1 and result[0]['name'] == 'test')
            
            client.close()
            
        except Exception as e:
            self.log_result("数据库客户端", False, str(e))
    
    def verify_performance_tester(self):
        """验证性能测试工具"""
        print("\n🏃 验证性能测试工具...")
        
        try:
            from utils.performance_tester import PerformanceTester, PerformanceMetrics
            
            # 测试性能指标类
            metrics = PerformanceMetrics()
            self.log_result("性能指标类创建", True)
            
            # 测试性能测试器创建
            tester = PerformanceTester("https://httpbin.org")
            self.log_result("性能测试器创建", True)
            
            # 测试报告生成
            metrics.total_requests = 10
            metrics.successful_requests = 9
            metrics.response_times = [100, 150, 200, 120, 180]
            
            report = tester.generate_report(metrics)
            self.log_result("性能报告生成", "成功率" in report and "响应时间" in report)
            
        except Exception as e:
            self.log_result("性能测试工具", False, str(e))
    
    def verify_tools(self):
        """验证工具集"""
        print("\n🛠️ 验证工具集...")
        
        # 测试CLI工具
        try:
            cli_path = project_root / "tools" / "cli.py"
            result = subprocess.run(
                [sys.executable, str(cli_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.log_result("CLI工具帮助", result.returncode == 0 and "工具集" in result.stdout)
        except Exception as e:
            self.log_result("CLI工具", False, str(e))
        
        # 测试工具类导入
        tools = [
            ("文件重命名工具", "tools.file_renamer", "FileRenamer"),
            ("图片压缩工具", "tools.image_compressor", "ImageCompressor"),
            ("文件下载工具", "tools.file_downloader", "FileDownloader")
        ]
        
        for tool_name, module_name, class_name in tools:
            try:
                module = importlib.import_module(module_name)
                tool_class = getattr(module, class_name)
                self.log_result(f"{tool_name}导入", True)
            except Exception as e:
                self.log_result(f"{tool_name}导入", False, str(e))
    
    def verify_test_cases(self):
        """验证测试用例"""
        print("\n🧪 验证测试用例...")
        
        test_files = [
            "tests/test_baidu_search.py",
            "tests/test_api_basic.py", 
            "tests/test_database_integration.py",
            "tests/test_performance.py"
        ]
        
        for test_file in test_files:
            test_path = project_root / test_file
            if test_path.exists():
                try:
                    # 尝试导入测试文件（语法检查）
                    spec = importlib.util.spec_from_file_location("test_module", test_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.log_result(f"测试文件语法: {test_file}", True)
                except Exception as e:
                    self.log_result(f"测试文件语法: {test_file}", False, str(e))
            else:
                self.log_result(f"测试文件存在: {test_file}", False, "文件不存在")
    
    def run_sample_tests(self):
        """运行示例测试"""
        print("\n🚀 运行示例测试...")
        
        # 运行配置测试
        try:
            result = subprocess.run(
                [sys.executable, "-c", "from config.config_manager import get_config; print('Config OK')"],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            self.log_result("配置系统运行测试", result.returncode == 0)
        except Exception as e:
            self.log_result("配置系统运行测试", False, str(e))
        
        # 运行数据库测试（如果可用）
        try:
            result = subprocess.run([
                sys.executable, "-c", 
                "from utils.database_client import DatabaseClient; "
                "client = DatabaseClient('sqlite', {'database': ':memory:'}); "
                "print('DB OK' if client.test_connection() else 'DB Failed')"
            ], cwd=project_root, capture_output=True, text=True, timeout=30)
            
            self.log_result("数据库运行测试", result.returncode == 0 and "DB OK" in result.stdout)
        except Exception as e:
            self.log_result("数据库运行测试", False, str(e))
    
    def generate_report(self):
        """生成验证报告"""
        print("\n" + "="*60)
        print("📊 验证结果汇总")
        print("="*60)
        
        success_rate = (self.passed_checks / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"总检查项: {self.total_checks}")
        print(f"通过检查: {self.passed_checks}")
        print(f"失败检查: {self.total_checks - self.passed_checks}")
        print(f"成功率: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 验证结果: 优秀！项目改进基本完成且功能正常")
        elif success_rate >= 75:
            print("👍 验证结果: 良好！大部分功能正常，有少量问题需要修复")
        elif success_rate >= 50:
            print("⚠️  验证结果: 一般！有一些问题需要解决")
        else:
            print("❌ 验证结果: 需要修复！存在较多问题")
        
        # 显示失败的检查项
        failed_checks = [name for name, result in self.results.items() if not result['success']]
        if failed_checks:
            print(f"\n❌ 失败的检查项 ({len(failed_checks)}个):")
            for check in failed_checks:
                message = self.results[check]['message']
                print(f"  - {check}" + (f": {message}" if message else ""))
        
        # 保存详细报告
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_checks': self.total_checks,
                'passed_checks': self.passed_checks,
                'failed_checks': self.total_checks - self.passed_checks,
                'success_rate': success_rate
            },
            'details': self.results
        }
        
        report_file = project_root / "verification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return success_rate >= 75  # 75%以上认为验证通过
    
    def run_all_verifications(self):
        """运行所有验证"""
        print("🔍 开始项目改进验证...")
        print("=" * 60)
        
        self.verify_project_structure()
        self.verify_dependencies()
        self.verify_config_system()
        self.verify_database_client()
        self.verify_performance_tester()
        self.verify_tools()
        self.verify_test_cases()
        self.run_sample_tests()
        
        return self.generate_report()


def main():
    """主函数"""
    verifier = ImprovementVerifier()
    success = verifier.run_all_verifications()
    
    print(f"\n🎯 验证{'通过' if success else '失败'}！")
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
