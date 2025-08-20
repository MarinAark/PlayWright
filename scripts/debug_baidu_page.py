#!/usr/bin/env python3
"""
百度页面调试脚本
用于诊断元素定位问题
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def debug_baidu_page():
    """调试百度页面结构"""
    async with async_playwright() as p:
        # 启动浏览器（有头模式便于观察）
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🚀 开始调试百度页面...")
            
            # 访问百度首页
            await page.goto("https://www.baidu.com")
            print("✅ 成功访问百度首页")
            
            # 等待页面加载
            await page.wait_for_load_state("networkidle")
            print("✅ 页面加载完成")
            
            # 获取页面基本信息
            title = await page.title()
            url = page.url
            print(f"📄 页面标题: {title}")
            print(f"🌐 页面URL: {url}")
            
            # 检查页面是否包含百度相关元素
            print("\n🔍 检查页面元素...")
            
            # 检查Logo
            logo = await page.query_selector(".logo")
            if logo:
                print("✅ 找到百度Logo")
            else:
                print("❌ 未找到百度Logo")
            
            # 检查搜索按钮
            search_button = await page.query_selector("input[type='submit'], button[type='submit'], .btn")
            if search_button:
                print("✅ 找到搜索按钮")
            else:
                print("❌ 未找到搜索按钮")
            
            # 查找所有input和textarea元素
            print("\n🔍 查找所有输入元素...")
            elements = await page.query_selector_all("input, textarea")
            print(f"📊 找到 {len(elements)} 个input/textarea元素")
            
            for i, element in enumerate(elements):
                try:
                    tag_name = await element.evaluate("el => el.tagName")
                    element_type = await element.get_attribute("type") or "无类型"
                    element_name = await element.get_attribute("name") or "无名称"
                    element_id = await element.get_attribute("id") or "无ID"
                    element_class = await element.get_attribute("class") or "无类名"
                    element_placeholder = await element.get_attribute("placeholder") or "无占位符"
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled()
                    
                    print(f"\n📝 元素 {i+1}:")
                    print(f"  标签: {tag_name}")
                    print(f"  类型: {element_type}")
                    print(f"  名称: {element_name}")
                    print(f"  ID: {element_id}")
                    print(f"  类名: {element_class}")
                    print(f"  占位符: {element_placeholder}")
                    print(f"  可见: {is_visible}")
                    print(f"  启用: {is_enabled}")
                    
                    # 检查是否可能是搜索框
                    if (is_visible and 
                        is_enabled and 
                        (element_type in ["text", "search"] or 
                         element_placeholder or
                         element_name == "wd" or
                         element_id == "kw" or
                         "s_ipt" in element_class)):
                        print("  🎯 这可能是搜索框！")
                        
                        # 尝试点击和输入
                        try:
                            await element.click()
                            await element.fill("测试文本")
                            print("  ✅ 可以点击和输入")
                            
                            # 清空测试文本
                            await element.fill("")
                        except Exception as e:
                            print(f"  ❌ 点击或输入失败: {e}")
                    else:
                        print("  ❌ 不是搜索框")
                        
                except Exception as e:
                    print(f"  ❌ 分析元素 {i+1} 时出错: {e}")
            
            # 尝试使用我们的选择器
            print("\n🔍 测试我们的选择器...")
            selectors = [
                "#kw",
                "input[name='wd']",
                "input[type='text']",
                "input[placeholder*='生万物']",
                "input[placeholder*='百度']",
                "input[placeholder*='请输入']",
                "input[class*='s_ipt']",
                "input[class*='search']",
                "input[id*='kw']",
                "input[autocomplete='off']",
                "textarea[name='wd']",
                ".s_ipt",
                "[class*='s_ipt']",
                "input[type='search']"
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        is_enabled = await element.is_enabled()
                        print(f"✅ 选择器 '{selector}' 找到元素 (可见: {is_visible}, 启用: {is_enabled})")
                        
                        if is_visible and is_enabled:
                            print(f"🎯 选择器 '{selector}' 可用！")
                    else:
                        print(f"❌ 选择器 '{selector}' 未找到元素")
                except Exception as e:
                    print(f"❌ 选择器 '{selector}' 出错: {e}")
            
            # 获取页面HTML片段
            print("\n🔍 获取页面HTML片段...")
            try:
                content = await page.content()
                # 只显示前500个字符
                print("📄 页面HTML片段:")
                print(content[:500])
                print("...")
            except Exception as e:
                print(f"❌ 获取HTML失败: {e}")
            
            # 等待用户观察
            print("\n⏳ 等待30秒，请观察浏览器页面...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ 调试过程中出错: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_baidu_page())
