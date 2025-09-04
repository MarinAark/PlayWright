"""
简化的API测试示例
不依赖复杂的fixture，直接测试基本功能
"""
import requests
import json

def test_httpbin_get():
    """测试基本的GET请求"""
    response = requests.get("https://httpbin.org/get")
    assert response.status_code == 200
    
    data = response.json()
    assert "url" in data
    assert "headers" in data
    print("✅ GET请求测试通过")

def test_httpbin_post():
    """测试基本的POST请求"""
    test_data = {"test": "data", "number": 123}
    response = requests.post("https://httpbin.org/post", json=test_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "json" in data
    assert data["json"]["test"] == "data"
    print("✅ POST请求测试通过")

def test_config_system():
    """测试配置系统"""
    from config.config_manager import get_config
    
    config = get_config()
    assert config.api.base_url == "https://httpbin.org"
    assert config.database.type == "sqlite"
    print("✅ 配置系统测试通过")

def test_database_client():
    """测试数据库客户端"""
    from utils.database_client import DatabaseClient
    
    client = DatabaseClient('sqlite', {'database': ':memory:'})
    assert client.test_connection()
    
    # 基本操作测试
    client.execute_update("CREATE TABLE test (id INTEGER, name TEXT)")
    client.execute_update("INSERT INTO test VALUES (1, 'test')")
    
    result = client.execute_query("SELECT * FROM test")
    assert len(result) == 1
    assert result[0]['name'] == 'test'
    
    client.close()
    print("✅ 数据库客户端测试通过")

if __name__ == "__main__":
    print("🚀 开始简化API测试")
    
    try:
        test_config_system()
        test_database_client()
        test_httpbin_get()
        test_httpbin_post()
        
        print("🎉 所有测试通过！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
