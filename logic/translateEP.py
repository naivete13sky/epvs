import os
import sys

from PyQt5 import QtCore
from epkernel.Action import Information


import logging
# 创建一个日志记录器
logger = logging.getLogger('epvs_logger')
logger.setLevel(logging.DEBUG)
# 创建一个文件处理器
file_handler = logging.FileHandler('log/epvs.log',encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# 检查是否已经存在相同的处理器
if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == file_handler.baseFilename for handler in logger.handlers):
    # 添加文件处理器到日志记录器
    logger.addHandler(file_handler)


class MyThreadStartTranslateEP(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc,whichJob,whichTranslateMethod):
        super(MyThreadStartTranslateEP, self).__init__()
        self.ussd = cc
        self.whichJob = whichJob
        self.whichTranslateMethod = whichTranslateMethod



    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始悦谱转图！")
        self.trigger.emit("正在悦谱转图！")
        from epkernel.Edition import Job, Matrix
        from epkernel import Input, BASE
        # 创建一个空料号
        Job.create_job(self.ussd.jobName)
        # 创建一个空step
        Matrix.create_step(self.ussd.jobName, self.ussd.step)
        # 开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        offsetFlag = False
        offset1 = 0
        offset2 = 0
        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            each_file = self.ussd.tableWidgetGerber.item(row, 0).text()

            result_each_file_identify = Input.file_identify(
                os.path.join(self.ussd.lineEditGerberFolderPath.text(), each_file))
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']

            # 如果是孔的话，可能要调整参数的。
            try:
                if result_each_file_identify["format"] == "Excellon2":
                    logger.info('need to set the para for drill excellon2'.center(190, '-'))
                    logger.info('原来导入参数'.center(190, '-'))
                    logger.info(result_each_file_identify)

                    result_each_file_identify['parameters']['zeroes_omitted'] = self.ussd.tableWidgetGerber.item(row,
                                                                                                            2).text()
                    result_each_file_identify['parameters']['Number_format_integer'] = int(
                        self.ussd.tableWidgetGerber.item(row, 3).text())
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(
                        self.ussd.tableWidgetGerber.item(row, 4).text())
                    result_each_file_identify['parameters']['units'] = self.ussd.tableWidgetGerber.item(row, 5).text()
                    result_each_file_identify['parameters']['tool_units'] = self.ussd.tableWidgetGerber.item(row, 6).text()
                    logger.info('现在导入参数'.center(190, '-'))
                    logger.info(result_each_file_identify)

                if result_each_file_identify["format"] == "Gerber274x":

                    if (offsetFlag == False) and (
                            abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):

                        offset1 = min_1
                        offset2 = min_2
                        offsetFlag = True
                    result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1,
                                                                                 'second': offset2}


            except Exception as e:
                logger.exception("有异常情况发生")
            translateResult = Input.file_translate(path=os.path.join(self.ussd.lineEditGerberFolderPath.text(), each_file),
                                                   job=self.ussd.jobName, step=self.ussd.step, layer=each_file,
                                                   param=result_each_file_identify['parameters'])
            self.trigger.emit("translateResult:"+str(translateResult))
            if translateResult == True:
                # self.ussd.tableWidgetGerber.setItem(row, 7, QTableWidgetItem("abc"))
                self.trigger.emit("更新料号"+self.whichJob+'转图结果|'+self.ussd.translateMethod+'|'+str(row)+'|'+each_file.lower())


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.ussd.jobName, self.ussd.tempODBParentPath)
        self.trigger.emit("已完成悦谱转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")

        all_layers_list_job = Information.get_layers(self.ussd.jobName)
        all_step_list_job = Information.get_steps(self.ussd.jobName)
        if len(all_layers_list_job) > 0:
            self.trigger.emit("料号转图完成|"+self.whichJob+'|'+self.ussd.translateMethod)