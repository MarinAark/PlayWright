import allure

class BaiduPage:
    def __init__(self, page):
        self.page = page
        self.url = "https://www.baidu.com"

    def goto(self):
        self.page.goto(self.url)

    def search(self, keyword):
        self.page.fill("input[name='wd']", keyword)
        self.page.press("input[name='wd']", "Enter")

    def is_result_loaded(self):
        return self.page.wait_for_selector("#content_left")
