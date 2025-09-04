import pytest
from pages.api_pages import HTTPBinAPI, UserAPI, ProductAPI
from utils.test_data import TestDataManager, TestDataTemplates
from utils.logger import get_logger

# 可选导入allure
try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

# 创建可选的allure装饰器
def optional_allure_epic(name):
    if ALLURE_AVAILABLE:
        return allure.epic(name)
    else:
        def decorator(cls):
            return cls
        return decorator

def optional_allure_feature(name):
    if ALLURE_AVAILABLE:
        return allure.feature(name)
    else:
        def decorator(cls):
            return cls
        return decorator

def optional_allure_story(name):
    if ALLURE_AVAILABLE:
        return allure.story(name)
    else:
        def decorator(func):
            return func
        return decorator

logger = get_logger(__name__)

@optional_allure_epic("API测试")
@optional_allure_feature("HTTPBin API")
class TestHTTPBinAPI:
    """HTTPBin API测试用例"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置"""
        self.api = HTTPBinAPI()
        yield
        self.api.close()
    
    @optional_allure_story("GET请求测试")
    def test_get_request(self):
        """测试GET请求"""
        response = self.api.get_request_info()
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 断言响应内容
        self.api.assert_response_contains(response, "args")
        self.api.assert_response_contains(response, "headers")
        
        # 断言响应时间
        self.api.assert_response_time(response, 5.0)
        
        logger.info("GET请求测试通过")
    
    @optional_allure_story("POST请求测试")
    def test_post_request(self):
        """测试POST请求"""
        test_data = {"name": "测试用户", "age": 25}
        response = self.api.post_data(test_data)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证返回的数据
        response_data = response.json()
        assert response_data["json"]["name"] == "测试用户"
        assert response_data["json"]["age"] == 25
        
        logger.info("POST请求测试通过")
    
    @optional_allure_story("PUT请求测试")
    def test_put_request(self):
        """测试PUT请求"""
        test_data = {"name": "更新用户", "age": 30}
        response = self.api.put_data(test_data)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证返回的数据
        response_data = response.json()
        assert response_data["json"]["name"] == "更新用户"
        
        logger.info("PUT请求测试通过")
    
    @optional_allure_story("DELETE请求测试")
    def test_delete_request(self):
        """测试DELETE请求"""
        response = self.api.delete_data()
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        logger.info("DELETE请求测试通过")
    
    @optional_allure_story("状态码测试")
    @pytest.mark.parametrize("status_code", [200, 404, 500])
    def test_status_codes(self, status_code):
        """测试不同状态码"""
        response = self.api.get_status_code(status_code)
        
        # 断言状态码
        self.api.assert_status_code(response, status_code)
        
        logger.info(f"状态码 {status_code} 测试通过")
    
    @optional_allure_story("延迟响应测试")
    def test_delayed_response(self):
        """测试延迟响应"""
        from utils.retry_decorator import retry_on_http_error
        import time
        
        @retry_on_http_error(
            max_retries=3, 
            delay=1.0, 
            retry_status_codes=(500, 502, 503, 504),
            skip_on_final_failure=True
        )
        def perform_delay_test():
            start_time = time.time()
            response = self.api.get_delayed_response(delay=2)
            end_time = time.time()
            
            # 断言状态码
            self.api.assert_status_code(response, 200)
            
            # 断言响应时间（应该大于延迟时间，但考虑网络延迟，允许一定误差）
            actual_delay = end_time - start_time
            assert actual_delay >= 1.5, f"响应时间{actual_delay:.2f}秒太短，期望至少1.5秒"
            
            logger.info(f"延迟响应测试通过，实际延迟: {actual_delay:.2f}秒")
            return response
        
        # 执行带重试的延迟测试
        perform_delay_test()
    
    @optional_allure_story("基本连接测试")
    def test_basic_connection(self):
        """测试基本连接（备用测试）"""
        try:
            response = self.api.get_basic_info()
            
            # 如果httpbin根端点不可用，尝试最简单的端点
            if response.status_code != 200:
                response = self.api.get_request_info()
                self.api.assert_status_code(response, 200)
            else:
                self.api.assert_status_code(response, 200)
            
            logger.info("基本连接测试通过")
            
        except Exception as e:
            pytest.skip(f"httpbin.org服务完全不可用: {e}")

@optional_allure_epic("API测试")
@allure.feature("用户管理API")
class TestUserAPI:
    """用户API测试用例"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置"""
        self.api = UserAPI()
        yield
        self.api.close()
    
    @optional_allure_story("获取用户列表")
    def test_get_all_users(self):
        """测试获取所有用户"""
        response = self.api.get_all_users()
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证响应数据结构
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        
        # 验证用户数据结构
        first_user = users[0]
        assert "id" in first_user
        assert "name" in first_user
        assert "email" in first_user
        
        logger.info("获取用户列表测试通过")
    
    @optional_allure_story("获取指定用户")
    @pytest.mark.parametrize("user_id", [1, 2, 3])
    def test_get_user_by_id(self, user_id):
        """测试根据ID获取用户"""
        response = self.api.get_user_by_id(user_id)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证用户数据
        user = response.json()
        assert user["id"] == user_id
        assert "name" in user
        assert "email" in user
        
        logger.info(f"获取用户 {user_id} 测试通过")
    
    @optional_allure_story("创建新用户")
    def test_create_user(self):
        """测试创建新用户"""
        user_data = TestDataTemplates.user_registration()
        response = self.api.create_user(user_data)
        
        # 断言状态码
        self.api.assert_status_code(response, 201)
        
        # 验证返回的用户数据
        created_user = response.json()
        assert created_user["username"] == user_data["username"]
        assert created_user["email"] == user_data["email"]
        
        logger.info("创建新用户测试通过")
    
    @optional_allure_story("更新用户信息")
    def test_update_user(self):
        """测试更新用户信息"""
        user_id = 1
        update_data = {"name": "更新后的用户名", "email": "updated@example.com"}
        response = self.api.update_user(user_id, update_data)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证更新后的数据
        updated_user = response.json()
        assert updated_user["name"] == update_data["name"]
        assert updated_user["email"] == update_data["email"]
        
        logger.info("更新用户信息测试通过")
    
    @optional_allure_story("删除用户")
    def test_delete_user(self):
        """测试删除用户"""
        user_id = 1
        response = self.api.delete_user(user_id)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        logger.info("删除用户测试通过")

@optional_allure_epic("API测试")
@allure.feature("产品管理API")
class TestProductAPI:
    """产品API测试用例"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置"""
        self.api = ProductAPI()
        yield
        self.api.close()
    
    @optional_allure_story("获取产品列表")
    def test_get_all_products(self):
        """测试获取所有产品"""
        response = self.api.get_all_products(limit=5, skip=0)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证响应数据结构
        products_data = response.json()
        assert "products" in products_data
        assert "total" in products_data
        
        products = products_data["products"]
        assert len(products) <= 5
        
        # 验证产品数据结构
        if products:
            first_product = products[0]
            assert "id" in first_product
            assert "title" in first_product
            assert "price" in first_product
        
        logger.info("获取产品列表测试通过")
    
    @optional_allure_story("搜索产品")
    @pytest.mark.parametrize("search_query", ["phone", "laptop", "book"])
    def test_search_products(self, search_query):
        """测试产品搜索"""
        response = self.api.search_products(search_query)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证搜索结果
        search_results = response.json()
        assert "products" in search_results
        
        logger.info(f"搜索产品 '{search_query}' 测试通过")
    
    @optional_allure_story("获取产品分类")
    def test_get_product_categories(self):
        """测试获取产品分类"""
        response = self.api.get_product_categories()
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证分类数据
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        
        logger.info("获取产品分类测试通过")
    
    @optional_allure_story("获取产品详情")
    @pytest.mark.parametrize("product_id", [1, 2, 3])
    def test_get_product_by_id(self, product_id):
        """测试根据ID获取产品详情"""
        response = self.api.get_product_by_id(product_id)
        
        # 断言状态码
        self.api.assert_status_code(response, 200)
        
        # 验证产品数据
        product = response.json()
        assert product["id"] == product_id
        assert "title" in product
        assert "price" in product
        assert "description" in product
        
        logger.info(f"获取产品 {product_id} 详情测试通过")
