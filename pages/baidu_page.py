import allure
import time

class BaiduPage:
    def __init__(self, page):
        self.page = page
        self.url = "https://www.baidu.com"
        
        # 多种搜索框定位策略（基于实际百度页面结构）
        self.search_selectors = [
            "#kw",                                 # 主要ID选择器
            "input[name='wd']",                    # 原始name选择器
            "input[type='text']",                  # 按类型定位
            "input[placeholder*='生万物']",         # 按当前占位符定位
            "input[placeholder*='百度']",           # 按占位符定位
            "input[placeholder*='请输入']",         # 按占位符定位
            "input[class*='s_ipt']",               # 按类名定位
            "input[class*='search']",              # 按类名定位
            "input[id*='kw']",                     # 按ID定位
            "input[autocomplete='off']",            # 按属性定位
            "textarea[name='wd']",                 # 可能是textarea
            ".s_ipt",                              # 类选择器
            "[class*='s_ipt']",                    # 通用类选择器
            "input[type='search']",                # 搜索类型
        ]

    @allure.step("访问百度首页")
    def goto(self):
        """访问百度首页并等待页面加载"""
        self.page.goto(self.url)
        # 等待页面完全加载
        self.page.wait_for_load_state("networkidle")
        # 等待页面标题包含"百度"
        self.page.wait_for_function("document.title.includes('百度')")
        
    @allure.step("调试页面结构")
    def debug_page_structure(self):
        """调试页面结构，帮助诊断元素定位问题"""
        try:
            # 获取页面基本信息
            page_title = self.page.title()
            page_url = self.page.url
            
            allure.attach(f"页面标题: {page_title}\n页面URL: {page_url}", "页面基本信息", allure.attachment_type.TEXT)
            
            # 检查页面是否包含百度相关元素
            baidu_logo = self.page.query_selector(".logo")
            if baidu_logo:
                allure.attach("找到百度Logo", "页面元素检查", allure.attachment_type.TEXT)
            else:
                allure.attach("未找到百度Logo", "页面元素检查", allure.attachment_type.TEXT)
            
            # 检查搜索按钮
            search_button = self.page.query_selector("input[type='submit'], button[type='submit'], .btn")
            if search_button:
                allure.attach("找到搜索按钮", "页面元素检查", allure.attachment_type.TEXT)
            else:
                allure.attach("未找到搜索按钮", "页面元素检查", allure.attachment_type.TEXT)
            
            # 获取页面HTML片段用于调试
            try:
                page_content = self.page.content()
                # 只获取前1000个字符避免报告过大
                allure.attach(page_content[:1000], "页面HTML片段", allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"获取页面HTML失败: {str(e)}", "HTML获取错误", allure.attachment_type.TEXT)
                
        except Exception as e:
            allure.attach(f"调试页面结构失败: {str(e)}", "调试错误", allure.attachment_type.TEXT)
        
    @allure.step("查找搜索框")
    def find_search_input(self):
        """使用多种策略查找搜索框"""
        # 首先尝试调试页面结构
        self.debug_page_structure()
        
        for selector in self.search_selectors:
            try:
                # 等待元素出现
                element = self.page.wait_for_selector(selector, timeout=5000)
                if element:
                    # 检查元素是否可见和可编辑
                    if element.is_visible() and element.is_enabled():
                        allure.attach(f"找到搜索框: {selector}", "元素定位成功", allure.attachment_type.TEXT)
                        return element
                    else:
                        allure.attach(f"元素存在但不可见/不可编辑: {selector}", "元素状态", allure.attachment_type.TEXT)
            except Exception as e:
                allure.attach(f"选择器 {selector} 失败: {str(e)}", "元素定位失败", allure.attachment_type.TEXT)
                continue
        
        # 如果所有选择器都失败，尝试更通用的方法
        try:
            # 查找所有input和textarea元素
            elements = self.page.query_selector_all("input, textarea")
            allure.attach(f"找到 {len(elements)} 个input/textarea元素", "通用搜索", allure.attachment_type.TEXT)
            
            for i, element in enumerate(elements):
                try:
                    tag_name = element.tag_name
                    element_type = element.get_attribute("type") or "无类型"
                    element_name = element.get_attribute("name") or "无名称"
                    element_id = element.get_attribute("id") or "无ID"
                    element_class = element.get_attribute("class") or "无类名"
                    element_placeholder = element.get_attribute("placeholder") or "无占位符"
                    is_visible = element.is_visible()
                    is_enabled = element.is_enabled()
                    
                    element_info = f"元素 {i+1}: tag={tag_name}, type={element_type}, name={element_name}, id={element_id}, class={element_class}, placeholder={element_placeholder}, visible={is_visible}, enabled={is_enabled}"
                    allure.attach(element_info, f"元素{i+1}信息", allure.attachment_type.TEXT)
                    
                    if (is_visible and 
                        is_enabled and 
                        (element_type in ["text", "search"] or 
                         element_placeholder or
                         element_name == "wd" or
                         element_id == "kw" or
                         "s_ipt" in element_class)):
                        allure.attach(f"通过通用方法找到搜索框: {element_info}", "备用定位成功", allure.attachment_type.TEXT)
                        return element
                except Exception as e:
                    allure.attach(f"分析元素 {i+1} 时出错: {str(e)}", "元素分析错误", allure.attachment_type.TEXT)
                    continue
        except Exception as e:
            allure.attach(f"通用定位方法失败: {str(e)}", "备用定位失败", allure.attachment_type.TEXT)
        
        raise Exception("无法找到可用的搜索框")

    @allure.step("执行搜索: {keyword}")
    def search(self, keyword):
        """执行搜索操作"""
        # 查找搜索框
        search_input = self.find_search_input()
        
        # 确保元素在视图中
        search_input.scroll_into_view_if_needed()
        
        # 等待元素完全可见
        self.page.wait_for_timeout(1000)
        
        # 清空搜索框并输入关键词
        search_input.click()
        search_input.fill("")
        search_input.type(keyword, delay=100)  # 添加延迟模拟真实输入
        
        # 按回车键搜索
        search_input.press("Enter")
        
        # 等待搜索结果加载
        self.wait_for_search_results()

    @allure.step("等待搜索结果加载")
    def wait_for_search_results(self):
        """等待搜索结果页面加载完成"""
        try:
            # 等待搜索结果容器出现
            self.page.wait_for_selector("#content_left", timeout=10000)
            allure.attach("搜索结果页面加载完成", "页面状态", allure.attachment_type.TEXT)
        except Exception as e:
            # 尝试其他可能的结果选择器
            alternative_selectors = [
                ".result", ".c-container", ".s-result", 
                "[class*='result']", "[class*='content']"
            ]
            
            for selector in alternative_selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=5000)
                    allure.attach(f"使用备用选择器找到结果: {selector}", "备用结果定位", allure.attachment_type.TEXT)
                    return
                except:
                    continue
            
            allure.attach(f"等待搜索结果超时: {str(e)}", "结果加载失败", allure.attachment_type.TEXT)
            raise Exception("搜索结果页面加载超时")

    @allure.step("检查搜索结果")
    def is_result_loaded(self):
        """检查搜索结果是否已加载"""
        try:
            # 检查多种可能的结果选择器
            selectors = ["#content_left", ".result", ".c-container", ".s-result"]
            for selector in selectors:
                if self.page.query_selector(selector):
                    return True
            return False
        except:
            return False

    @allure.step("获取页面标题")
    def get_page_title(self):
        """获取当前页面标题"""
        return self.page.title()

    @allure.step("获取页面URL")
    def get_page_url(self):
        """获取当前页面URL"""
        return self.page.url
