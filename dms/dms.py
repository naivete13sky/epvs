from bs4 import BeautifulSoup
import time



class DMS():
    def login(self,username,password):
        import requests
        from bs4 import BeautifulSoup

        # 登录系统的URL
        login_url = 'http://10.97.80.119/admin/login/'

        # 用户名和密码
        username = username
        password = password

        # 创建一个会话
        self.session = requests.Session()

        # 打开登录页面，获取csrf码
        response = self.session.get(login_url)
        # print(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')
        input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        input_content = input_tag.get('value')
        # print('登录页面csrf', input_content)

        # 发送POST请求，登录系统
        login_data = {
            'csrfmiddlewaretoken': input_content,
            'username': username,
            'password': password,
            'next': '/admin/'
        }
        response = self.session.post(login_url, data=login_data)
        # print(response.text)

        # 检查登录是否成功
        if '注销' in response.text:
            print('登录DMS成功！')
            # 这个会话现在可以用于后续的请求，保持登录状态
            # 在这里可以执行其他操作，如获取数据、访问其他页面等
            return {'result':True,'info':''}
        else:
            print('登录失败！')
            soup = BeautifulSoup(response.text, 'html.parser')
            alert_tag = soup.find('el-alert')
            alert_tag_content = alert_tag['title']
            # print('alert_tag_content:',alert_tag_content)
            return {'result':False,'info':alert_tag_content}

    def add_main_job(self,job_name,has_file_type,status,from_object_pcb_factory,from_object_pcb_design,tags,remark,epvs_search_id,file_path):
        from bs4 import BeautifulSoup

        # 打开主料号页面，获取csrf
        main_job_url = 'http://10.97.80.119/admin/job/job/add/'
        response = self.session.get(main_job_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        input_content = input_tag.get('value')
        print('主料号新增页面csrf',input_content)

        # 发送POST请求，录入主料号
        # 文件路径
        file_path = file_path
        # print('file_path:',file_path)

        # 构建文件对象
        files = {
            'file_compressed': open(file_path, 'rb')  # 文件字段
        }

        post_data = {
            'csrfmiddlewaretoken': input_content,
            'job_name': job_name,
            # 'file_compressed': ('760.rar', file_data,'application/octet-stream'),
            'has_file_type': has_file_type,
            'status':status,
            'from_object_pcb_factory': from_object_pcb_factory,
            'from_object_pcb_design': from_object_pcb_design,
            'tags': tags,
            'remark': remark,
            'epvs_search_id': epvs_search_id,
            '_save': '',
            'actionName': 'actionValue',
        }

        # 构建请求头
        headers = {
            'Content-Type': 'application/octet-stream',
        }


        response = self.session.post(main_job_url, data=post_data,files=files)

        print('status_code:',response.status_code)




    def add_test_job(self,job_parent,job_name,file_type,test_usage_for_epcam_module,vs_result_ep,vs_result_g,
                     bug_info,bool_layer_info,vs_time_ep,vs_time_g,
                     status,author,tags,remark,epvs_search_id,
                     file_path_org,file_path_std):
        from bs4 import BeautifulSoup

        # 打开主料号页面，获取csrf
        test_job_url = 'http://10.97.80.119/admin/eptest/jobfortest/add/'
        response = self.session.get(test_job_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        input_content = input_tag.get('value')
        print('测试料号新增页面csrf',input_content)

        # 发送POST请求，录入主料号
        # 文件路径
        file_path_org = file_path_org
        file_path_std = file_path_std
        # print('file_path:',file_path)

        # 构建文件对象
        files = {
            'file': open(file_path_org, 'rb'),  # 文件字段
            'standard_odb': open(file_path_std, 'rb')  # 文件字段
        }

        post_data = {
            'csrfmiddlewaretoken': input_content,
            'job_parent':job_parent,
            'job_name': job_name,
            'file_type': file_type,
            'test_usage_for_epcam_module':test_usage_for_epcam_module,
            'vs_result_ep':vs_result_ep,
            'vs_result_g': vs_result_g,
            'bug_info':bug_info,
            'bool_layer_info':bool_layer_info,
            'vs_time_ep':vs_time_ep,
            'vs_time_g': vs_time_g,
            'status':status,
            'author': author,
            'tags': tags,
            'remark': remark,
            'epvs_search_id': epvs_search_id,
            '_save': '',
            'actionName': 'actionValue',
        }

        # 构建请求头
        headers = {
            'Content-Type': 'application/octet-stream',
        }


        response = self.session.post(test_job_url, data=post_data,files=files)

        print('status_code:',response.status_code)
        # print('response:',response.text)




    def get_layer_name_from_org(self,test_job_id):
        pass

        url = 'http://10.97.80.119/eptest/get_layer_name_from_org/{}/'.format(str(test_job_id))
        # print(url)
        response = self.session.get(url)
        print('response.status_code:',response.status_code)




    def update_layer_para0(self,test_layer_id,layer_file_type,layer_type,units,coordinates,zeroes_omitted,
                          number_format_A,number_format_B,tool_units_ep,tool_units_g,status,remark):
        pass

        url = 'http://10.97.80.119/admin/eptest/layer/?q={}'.format(str(test_layer_id))
        # # print(url)
        response = self.session.get(url)
        # print('response.status_code:',response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        input_content = input_tag.get('value')
        # print('input_content:',input_content)

        post_data = {
            'csrfmiddlewaretoken': input_content,
            'form-TOTAL_FORMS':1,
            'form-INITIAL_FORMS':1,
            'form-MIN_NUM_FORMS':0,
            'form-MAX_NUM_FORMS':1000,
            'action': '',
            'select_across': 0,
            '_save': '保存',
            'form-0-id': test_layer_id,
            'form-0-layer_file_type': layer_file_type,
            'form-0-layer_type': layer_type,
            'form-0-units': units,
            'form-0-coordinates': coordinates,
            'form-0-zeroes_omitted': zeroes_omitted,
            'form-0-number_format_A': number_format_A,
            'form-0-number_format_B': number_format_B,
            'form-0-tool_units_ep': tool_units_ep,
            'form-0-tool_units_g': tool_units_g,
            'form-0-status': status,
            'form-0-remark': remark
        }

        # 构建请求头
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        url_update_layer = r''
        response = self.session.post(url, data=post_data)

        print('status_code:', response.status_code)

    def update_layer_para(self,test_layer_id,job,layer,layer_org,vs_result_manual,vs_result_ep,vs_result_g,
                          layer_file_type,layer_type,features_count,
                          units,coordinates,zeroes_omitted,number_format_A,number_format_B,tool_units_ep,tool_units_g,
                          author,status,vs_time_ep,vs_time_g,remark):
        pass


        url = 'http://10.97.80.119/admin/eptest/layer/{}/change/?_changelist_filters=q%3D{}'.format(str(test_layer_id),str(test_layer_id))
        # # print(url)
        response = self.session.get(url)
        # print('response.status_code:',response.status_code)
        soup = BeautifulSoup(response.text, 'html.parser')
        input_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        input_content = input_tag.get('value')
        print('input_content:',input_content)

        post_data = {
            'csrfmiddlewaretoken': input_content,
            'job':job,
            'layer':layer,
            'layer_org':layer_org,
            'vs_result_manual':vs_result_manual,
            'vs_result_ep':vs_result_ep,
            'vs_result_g': vs_result_g,
            'layer_file_type': layer_file_type,
            'layer_type': layer_type,
            'features_count':features_count,
            'units': units,
            'coordinates': coordinates,
            'zeroes_omitted': zeroes_omitted,
            'number_format_A': number_format_A,
            'number_format_B': number_format_B,
            'tool_units_ep': tool_units_ep,
            'tool_units_g': tool_units_g,
            'author': author,
            'status': status,
            'vs_time_ep':vs_time_ep,
            'vs_time_g': vs_time_g,
            'remark': remark,
            '_save':'',
            'actionName':'actionValue'
        }
        # print(post_data)
        # 构建请求头
        headers = {
            'Content-Type': 'application/octet-stream',
        }
        url_update_layer = r''
        response = self.session.post(url, data=post_data)

        print('status_code:', response.status_code)


def main_job_test():
    pass
    dms = DMS()
    dms.login('cc', 'cc')

    job_name = 'cctest7'
    has_file_type = ['gerber274x', 'gerber274d', 'dxf', 'dwg']
    status = 'draft'
    from_object_pcb_factory = ''
    from_object_pcb_design = ''
    tags = 'test'
    remark = '备注'

    dms.add_main_job(job_name=job_name, has_file_type=has_file_type, status=status,
                     from_object_pcb_factory=from_object_pcb_factory, from_object_pcb_design=from_object_pcb_factory,
                     tags=tags, remark=remark)

def test_job_test():
    pass
    dms = DMS()
    dms.login('cc', 'cc')

    job_parent = '1773'
    job_name = 'cctest7'
    file_type = 'gerber274X'
    test_usage_for_epcam_module = '8'
    vs_result_ep = 'none'
    vs_result_g = 'passed'
    bug_info = ''
    bool_layer_info = 'false'
    vs_time_ep = ''
    vs_time_g = ''
    status = 'draft'
    author = '1'
    tags = 'test'
    remark = '备注'
    file_path_org = r"C:\Users\cheng.chen\Desktop\nca60led.rar"
    file_path_std = r"C:\Users\cheng.chen\Desktop\nca60led.rar"

    dms.add_test_job(job_parent=job_parent,
                     job_name=job_name,
                     file_type=file_type,
                     test_usage_for_epcam_module=test_usage_for_epcam_module,
                     vs_result_ep=vs_result_ep,
                     vs_result_g=vs_result_g,
                     bug_info=bug_info,
                     bool_layer_info=bool_layer_info,
                     vs_time_ep=vs_time_ep,
                     vs_time_g=vs_time_g,
                     status=status,
                     author=author,
                     tags=tags,
                     remark=remark,
                     file_path_org=file_path_org,
                     file_path_std=file_path_std)

def test_job_update_layer_test():
    dms = DMS()
    dms.login('cc', 'cc')

    test_layer_id=110173
    job=16770
    layer='Polaris_600_LED.DRD'
    layer_org='Polaris_600_LED.DRD'
    vs_result_manual = 'none'
    vs_result_ep = 'none'
    vs_result_g = 'none'
    layer_file_type='excellon2'
    layer_type='drill'
    features_count = 0
    units='Inch'
    coordinates = 'none'
    zeroes_omitted='Leading'
    number_format_A=2
    number_format_B=4
    tool_units_ep='Inch'
    tool_units_g='Inch'
    author=''
    status='published'
    vs_time_ep=''
    vs_time_g = ''
    remark='epvs_update12'




    dms.update_layer_para(test_layer_id=test_layer_id,
                          job=job,
                          layer=layer,
                          layer_org=layer_org,
                          vs_result_manual=vs_result_manual,
                          vs_result_ep=vs_result_ep,
                          vs_result_g=vs_result_g,
                          layer_file_type=layer_file_type,
                          layer_type=layer_type,
                          features_count=features_count,
                          units=units,
                          coordinates=coordinates,
                          zeroes_omitted=zeroes_omitted,
                          number_format_A=number_format_A,
                          number_format_B=number_format_B,
                          tool_units_ep=tool_units_ep,
                          tool_units_g=tool_units_g,
                          author=author,
                          status=status,
                          vs_time_ep=vs_time_ep,
                          vs_time_g=vs_time_g,
                          remark=remark)





if __name__ == '__main__':

    pass
    test_job_update_layer_test()
    # dms = DMS()
    # dms.login('cc', 'cc')
    # dms.get_layer_name_from_org(16762)
