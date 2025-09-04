import json
import os
from typing import List, Dict, Any, Union
from utils.logger import get_logger

# 可选导入pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = get_logger(__name__)

class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, data_dir: str = "test_data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"创建测试数据目录: {self.data_dir}")
    
    def load_json_data(self, filename: str) -> List[Dict]:
        """加载JSON格式的测试数据"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功加载JSON测试数据: {filename}")
                return data
        except FileNotFoundError:
            logger.warning(f"测试数据文件不存在: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件解析失败: {file_path}, 错误: {e}")
            return []
    
    def load_excel_data(self, filename: str, sheet_name: str = None) -> List[Dict]:
        """加载Excel格式的测试数据"""
        if not PANDAS_AVAILABLE:
            logger.warning("pandas不可用，无法加载Excel文件")
            return []
            
        file_path = os.path.join(self.data_dir, filename)
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # 转换为字典列表
            data = df.to_dict('records')
            logger.info(f"成功加载Excel测试数据: {filename}")
            return data
        except FileNotFoundError:
            logger.warning(f"测试数据文件不存在: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Excel文件读取失败: {file_path}, 错误: {e}")
            return []
    
    def save_test_result(self, filename: str, data: List[Dict]):
        """保存测试结果"""
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"测试结果已保存: {filename}")
        except Exception as e:
            logger.error(f"保存测试结果失败: {e}")
    
    def generate_test_data(self, template: Dict, count: int = 1) -> List[Dict]:
        """根据模板生成测试数据"""
        data = []
        for i in range(count):
            item = {}
            for key, value in template.items():
                if isinstance(value, str) and '{index}' in value:
                    item[key] = value.format(index=i + 1)
                elif isinstance(value, str) and '{random}' in value:
                    import random
                    import string
                    random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
                    item[key] = value.replace('{random}', random_str)
                else:
                    item[key] = value
            data.append(item)
        return data
    
    def filter_test_data(self, data: List[Dict], filters: Dict) -> List[Dict]:
        """根据条件过滤测试数据"""
        filtered_data = []
        for item in data:
            match = True
            for key, value in filters.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                filtered_data.append(item)
        return filtered_data

# 预定义的测试数据模板
class TestDataTemplates:
    """测试数据模板"""
    
    @staticmethod
    def user_registration():
        """用户注册测试数据模板"""
        return {
            "username": "testuser{index}",
            "email": "test{index}@example.com",
            "password": "password123",
            "confirm_password": "password123"
        }
    
    @staticmethod
    def user_login():
        """用户登录测试数据模板"""
        return {
            "username": "testuser",
            "password": "password123"
        }
    
    @staticmethod
    def product_search():
        """产品搜索测试数据模板"""
        return {
            "keyword": "手机",
            "category": "电子产品",
            "price_min": 100,
            "price_max": 5000
        }
    
    @staticmethod
    def order_creation():
        """订单创建测试数据模板"""
        return {
            "product_id": "{random}",
            "quantity": 1,
            "shipping_address": "测试地址{index}",
            "payment_method": "支付宝"
        }
