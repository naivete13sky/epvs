from bs4 import BeautifulSoup
from pyppeteer import launch
import pyppeteer
import asyncio
import time

import gl as gl

class DMS():
    def f1(self):
        pyppeteer.DEBUG = False
        loop = asyncio.get_event_loop()
        # print("*" * 30, "log in", "*" * 30)
        task = asyncio.ensure_future(self.login('cc', 'cc', gl.url_login))
        print("*" * 30, "Begin log in DMS", "*" * 30)
        loop.run_until_complete(task)
        print("*" * 30, "init finish", "*" * 30)

        task = asyncio.ensure_future(self.job_test_add())
        loop.run_until_complete(task)

    async def login(self, username, password, url):
        # 'headless': False如果想要浏览器隐藏更改False为True
        width, height = 1920, 1080  # 尺寸配置
        self.browser = await launch({'headless': False,
                                     'args': ['--disable-infobars',  # 关闭自动化提示框
                                              '--no-sandbox',# 关闭沙盒模式
                                              '--start-maximized',# 窗口最大化模式
                                              ]})
        self.page = await self.browser.newPage()
        await self.page.setViewport({'width': width, 'height': height})
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')






        await self.page.goto(url)
        await self.page.type(gl.css_login_user, username)  # 输入用户名
        await self.page.type(gl.css_login_pwd, password)  # 输入密码
        await self.page.click(gl.css_login_confirm)  # 点击登录
        time.sleep(100)
        return self.page

    async def job_test_add(self):
        pass
        print('job_test_add')
        await asyncio.sleep(1)
        await self.page.close()


dms = DMS()
dms.f1()
