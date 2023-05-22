from bs4 import BeautifulSoup
from pyppeteer import launch
import pyppeteer
import asyncio
import time


class DMS():


    def f1(self):
        pyppeteer.DEBUG = False
        loop = asyncio.get_event_loop()

        # print("*" * 30, "log in", "*" * 30)
        task = asyncio.ensure_future(self.login('wangyufeng-wwyg', 'Cc123456*', 'http://10.97.80.119/admin/login/'))

        print("*" * 30, "Begin log in DMS", "*" * 30)

        loop.run_until_complete(task)

        # self.browser = task.result()
        print("*" * 30, "init finish", "*" * 30)

    async def login(self, username, password, url):
        # 'headless': False如果想要浏览器隐藏更改False为True
        self.browser = await launch({'headless': False, 'args': ['--no-sandbox']})
        self.page = await self.browser.newPage()
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
        await self.page.goto(url)
        # await self.page.type(gl.css_login_user, username)  # 输入用户名
        # await self.page.type(gl.css_login_pwd, password)  # 输入密码
        # # 获取验证码，先找到图片，再保存到本地
        # html_content = await self.page.content()
        # soup = BeautifulSoup(html_content, 'html.parser')
        # mask_code_png_src = soup.find_all('img')[4].get('src')
        # encode_img = mask_code_png_src.split(',')[1]
        #
        # await self.page.type(gl.css_login_mask_code, mask_code)
        # await self.page.click('#app > div > div.login-panel > div > button')  # 点击登录
        time.sleep(10)
        return self.page


cc = DMS()
cc.f1()