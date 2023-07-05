import json
import os
import shutil

from PyQt5 import QtCore

from logic.log import MyLog
logger = MyLog.log_init()



class MyThreadStartTranslateG(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc,whichJob,whichTranslateMethod):
        super(MyThreadStartTranslateG, self).__init__()
        self.ussd = cc
        self.whichJob = whichJob
        self.whichTranslateMethod = whichTranslateMethod



    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始G转图！")
        self.trigger.emit("正在G转图！")
        from config_g.g import G
        from epkernel import Input
        from epkernel.Action import Information
        from epkernel import GUI

        #如果料号名被更改了，那么要重新copy一份gerber文件来。
        self.ussd.jobName = self.ussd.lineEditJobName.text()
        self.ussd.tempGerberPath = os.path.join(self.ussd.tempGerberParentPath, self.ussd.jobName)
        if os.path.exists(self.ussd.tempGerberPath):
            # 读取配置文件
            with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            self.gSetupType = self.json['g']['gSetupType']
            self.temp_path = self.json['general']['temp_path']
            if self.gSetupType == 'local':
                # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                shutil.rmtree(self.ussd.tempGerberPath)
            if self.gSetupType == 'vmware':
                # 使用PsExec通过命令删除远程机器的文件
                from ccMethod.ccMethod import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path=r'ccMethod', computer='192.168.1.3',
                                        username='administrator', password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = os.path.join(self.ussd.temp_path_g, 'gerber', self.ussd.jobName)
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)




            shutil.copytree(self.ussd.folder_path, self.ussd.tempGerberPath)
        else:
            shutil.copytree(self.ussd.folder_path, self.ussd.tempGerberPath)

        # 读取配置文件
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.json = json.load(cfg)
        self.gateway_path = self.json['g']['gateway_path']  # (json格式数据)字符串 转化 为字典

        self.gSetupType = self.json['g']['gSetupType']
        self.temp_path = self.json['general']['temp_path']
        self.temp_path_g = self.json['g']['temp_path_g']
        self.GENESIS_DIR = self.json['g']['GENESIS_DIR']
        self.gUserName = self.json['g']['gUserName']


        self.g = G(self.gateway_path,gSetupType=self.gSetupType,GENESIS_DIR=self.GENESIS_DIR,gUserName=self.gUserName)
        # 先清空料号
        if self.gSetupType == 'local':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path,r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path,r'job_list.txt'))
        if self.gSetupType == 'vmware':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path_g, r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path, r'job_list.txt'))

        if self.gSetupType == 'local':
            self.temp_path_g = self.temp_path

        gerberList_path = []
        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            each_dict = {}
            gerberFolderPathG = os.path.join(self.temp_path_g,'gerber', self.ussd.jobName)

            each_dict['path'] = os.path.join(gerberFolderPathG, self.ussd.tableWidgetGerber.item(row, 0).text())
            if self.ussd.tableWidgetGerber.item(row, 1).text() in ['Excellon2', 'excellon2', 'Excellon', 'excellon']:
                each_dict['file_type'] = 'excellon'
                each_dict_para = {}
                each_dict_para['zeroes'] = self.ussd.tableWidgetGerber.item(row, 2).text()
                each_dict_para['nf1'] = int(self.ussd.tableWidgetGerber.item(row, 3).text())
                each_dict_para['nf2'] = int(self.ussd.tableWidgetGerber.item(row, 4).text())
                each_dict_para['units'] = self.ussd.tableWidgetGerber.item(row, 5).text()
                each_dict_para['tool_units'] = self.ussd.tableWidgetGerber.item(row, 6).text()
                each_dict['para'] = each_dict_para
                gerberList_path.append(each_dict)
            elif self.ussd.tableWidgetGerber.item(row, 1).text() in ['Gerber274x', 'gerber274x']:
                each_dict['file_type'] = 'gerber'
                gerberList_path.append(each_dict)
            else:
                each_dict['file_type'] = ''
            # gerberList_path.append(each_dict)




        self.g.input_init(job=self.ussd.jobName, step=self.ussd.step, gerberList_path=gerberList_path,jsonPath=r'settings\epvs.json')


        out_path_g = os.path.join(self.temp_path_g, r'odb')
        self.g.g_export(self.ussd.jobName, out_path_g, mode_type='directory')
        self.g.g_export(self.ussd.jobName, out_path_g, mode_type='tar_gzip')

        out_path_local = self.ussd.tempODBParentPath
        Input.open_job(self.ussd.jobName, out_path_local)  # 用悦谱CAM打开料号
        # GUI.show_layer(self.jobNameG, self.step, "")

        # G转图情况，更新到表格中
        all_layers_list_job = Information.get_layers(self.ussd.jobName)


        for row in range(self.ussd.tableWidgetGerber.rowCount()):

            current_layerName = self.ussd.tableWidgetGerber.item(row, 0).text().lower()
            if current_layerName in all_layers_list_job:
                self.trigger.emit("更新料号"+self.whichJob+'转图结果|'+self.ussd.translateMethod+'|'+str(row)+'|'+current_layerName)

        self.trigger.emit("已完成G转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")
        all_step_list_job = Information.get_steps(self.ussd.jobName)
        if len(all_layers_list_job) > 0:
            self.trigger.emit("料号转图完成|"+self.whichJob+'|'+self.ussd.translateMethod)
        #把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。
        logger.info("把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。")
        self.g.input_reset(self.ussd.jobName)