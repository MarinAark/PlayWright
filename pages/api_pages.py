import allure
from utils.api_client import APIClient
from utils.logger import get_logger

logger = get_logger(__name__)

class HTTPBinAPI(APIClient):
    """HTTPBin API测试页面类"""
    
    def __init__(self):
        super().__init__(base_url="https://httpbin.org")
    
    @allure.step("获取请求信息")
    def get_request_info(self):
        """获取请求信息"""
        return self.get("get")
    
    @allure.step("发送POST请求")
    def post_data(self, data):
        """发送POST请求"""
        return self.post("post", json_data=data)
    
    @allure.step("发送PUT请求")
    def put_data(self, data):
        """发送PUT请求"""
        return self.put("put", json_data=data)
    
    @allure.step("发送DELETE请求")
    def delete_data(self):
        """发送DELETE请求"""
        return self.delete("delete")
    
    @allure.step("获取状态码")
    def get_status_code(self, status_code):
        """获取指定状态码"""
        return self.get(f"status/{status_code}")
    
    @allure.step("延迟响应")
    def get_delayed_response(self, delay=3):
        """获取延迟响应"""
        # HTTPBin的延迟端点格式是 /delay/{seconds}
        return self.get(f"delay/{delay}")
    
    @allure.step("获取随机字节")
    def get_random_bytes(self, size=1024):
        """获取随机字节"""
        return self.get("bytes", params={"n": size})

class UserAPI(APIClient):
    """用户API测试页面类"""
    
    def __init__(self):
        super().__init__(base_url="https://jsonplaceholder.typicode.com")
    
    @allure.step("获取所有用户")
    def get_all_users(self):
        """获取所有用户"""
        return self.get("users")
    
    @allure.step("获取指定用户")
    def get_user_by_id(self, user_id):
        """根据ID获取用户"""
        return self.get(f"users/{user_id}")
    
    @allure.step("创建新用户")
    def create_user(self, user_data):
        """创建新用户"""
        return self.post("users", json_data=user_data)
    
    @allure.step("更新用户信息")
    def update_user(self, user_id, user_data):
        """更新用户信息"""
        return self.put(f"users/{user_id}", json_data=user_data)
    
    @allure.step("删除用户")
    def delete_user(self, user_id):
        """删除用户"""
        return self.delete(f"users/{user_id}")
    
    @allure.step("获取用户帖子")
    def get_user_posts(self, user_id):
        """获取用户的帖子"""
        return self.get(f"users/{user_id}/posts")

class ProductAPI(APIClient):
    """产品API测试页面类"""
    
    def __init__(self):
        super().__init__(base_url="https://dummyjson.com")
    
    @allure.step("获取所有产品")
    def get_all_products(self, limit=10, skip=0):
        """获取所有产品"""
        return self.get("products", params={"limit": limit, "skip": skip})
    
    @allure.step("搜索产品")
    def search_products(self, query):
        """搜索产品"""
        return self.get("products/search", params={"q": query})
    
    @allure.step("获取产品分类")
    def get_product_categories(self):
        """获取产品分类"""
        return self.get("products/categories")
    
    @allure.step("获取指定分类的产品")
    def get_products_by_category(self, category):
        """根据分类获取产品"""
        return self.get(f"products/category/{category}")
    
    @allure.step("获取产品详情")
    def get_product_by_id(self, product_id):
        """根据ID获取产品详情"""
        return self.get(f"products/{product_id}")
    
    @allure.step("添加产品到购物车")
    def add_to_cart(self, user_id, products):
        """添加产品到购物车"""
        return self.post("carts/add", json_data={
            "userId": user_id,
            "products": products
        })
