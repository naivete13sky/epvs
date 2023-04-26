import json
import os,shutil
import subprocess
import time


LAYER_COMPARE_JSON = 'layer_compare.json'


class G():
    def __init__(self,gateway_path):
        self.gateway_path=gateway_path
        command0 = 'SET GENESIS_DIR=C:/Program Files/shareg'
        command = '{} 1'.format(self.gateway_path)
        self.process = subprocess.Popen(command0 + "&" + command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    def __del__(self):
        os.system('taskkill /f /im gateway.exe')


    def exec_cmd(self, cmd):
        self.process.stdin.write((cmd + '\n').encode())
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        ret = int(line.decode().strip())
        return ret


    def import_odb_folder(self, jobpath,*args,**kwargs):
        print('import job')
        results=[]
        self.jobpath = jobpath
        if "job_name" in kwargs:
            job_name = kwargs['job_name']
        else:
            job_name = os.path.basename(self.jobpath)
        cmd_list = [
            'COM import_job,db=genesis,path={},name={},analyze_surfaces=no'.format(jobpath, job_name.lower()),
        ]
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            results=results.append(ret)
        return results


    def delete_job(self,job_name):
        pass
        cmd_list = [
            'COM close_job,job={}'.format(job_name),
            'COM close_form,job={}'.format(job_name),
            'COM close_flow,job={}'.format(job_name),
            'COM delete_entity,job=,type=job,name={}'.format(job_name),
            'COM close_form,job={}'.format(job_name),
            'COM close_flow,job={}'.format(job_name)
        ]

        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print(ret)
            if ret != 0:
                print('inner error')
                # return
        return "clean finish!"

    def clean_g_all_pre_get_job_list(self,job_list_path):
        pass
        cmd_list = [
            'COM info,args=-t root -m display -d JOBS_LIST,out_file={},write_mode=replace,units=inch'.format(job_list_path)
        ]

        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print(ret)
            if ret != 0:
                print('inner error')
        return "已生成job_list!"

    def clean_g_all_do_clean(self,job_list_path):
        with open(job_list_path, "r") as f:
            s = f.readlines()
        print(s)

        for each_job in s:

            job_name = each_job.split("=")[1]
            self.delete_job(job_name)

        return "clean finish!"

    def Create_Entity(self, job, step):
        print("*"*100,job,step)
        cmd_list1 = [
            # 'COM abc',
            'COM create_entity,job=,is_fw=no,type=job,name={},db=genesis,fw_type=form'.format(job),
            'COM create_entity,job={},is_fw=no,type=step,name={},db=genesis,fw_type=form'.format(job, step),
            'COM save_job,job={},override=no'.format(job)
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print("*"*100,ret)
            if ret != 0:
                print('inner error')
                return False
        return True

    def save_job(self, job):
        print("save")
        results = []

        cmd_list1 = [
            'COM save_job,job={},override=no'.format(job),
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            if ret != 0:
                print('inner error')
                return results

        time.sleep(1)


    def input_init(self, *, job: str,step='orig',gerberList_path:list,out_path):
        self.job = job
        self.step = step
        self.gerberList_path = gerberList_path
        self.out_path = out_path
        self.input_set_para_default()
        kw = {}
        self.in_put(self.job,self.step,self.gerberList_path,self.out_path,**kw)

    def input_set_para_default(self):
        # 设置默认导入参数
        with open(r'C:\cc\python\epwork\epvs\config_g\config.json', 'r') as cfg:
            self.para = json.load(cfg)['input']  # (json格式数据)字符串 转化 为字典
            print("self.para::",self.para)

    def input_set_para_customer(self,customer_para:dict):
        pass
        print('customer_para:',customer_para)
        for each in customer_para:
            print(each)
            self.para[each] = customer_para[each]
        print(self.para)
        print("cc")


    def in_put(self,job_name, step, gerberList_path, out_path,*args,**kwargs):
        # 先创建job, step
        jobpath = r'C:\genesis\fw\jobs' + '/' + job_name
        results = []
        if os.path.exists(jobpath):
            shutil.rmtree(jobpath)
        self.Create_Entity(job_name, step)
        for each in gerberList_path:
            result = {}
            result['gerberPath'] = each["path"]
            result['result'] = self.gerber_to_odb_one_file(each,*args,**kwargs)
            results.append(result)
        self.save_job(self.job)
        return results

    def gerber_to_odb_one_file(self,eachGerberInfo, *args,**kwargs):
        self.para['job'] = self.job
        self.para['step'] = self.step
        self.para['format'] = 'Gerber274x'
        self.para['separator'] = '*'
        self.para['path'] = eachGerberInfo['path']
        self.para['layer'] = os.path.basename(eachGerberInfo['path']).lower()
        self.para['layer']=self.para['layer'].replace(' ','-').replace('(', '-').replace(')', '-')
        print("iamcc",'kwargs:',kwargs)
        file_type = eachGerberInfo["file_type"]


        if file_type == 'excellon':
            print("I am drill")
            self.para['format'] = 'Excellon2'
            if eachGerberInfo.get('para'):
                self.para['zeroes'] = eachGerberInfo['para']['zeroes']
                self.para['nf1'] = eachGerberInfo['para']['nf1']
                self.para['nf2'] = eachGerberInfo['para']['nf2']
                self.para['units'] = eachGerberInfo['para']['units']
                self.para['tool_units'] = eachGerberInfo['para']['tool_units']
                self.para['separator'] = 'nl'
            else:
                self.para['zeroes'] = 'leading'
                self.para['nf1'] = "2"
                self.para['nf2'] = "4"
                self.para['units'] = 'inch'
                self.para['tool_units'] = 'inch'
                self.para['separator'] = 'nl'



        trans_COM = 'COM input_manual_set,'
        trans_COM += 'path={},job={},step={},format={},data_type={},units={},coordinates={},zeroes={},'.format(
            self.para['path'].replace("\\","/"),
            self.para['job'],
            self.para['step'],
            self.para['format'],
            self.para['data_type'],
            self.para['units'],
            self.para['coordinates'],
            self.para['zeroes'])
        trans_COM += 'nf1={},nf2={},decimal={},separator={},tool_units={},layer={},wheel={},wheel_template={},'.format(
            self.para['nf1'],
            self.para['nf2'],
            self.para['decimal'],
            self.para['separator'],
            self.para['tool_units'],
            self.para['layer'],
            self.para['wheel'],
            self.para['wheel_template'])
        trans_COM += 'nf_comp={},multiplier={},text_line_width={},signed_coords={},break_sr={},drill_only={},'.format(
            self.para['nf_comp'],
            self.para['multiplier'],
            self.para['text_line_width'],
            self.para['signed_coords'],
            self.para['break_sr'],
            self.para['drill_only'])
        trans_COM += 'merge_by_rule={},threshold={},resolution={}'.format(
            self.para['merge_by_rule'],
            self.para['threshold'],
            self.para['resolution'])



        cmd_list1 = [
            'COM input_manual_reset',
            trans_COM,
            ('COM input_manual,script_path={}'.format(''))
        ]


        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            if ret != 0:
                print('inner error')
                return False
        return True

    def g_export(self,job,export_to_path):
        print("导出--开始")
        cmd_list1 = [
            'COM export_job,job={},path={},mode=tar_gzip,submode=full,overwrite=yes'.format(job,export_to_path),
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)

            if ret != 0:
                print('inner error')
                return False
        print("导出--结束")
        return True


if __name__ == '__main__':
    g = G(r"C:\cc\python\epwork\epvs\config_g\bin\gateway.exe")

    #删除所有料号
    g.clean_g_all_pre_get_job_list(r'//vmware-host/Shared Folders/share/job_list.txt')
    g.clean_g_all_do_clean(r'C:\cc\share\job_list.txt')
    g.import_odb_folder(r'C:\temp\biz22351_ep')

    job_name = 'test'
    step = 'orig'
    gerberList_path = [{"path":r"C:\temp\gerber\nca60led\Polaris_600_LED.DRD","file_type":"excellon"},
                       {"path":r"C:\temp\gerber\nca60led\Polaris_600_LED.TOP","file_type":"gerber"}]
    out_path = r'C:\temp\g\output'
    g.input_init(job=job_name, step=step, gerberList_path=gerberList_path, out_path=out_path)
    # 输出tgz到指定目录
    g.g_export(job_name, out_path)