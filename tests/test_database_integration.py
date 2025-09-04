"""
数据库集成测试示例
展示如何使用数据库测试工具进行数据验证
"""
import pytest
import allure
from utils.database_client import DatabaseClient, DatabaseTestHelper
from config.config_manager import get_config


@allure.epic("数据库测试")
@allure.feature("数据库集成")
class TestDatabaseIntegration:
    """数据库集成测试类"""
    
    @pytest.fixture(scope="class")
    def db_client(self):
        """数据库客户端fixture"""
        config = get_config()
        db_config = {
            'type': config.database.type,
            'database': config.database.database,
            'host': config.database.host,
            'port': config.database.port,
            'user': config.database.username,
            'password': config.database.password
        }
        
        client = DatabaseClient(db_config['type'], db_config)
        yield client
        client.close()
    
    @pytest.fixture(scope="class")
    def db_helper(self, db_client):
        """数据库测试助手fixture"""
        return DatabaseTestHelper(db_client)
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_test_tables(self, db_client):
        """设置测试表"""
        # 创建测试表（SQLite示例）
        if db_client.db_type == 'sqlite':
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS test_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            db_client.execute_update(create_table_sql)
        
        yield
        
        # 清理测试表
        if db_client.db_type == 'sqlite':
            db_client.execute_update("DROP TABLE IF EXISTS test_users")
    
    @allure.story("连接测试")
    def test_database_connection(self, db_client):
        """测试数据库连接"""
        with allure.step("测试数据库连接"):
            assert db_client.test_connection(), "数据库连接失败"
        
        allure.attach(f"数据库类型: {db_client.db_type}", "连接信息", allure.attachment_type.TEXT)
    
    @allure.story("数据操作")
    def test_crud_operations(self, db_client, db_helper):
        """测试基本的CRUD操作"""
        
        with allure.step("插入测试数据"):
            test_data = [
                {"username": "testuser1", "email": "test1@example.com"},
                {"username": "testuser2", "email": "test2@example.com"},
                {"username": "testuser3", "email": "test3@example.com"}
            ]
            
            success = db_helper.create_test_data("test_users", test_data)
            assert success, "插入测试数据失败"
            
            allure.attach(f"插入了 {len(test_data)} 条记录", "插入结果", allure.attachment_type.TEXT)
        
        with allure.step("查询数据"):
            users = db_client.execute_query("SELECT * FROM test_users ORDER BY id")
            assert len(users) == 3, f"期望3条记录，实际{len(users)}条"
            
            # 验证数据内容
            assert users[0]["username"] == "testuser1"
            assert users[1]["email"] == "test2@example.com"
            
            allure.attach(f"查询到 {len(users)} 条记录", "查询结果", allure.attachment_type.TEXT)
        
        with allure.step("更新数据"):
            affected = db_client.execute_update(
                "UPDATE test_users SET email = ? WHERE username = ?",
                ("updated@example.com", "testuser1")
            )
            assert affected == 1, f"期望更新1条记录，实际更新{affected}条"
            
            # 验证更新结果
            updated_user = db_client.execute_query(
                "SELECT email FROM test_users WHERE username = ?",
                ("testuser1",)
            )
            assert updated_user[0]["email"] == "updated@example.com"
            
            allure.attach(f"更新了 {affected} 条记录", "更新结果", allure.attachment_type.TEXT)
        
        with allure.step("删除数据"):
            affected = db_client.execute_update(
                "DELETE FROM test_users WHERE username = ?",
                ("testuser3",)
            )
            assert affected == 1, f"期望删除1条记录，实际删除{affected}条"
            
            # 验证删除结果
            remaining_users = db_client.execute_query("SELECT COUNT(*) as count FROM test_users")
            assert remaining_users[0]["count"] == 2
            
            allure.attach(f"删除了 {affected} 条记录", "删除结果", allure.attachment_type.TEXT)
    
    @allure.story("数据完整性")
    def test_data_integrity(self, db_client, db_helper):
        """测试数据完整性验证"""
        
        with allure.step("准备测试数据"):
            test_data = [
                {"username": f"user{i}", "email": f"user{i}@example.com"}
                for i in range(1, 11)
            ]
            db_helper.create_test_data("test_users", test_data)
        
        with allure.step("验证数据完整性"):
            # 验证记录数量
            integrity_check = db_helper.verify_data_integrity("test_users", 10)
            assert integrity_check, "数据完整性验证失败"
            
            # 验证数据唯一性
            unique_check = db_client.execute_query(
                "SELECT COUNT(DISTINCT username) as unique_count FROM test_users"
            )
            assert unique_check[0]["unique_count"] == 10, "用户名不唯一"
            
            allure.attach("数据完整性验证通过", "验证结果", allure.attachment_type.TEXT)
    
    @allure.story("表信息")
    def test_table_info(self, db_client):
        """测试获取表信息"""
        
        with allure.step("获取表信息"):
            table_info = db_client.get_table_info("test_users")
            
            assert table_info["name"] == "test_users"
            assert "row_count" in table_info or "count" in table_info
            
            if db_client.db_type == 'sqlite':
                assert "columns" in table_info
                assert len(table_info["columns"]) > 0
            
            allure.attach(
                f"表信息: {table_info}",
                "表结构信息",
                allure.attachment_type.TEXT
            )


@pytest.mark.database
@pytest.mark.slow
class TestDatabasePerformance:
    """数据库性能测试"""
    
    @pytest.fixture(scope="class")
    def db_client(self):
        """数据库客户端fixture"""
        config = get_config()
        db_config = {
            'type': config.database.type,
            'database': config.database.database
        }
        
        client = DatabaseClient(db_config['type'], db_config)
        
        # 创建性能测试表
        if client.db_type == 'sqlite':
            client.execute_update("""
                CREATE TABLE IF NOT EXISTS perf_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        yield client
        
        # 清理
        if client.db_type == 'sqlite':
            client.execute_update("DROP TABLE IF EXISTS perf_test")
        client.close()
    
    @allure.story("批量插入性能")
    def test_batch_insert_performance(self, db_client):
        """测试批量插入性能"""
        import time
        
        batch_size = 1000
        
        with allure.step(f"批量插入{batch_size}条记录"):
            start_time = time.time()
            
            for i in range(batch_size):
                db_client.execute_update(
                    "INSERT INTO perf_test (data) VALUES (?)",
                    (f"test_data_{i}",)
                )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 验证插入结果
            count_result = db_client.execute_query("SELECT COUNT(*) as count FROM perf_test")
            assert count_result[0]["count"] == batch_size
            
            # 性能断言（每秒至少插入100条记录）
            records_per_second = batch_size / duration
            assert records_per_second > 100, f"插入性能过低: {records_per_second:.2f} records/s"
            
            allure.attach(
                f"批量插入{batch_size}条记录耗时: {duration:.2f}秒\n"
                f"插入速率: {records_per_second:.2f} records/s",
                "性能统计",
                allure.attachment_type.TEXT
            )
    
    @allure.story("查询性能")
    def test_query_performance(self, db_client):
        """测试查询性能"""
        import time
        
        with allure.step("查询性能测试"):
            start_time = time.time()
            
            # 执行多次查询
            for _ in range(100):
                result = db_client.execute_query("SELECT COUNT(*) as count FROM perf_test")
                assert len(result) == 1
            
            end_time = time.time()
            duration = end_time - start_time
            queries_per_second = 100 / duration
            
            # 性能断言（每秒至少执行50次查询）
            assert queries_per_second > 50, f"查询性能过低: {queries_per_second:.2f} queries/s"
            
            allure.attach(
                f"执行100次查询耗时: {duration:.2f}秒\n"
                f"查询速率: {queries_per_second:.2f} queries/s",
                "查询性能统计",
                allure.attachment_type.TEXT
            )
