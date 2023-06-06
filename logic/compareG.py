import json
import os
import shutil
import time

from PyQt5 import QtCore
from epkernel import GUI, Input
from epkernel.Action import Information


from logic.log import MyLog
logger = MyLog.log_init()


class MyThreadStartCompareG(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc):
        super(MyThreadStartCompareG, self).__init__()
        self.ussd = cc

    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始G比图！")
        self.trigger.emit("正在G比图！")
        from epkernel.Edition import Job, Matrix,Layers
        from epkernel import Input, BASE
        from config_g.g import G

        # 读取配置文件
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.json = json.load(cfg)
        self.gateway_path = self.json['g']['gateway_path']  # (json格式数据)字符串 转化 为字典

        self.gSetupType = self.json['g']['gSetupType']
        self.GENESIS_DIR = self.json['g']['GENESIS_DIR']
        self.temp_path = self.json['general']['temp_path']
        self.temp_path_g = self.json['g']['temp_path_g']
        self.gUserName = self.json['g']['gUserName']
        self.g = G(self.gateway_path, gSetupType=self.gSetupType, GENESIS_DIR=self.GENESIS_DIR,gUserName=self.gUserName)




        #料号A与料号B转图来源，是input还是import
        if self.ussd.FlagInputA:
            job2 = self.ussd.dialogInputA.jobName
            step2 = self.ussd.dialogInputA.step
        if self.ussd.FlagImportA:
            job2 = self.ussd.dialogImportA.jobName
            step2 = self.ussd.dialogImportA.step
        if self.ussd.FlagInputB:
            job1 = self.ussd.dialogInputB.jobName
            step1 = self.ussd.dialogInputB.step
            tempGOutputPathCompareResult = self.ussd.dialogInputB.tempGOutputPathCompareResult
        if self.ussd.FlagImportB:
            job1 = self.ussd.dialogImportB.jobName
            step1 = self.ussd.dialogImportB.step
            tempGOutputPathCompareResult = self.ussd.dialogImportB.tempGOutputPathCompareResult


        if self.ussd.FlagInputA and self.ussd.FlagInputB:
            #当料号A与料号B都是Input转图时
            pass
            #找出料号A与料号B共同的层名。只有共同层才需要比图。
            jobAList = [(self.ussd.dialogInputA.tableWidgetGerber.item(each, 0).text(),self.ussd.dialogInputA.tableWidgetGerber.item(each, 1).text()) for each in
                        range(self.ussd.dialogInputA.tableWidgetGerber.rowCount())]

            jobBList = [(self.ussd.dialogInputB.tableWidgetGerber.item(each, 0).text(),self.ussd.dialogInputB.tableWidgetGerber.item(each, 1).text()) for each in
                        range(self.ussd.dialogInputB.tableWidgetGerber.rowCount())]

            setA = set(jobAList)
            setB = set(jobBList)
            intersection = setA.intersection(setB)
            jobABList = list(intersection)

            jobABLayerNameList = [each[0] for each in jobABList]


            layerInfo = []

            for row in range(self.ussd.tableWidgetVS.rowCount()):
                if self.ussd.tableWidgetVS.item(row, 0).text() in jobABLayerNameList:
                    pass
                    each_dict = {}
                    each_file = self.ussd.tableWidgetVS.item(row, 0).text()

                    each_dict["layer"] = each_file.lower()

                    for each in jobABList:
                        if each[0] == each_file:
                            if each[1] in ['Excellon2','excellon2','Excellon','excellon']:
                                each_dict['layer_type'] = 'drill'
                            else:
                                each_dict['layer_type'] = ''
                    layerInfo.append(each_dict)
        else:
            pass
            #料号A与料号B至少有一个不是Input转图的，这个时候要比图的层通过总表来判断，看看哪些层是2个料号里都存在转图成功的。
            logger.info("料号A与料号B至少有一个不是Input转图的，这个时候要比图的层通过总表来判断，看看哪些层是2个料号里都存在转图成功的。")



            # 找出料号A与料号B共同的层名。只有共同层才需要比图。
            jobAList = [(each,"") for each in Information.get_layers(job2)]

            jobBList = [(each,"") for each in Information.get_layers(job1)]

            setA = set(jobAList)
            setB = set(jobBList)
            intersection = setA.intersection(setB)
            jobABList = list(intersection)

            jobABLayerNameList = [each[0] for each in jobABList]

            layerInfo = []

            for row in range(self.ussd.tableWidgetVS.rowCount()):
                if self.ussd.tableWidgetVS.item(row, 0).text().lower() in jobABLayerNameList:
                    pass
                    each_dict = {}
                    each_file = self.ussd.tableWidgetVS.item(row, 0).text()

                    each_dict["layer"] = each_file.lower()
                    each_dict['layer_type'] = ''#所有层都不区分是gerber还是孔了。
                    layerInfo.append(each_dict)




        logger.info('layerInfo:'+str(layerInfo))





        # 先清空料号
        if self.gSetupType == 'local':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path, r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path, r'job_list.txt'))
        if self.gSetupType == 'vmware':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path_g, r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path, r'job_list.txt'))



        #导料号
        if self.gSetupType == 'local':
            self.temp_path_g = self.temp_path

        self.g.import_odb_folder(os.path.join(self.temp_path_g,  r'odb',job1))
        self.g.import_odb_folder(os.path.join(self.temp_path_g, r'odb', job2))

        self.g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)
        # adjust_position = True表示 在孔有错位时尝试做一次对齐
        compareResult = self.g.layer_compare(temp_path=self.temp_path,temp_path_g=self.temp_path_g,
            job1=job1, step1=step1,
            job2=job2, step2=step2,
            layerInfo=layerInfo,
            adjust_position=True,jsonPath=r'settings/epvs.json')
        logger.info('compareResult:'+str(compareResult))
        self.trigger.emit("compareResult:"+str(compareResult))

        for row in range(self.ussd.tableWidgetVS.rowCount()):
            pass
            each_file = self.ussd.tableWidgetVS.item(row, 0).text().lower()
            each_file_compare_result = compareResult.get('all_result_g').get(each_file)

            self.trigger.emit(each_file_compare_result)
            self.trigger.emit("更新G比图结果|" + str(row) + '|' + str(each_file_compare_result))





        #G比图后保存一下jobNameG
        self.g.save_job(job1)
        out_path_g_with_compare_result = os.path.join(self.temp_path_g, r'output_compare_result')
        self.g.g_export(job1, out_path_g_with_compare_result, mode_type='directory')
        # 改一下odb料号名称
        self.ussd.jobNameGCompareResult = job1 + '_comRes'
        if os.path.exists(os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult)):
            shutil.rmtree(os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult))
            time.sleep(1)

        os.rename(os.path.join(tempGOutputPathCompareResult, job1),
                  os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult))
        #用EPCAM打开比过图的jobNameG_comRes
        Input.open_job(self.ussd.jobNameGCompareResult, tempGOutputPathCompareResult)  # 用悦谱CAM打开料号
        self.trigger.emit("已完成G比图！")
        self.ussd.textBrowserMain.append("我可以直接在Qthread中设置窗口")

        # 把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。
        logger.info("把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。")
        self.g.input_reset(job1)
        self.trigger.emit('比图结果料号已导出！')