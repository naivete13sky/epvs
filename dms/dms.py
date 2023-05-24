from bs4 import BeautifulSoup
import time
import gl as gl


class DMS():
    pass
    def f3(self):
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



dms = DMS()
dms.f3()
