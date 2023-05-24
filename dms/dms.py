from bs4 import BeautifulSoup
from pyppeteer import launch
import pyppeteer
import asyncio
import time

import gl as gl

class DMS2():
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

        width, height = 1920, 1080  # 尺寸配置
        self.browser = await launch({'headless': False,# 'headless': False如果想要浏览器隐藏更改False为True
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
        # time.sleep(100)
        return self.page

    async def job_test_add(self):
        pass
        print('job_test_add')
        await self.page.goto('http://10.97.80.119/admin/#/admin/eptest/jobfortest/')
        await asyncio.sleep(1)
        await self.page.close()





class DMS:
    def __init__(self):
        self.browser = None
        self.page = None

    async def login(self):
        width, height = 1920, 1080  # 尺寸配置
        self.browser = await launch({'headless': False,  # 'headless': False如果想要浏览器隐藏更改False为True
                                     'args': ['--disable-infobars',  # 关闭自动化提示框
                                              '--no-sandbox',  # 关闭沙盒模式
                                              '--start-maximized',  # 窗口最大化模式
                                              ]})
        self.page = await self.browser.newPage()
        await self.page.setViewport({'width': width, 'height': height})
        await self.page.setUserAgent(
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')
        await self.page.goto(gl.url_login)
        await self.page.type(gl.css_login_user, 'cc')  # 输入用户名
        await self.page.type(gl.css_login_pwd, 'cc')  # 输入密码
        await self.page.click(gl.css_login_confirm)  # 点击登录
        await asyncio.sleep(0.5)
        # await self.page.waitForNavigation()  # 等待页面跳转完成

    async def open_page(self):
        # await self.page.click('#main > section > aside > ul > div > li:nth-child(3) > div')  # 点击左侧菜单项，例如通过元素ID选择菜单项
        # await self.page.click('#main > section > aside > ul > div > li.el-submenu.is-opened > ul > div > li:nth-child(1) > span')#点击测试料号菜单
        # await self.page.waitForNavigation()  # 等待页面跳转完成
        await self.page.goto('http://10.97.80.119/admin/eptest/jobfortest/add/')
        await self.page.type('#id_job_name','abc')



        # 进行其他操作...
        await asyncio.sleep(100)

    async def run(self):
        self.browser = await launch()
        self.page = await self.browser.newPage()

        await self.login()  # 执行登录操作
        await self.open_page()  # 执行打开指定页面操作

        await self.browser.close()

async def main():
    dms = DMS()
    await dms.run()

# asyncio.get_event_loop().run_until_complete(main())



def f3():
    pass
    import requests
    from bs4 import BeautifulSoup

    # 登录系统的URL
    login_url = 'http://10.97.80.119/admin/login/'

    # 用户名和密码
    username = 'cc'
    password = 'cc'

    # 创建一个会话
    session = requests.Session()

    # 打开登录页面，获取csrf码
    response = session.get(login_url)
    # print(response.text)

    soup = BeautifulSoup(response.text, 'html.parser')
    input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    input_content = input_tag.get('value')
    print('登录页面csrf',input_content)



    # 发送POST请求，登录系统
    login_data = {
        'csrfmiddlewaretoken': input_content,
        'username': 'cc',
        'password':'cc',
        'next':'/admin/'
    }
    response = session.post(login_url, data=login_data)

    # 检查登录是否成功
    if response.status_code == 200:
        print('登录成功！')
        # 这个会话现在可以用于后续的请求，保持登录状态
        # 在这里可以执行其他操作，如获取数据、访问其他页面等
    else:
        print('登录失败！')

    # 打开主料号页面，获取csrf
    main_job_url = 'http://10.97.80.119/admin/job/job/add/'
    response = session.get(main_job_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    input_content = input_tag.get('value')
    print('主料号新增页面csrf',input_content)

    # 发送POST请求，录入主料号
    # 文件路径
    file_path = r"C:\Users\cheng.chen\Desktop\760.rar"

    # 构建文件对象
    files = {
        'file_compressed': open(file_path, 'rb')  # 文件字段
    }

    post_data = {
        'csrfmiddlewaretoken': input_content,
        'job_name': 'cctest7',
        # 'file_compressed': ('760.rar', file_data,'application/octet-stream'),
        'has_file_type': 'gerber274x',
        'status':'draft',
        'from_object_pcb_factory': '',
        'from_object_pcb_design': '',
        'tags': 'test',
        'remark': 'cctest',
        '_save': '',
        'actionName': 'actionValue',
    }

    # 构建请求头
    headers = {
        'Content-Type': 'application/octet-stream',
    }


    response = session.post(main_job_url, data=post_data,files=files)

    print('status_code:',response.status_code)
    # print('response:',response.text)
    # 检查登录是否成功
    if response.status_code == 200:
        print('登录成功！')
        # 这个会话现在可以用于后续的请求，保持登录状态
        # 在这里可以执行其他操作，如获取数据、访问其他页面等
    else:
        print('登录失败！')




f3()