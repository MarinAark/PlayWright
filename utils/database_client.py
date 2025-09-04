"""
数据库测试客户端
支持多种数据库的连接和测试操作
"""
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager
import os
from pathlib import Path

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    import psycopg2.extras
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    import pymongo
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

# 设置日志
logger = logging.getLogger(__name__)


class DatabaseClient:
    """通用数据库客户端"""
    
    def __init__(self, db_type: str, connection_config: Dict[str, Any]):
        self.db_type = db_type.lower()
        self.connection_config = connection_config
        self.connection = None
        self._setup_connection()
    
    def _setup_connection(self):
        """设置数据库连接"""
        if self.db_type == 'sqlite':
            self._setup_sqlite()
        elif self.db_type == 'mysql':
            self._setup_mysql()
        elif self.db_type == 'postgresql':
            self._setup_postgresql()
        elif self.db_type == 'mongodb':
            self._setup_mongodb()
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
    
    def _setup_sqlite(self):
        """设置SQLite连接"""
        if not SQLITE_AVAILABLE:
            raise ImportError("SQLite不可用，请检查Python安装")
        
        db_path = self.connection_config.get('database', ':memory:')
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        logger.info(f"SQLite连接已建立: {db_path}")
    
    def _setup_mysql(self):
        """设置MySQL连接"""
        if not MYSQL_AVAILABLE:
            raise ImportError("MySQL连接器不可用，请安装: pip install mysql-connector-python")
        
        self.connection = mysql.connector.connect(**self.connection_config)
        logger.info(f"MySQL连接已建立: {self.connection_config.get('host')}")
    
    def _setup_postgresql(self):
        """设置PostgreSQL连接"""
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL连接器不可用，请安装: pip install psycopg2-binary")
        
        self.connection = psycopg2.connect(**self.connection_config)
        logger.info(f"PostgreSQL连接已建立: {self.connection_config.get('host')}")
    
    def _setup_mongodb(self):
        """设置MongoDB连接"""
        if not MONGODB_AVAILABLE:
            raise ImportError("MongoDB连接器不可用，请安装: pip install pymongo")
        
        host = self.connection_config.get('host', 'localhost')
        port = self.connection_config.get('port', 27017)
        self.connection = pymongo.MongoClient(host, port)
        logger.info(f"MongoDB连接已建立: {host}:{port}")
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标（上下文管理器）"""
        if self.db_type == 'mongodb':
            yield self.connection
        else:
            cursor = self.connection.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        if self.db_type == 'mongodb':
            raise ValueError("MongoDB请使用专门的方法")
        
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 获取结果
            if self.db_type == 'sqlite':
                results = [dict(row) for row in cursor.fetchall()]
            elif self.db_type == 'mysql':
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            elif self.db_type == 'postgresql':
                cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                results = [dict(row) for row in cursor.fetchall()]
            else:
                results = []
            
            logger.debug(f"查询执行完成，返回 {len(results)} 行结果")
            return results
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        执行更新语句（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL语句
            params: 参数
            
        Returns:
            影响的行数
        """
        if self.db_type == 'mongodb':
            raise ValueError("MongoDB请使用专门的方法")
        
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            affected_rows = cursor.rowcount
            self.connection.commit()
            
            logger.debug(f"更新执行完成，影响 {affected_rows} 行")
            return affected_rows
    
    def execute_script(self, script_path: str) -> bool:
        """
        执行SQL脚本文件
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            是否执行成功
        """
        if self.db_type == 'mongodb':
            raise ValueError("MongoDB不支持SQL脚本")
        
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            # 分割多个语句
            statements = [stmt.strip() for stmt in script_content.split(';') if stmt.strip()]
            
            with self.get_cursor() as cursor:
                for statement in statements:
                    cursor.execute(statement)
                
                self.connection.commit()
            
            logger.info(f"脚本执行完成: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"脚本执行失败: {e}")
            self.connection.rollback()
            return False
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            if self.db_type == 'mongodb':
                # MongoDB连接测试
                self.connection.admin.command('ping')
            else:
                # SQL数据库连接测试
                test_queries = {
                    'sqlite': 'SELECT 1',
                    'mysql': 'SELECT 1',
                    'postgresql': 'SELECT 1'
                }
                
                query = test_queries.get(self.db_type, 'SELECT 1')
                self.execute_query(query)
            
            logger.info(f"{self.db_type}数据库连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"{self.db_type}数据库连接测试失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        if self.db_type == 'mongodb':
            # MongoDB集合信息
            db_name = self.connection_config.get('database', 'test')
            db = self.connection[db_name]
            collection = db[table_name]
            
            return {
                'name': table_name,
                'count': collection.count_documents({}),
                'indexes': list(collection.list_indexes())
            }
        
        else:
            # SQL表信息
            info_queries = {
                'sqlite': f"PRAGMA table_info({table_name})",
                'mysql': f"DESCRIBE {table_name}",
                'postgresql': f"""
                    SELECT column_name, data_type, is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                """
            }
            
            query = info_queries.get(self.db_type)
            if query:
                columns = self.execute_query(query)
                
                # 获取行数
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = count_result[0]['count'] if count_result else 0
                
                return {
                    'name': table_name,
                    'columns': columns,
                    'row_count': row_count
                }
            
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info(f"{self.db_type}数据库连接已关闭")


class DatabaseTestHelper:
    """数据库测试助手类"""
    
    def __init__(self, client: DatabaseClient):
        self.client = client
    
    def create_test_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """创建测试数据"""
        if not data:
            return True
        
        try:
            # 构建INSERT语句
            columns = list(data[0].keys())
            placeholders = ', '.join(['?' if self.client.db_type == 'sqlite' else '%s'] * len(columns))
            column_names = ', '.join(columns)
            
            query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
            
            for row in data:
                values = tuple(row[col] for col in columns)
                self.client.execute_update(query, values)
            
            logger.info(f"成功插入 {len(data)} 条测试数据到表 {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建测试数据失败: {e}")
            return False
    
    def cleanup_test_data(self, table_name: str, condition: str = None) -> bool:
        """清理测试数据"""
        try:
            if condition:
                query = f"DELETE FROM {table_name} WHERE {condition}"
            else:
                query = f"DELETE FROM {table_name}"
            
            affected = self.client.execute_update(query)
            logger.info(f"从表 {table_name} 删除了 {affected} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"清理测试数据失败: {e}")
            return False
    
    def verify_data_integrity(self, table_name: str, expected_count: int) -> bool:
        """验证数据完整性"""
        try:
            result = self.client.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
            actual_count = result[0]['count']
            
            if actual_count == expected_count:
                logger.info(f"数据完整性验证通过: {table_name} ({actual_count} 条记录)")
                return True
            else:
                logger.error(f"数据完整性验证失败: 期望 {expected_count} 条，实际 {actual_count} 条")
                return False
                
        except Exception as e:
            logger.error(f"数据完整性验证异常: {e}")
            return False


def create_database_client(db_config: Dict[str, Any]) -> DatabaseClient:
    """
    创建数据库客户端的工厂函数
    
    Args:
        db_config: 数据库配置字典
        
    Returns:
        DatabaseClient实例
    """
    db_type = db_config.pop('type', 'sqlite')
    return DatabaseClient(db_type, db_config)


# 配置示例
DATABASE_CONFIGS = {
    'sqlite_test': {
        'type': 'sqlite',
        'database': ':memory:'  # 内存数据库用于测试
    },
    'mysql_test': {
        'type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'user': 'test_user',
        'password': 'test_password',
        'database': 'test_db'
    },
    'postgresql_test': {
        'type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'user': 'test_user',
        'password': 'test_password',
        'database': 'test_db'
    },
    'mongodb_test': {
        'type': 'mongodb',
        'host': 'localhost',
        'port': 27017,
        'database': 'test_db'
    }
}
