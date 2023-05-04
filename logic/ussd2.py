import os
import shutil
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from ui.ussd2 import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI

class Ussd2(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Ussd2,self).__init__()
        self.setupUi(self)



        # 设置表格大小
        self.tableWidgetVS.setRowCount(0)
        self.tableWidgetVS.setColumnCount(6)
        # 设置列标签
        column_labels = ["文件名", "悦谱转图结果", "第三方转图结果",
                         "悦谱比图结果", "第三方比图结果", "说明"]
        self.tableWidgetVS.setHorizontalHeaderLabels(column_labels)

        self.pushButtonInputA.clicked.connect(self.inputType)

    def inputType(self):
        '''
        选择导入类型：Gerber或ODB
        :return:
        '''
        # print(123)
        # 打开文件夹选择对话框
        pass
        self.dialogInputType = DialogInputType()
        self.dialogInputType.setModal(True)  # 设置对话框为模态
        self.dialogInputType.show()






from ui.dialogInputType import Ui_Dialog as DialogInputType
class DialogInputType(QDialog,DialogInputType):
    pass
    def __init__(self):
        super(DialogInputType,self).__init__()
        self.setupUi(self)

        self.pushButtonGerber.clicked.connect(self.inputGerber)
        self.pushButtonOdb.clicked.connect(self.inputOdb)

    def inputGerber(self):
        pass
        print("gerber")
        self.close()
        self.dialogInput = DialogInput()
        self.dialogInput.setModal(True)  # 设置对话框为模态
        self.dialogInput.show()



    def inputOdb(self):
        pass
        print("odb")



from ui.dialogInput import Ui_Dialog as DialogInput
class DialogInput(QDialog,DialogInput):
    pass
    def __init__(self):
        super(DialogInput,self).__init__()
        self.setupUi(self)
        # 设置表格大小
        self.tableWidgetGerber.setRowCount(0)
        self.tableWidgetGerber.setColumnCount(8)
        # 设置列标签
        column_labels = ["文件名", "类型", "省零", "整数", "小数", "单位", "工具单位", "悦谱转图结果"]
        self.tableWidgetGerber.setHorizontalHeaderLabels(column_labels)

        self.pushButtonSelectGerber.clicked.connect(self.selectGerber)
        self.pushButtonIdentify.clicked.connect(self.identify)
        self.pushButtonTranslateEP.clicked.connect(self.translateEP2)

    def selectGerber(self):
        '''
        选择原始Gerber路径
        :return:
        '''
        # print(123)
        # 打开文件夹选择对话框
        self.folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        if self.folder_path:
            self.lineEditGerberFolderPath.setText(self.folder_path)
            self.lineEditJobName.setText(self.folder_path.split("/")[-1])
            self.lineEditStep.setText("orig")

            # print('返回指定目录下的所有文件和目录名：', os.listdir(folder_path))
            file_list = os.listdir(self.folder_path)
            file_count = len(file_list)
            # print(file_count)
            self.tableWidgetGerber.setRowCount(file_count)
            for each in range(file_count):
                self.tableWidgetGerber.setItem(each, 0, QTableWidgetItem(file_list[each]))
            # 设置固定宽度为多少像素
            self.tableWidgetGerber.setColumnWidth(0, 200)
            self.tableWidgetGerber.setColumnWidth(1, 80)
            self.tableWidgetGerber.setColumnWidth(2, 70)
            self.tableWidgetGerber.setColumnWidth(3, 50)
            self.tableWidgetGerber.setColumnWidth(4, 50)
            self.tableWidgetGerber.setColumnWidth(5, 50)
            self.tableWidgetGerber.setColumnWidth(6, 60)
            # 设置自适应宽度
            header = self.tableWidgetGerber.horizontalHeader()
            # header.setSectionResizeMode(11, QHeaderView.Stretch)


    def identify(self):
        '''
        # 用EPCAM判断文件类型
        :return:
        '''
        print("ready to identify")
        from epkernel import Input

        self.jobName = self.lineEditJobName.text()
        self.step = self.lineEditStep.text()

        # 复制一份原稿到临时文件夹
        self.vs_time = str(int(time.time()))  # 比对时间
        self.temp_path = os.path.join(r"C:\cc\share", self.vs_time + '_' + self.jobName)
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

            self.tempGerberParentPath = os.path.join(self.temp_path, r'gerber')
            os.mkdir(self.tempGerberParentPath)

            self.tempEpPath = os.path.join(self.temp_path, r'ep')
            os.mkdir(self.tempEpPath)

            self.tempEpOutputPath = os.path.join(self.tempEpPath, r'output')
            os.mkdir(self.tempEpOutputPath)

            self.tempGPath = os.path.join(self.temp_path, r'g')
            os.mkdir(self.tempGPath)

            self.tempGOutputPath = os.path.join(self.tempGPath, r'output')
            os.mkdir(self.tempGOutputPath)

            self.tempGOutputPathCompareResult = os.path.join(self.tempGPath, r'output_compare_result')
            os.mkdir(self.tempGOutputPathCompareResult)

            self.tempGerberPath = os.path.join(self.tempGerberParentPath, self.jobName)
            # shutil.copy(folder_path, tempGerberPath)
            shutil.copytree(self.folder_path, self.tempGerberPath)


        for row in range(self.tableWidgetGerber.rowCount()):
            # print(self.tableWidgetGerber.item(row, 0).text())
            result_each_file_identify = Input.file_identify(os.path.join(self.tempGerberPath,self.tableWidgetGerber.item(row, 0).text()))
            # print(result_each_file_identify)
            # print(result_each_file_identify["format"])
            self.tableWidgetGerber.setItem(row, 1, QTableWidgetItem(result_each_file_identify["format"]))
            self.tableWidgetGerber.setItem(row, 2, QTableWidgetItem(result_each_file_identify["parameters"]['zeroes_omitted']))
            self.tableWidgetGerber.setItem(row, 3, QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_integer'])))
            self.tableWidgetGerber.setItem(row, 4,QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_decimal'])))
            self.tableWidgetGerber.setItem(row, 5,QTableWidgetItem(result_each_file_identify["parameters"]['units']))
            self.tableWidgetGerber.setItem(row, 6,QTableWidgetItem(result_each_file_identify["parameters"]['tool_units']))



    def translateEP2(self):
        '''
         #悦谱转图2：在方法中调用QThread类来执行转图
        :return:
        '''
        pass
        #先清空历史
        for row in range(self.tableWidgetGerber.rowCount()):
            self.tableWidgetGerber.removeCellWidget(row,7)



        self.thread = MyThreadStartTranslateEP(self)  # 创建线程
        self.thread.trigger.connect(self.update_text_start_translate_ep)  # 连接信号！
        self.thread.start()  # 启动线程


    def update_text_start_translate_ep(self, message):
        '''
        悦谱转图在QThread中实现时，
        转图后要把每一层是否成功转成功的信息更新到窗口上，需要通过在QThread中emit信号，在这里接收到信号后做出窗口调整处理。
        :param message:
        :return:
        '''
        self.textBrowserLog.append(message)
        if message.split("|")[0] =="更新悦谱转图结果":
            current_row = int(message.split("|")[1])
            self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateEP(str(current_row)))

        if message =="转图成功！":
            print("转图成功2！")




    def buttonForRowTranslateEP(self, id):
        '''
        # 列表内添加按钮EP
        :param id:
        :return:
        '''
        widget = QWidget()
        # 修改
        updateBtn = QPushButton('修改')
        updateBtn.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')

        updateBtn.clicked.connect(lambda: self.updateTable(id))

        # 查看
        viewBtn = QPushButton('查看')
        viewBtn.setStyleSheet(''' text-align : center;
                                  background-color : DarkSeaGreen;
                                  height : 30px;
                                  border-style: outset;
                                  font : 13px; ''')

        viewBtn.clicked.connect(lambda: self.viewLayerEP(id))

        # 删除
        deleteBtn = QPushButton('删除')
        deleteBtn.setStyleSheet(''' text-align : center;
                                    background-color : LightCoral;
                                    height : 30px;
                                    border-style: outset;
                                    font : 13px; ''')

        hLayout = QHBoxLayout()
        # hLayout.addWidget(updateBtn)
        hLayout.addWidget(viewBtn)
        # hLayout.addWidget(deleteBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget


    def viewLayerEP(self,id):
        '''
        # 用EPCAM查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass
        # print("layer id:",id)
        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()
        # print("layerName:",layerName)
        GUI.show_layer(self.jobName, self.step, layerName)





class MyThreadStartTranslateEP(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, ussd2):
        super(MyThreadStartTranslateEP, self).__init__()
        self.ussd = ussd2

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
            # print(each_file)
            result_each_file_identify = Input.file_identify(
                os.path.join(self.ussd.lineEditGerberFolderPath.text(), each_file))
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']
            # print("orig min_1,min_2:", min_1, ":", min_2)
            # 如果是孔的话，可能要调整参数的。
            try:
                if result_each_file_identify["format"] == "Excellon2":
                    print('need to set the para for drill excellon2'.center(190, '-'))
                    print('原来导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                    result_each_file_identify['parameters']['zeroes_omitted'] = self.ussd.tableWidgetGerber.item(row,
                                                                                                            2).text()
                    result_each_file_identify['parameters']['Number_format_integer'] = int(
                        self.ussd.tableWidgetGerber.item(row, 3).text())
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(
                        self.ussd.tableWidgetGerber.item(row, 4).text())
                    result_each_file_identify['parameters']['units'] = self.ussd.tableWidgetGerber.item(row, 5).text()
                    result_each_file_identify['parameters']['tool_units'] = self.ussd.tableWidgetGerber.item(row, 6).text()
                    print('现在导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                if result_each_file_identify["format"] == "Gerber274x":
                    # print("我是Gerber274x")
                    # print(result_each_file_identify)
                    # print("offsetFlag:", offsetFlag)
                    if (offsetFlag == False) and (
                            abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
                        # print("hihihi2:",each_file)
                        offset1 = min_1
                        offset2 = min_2
                        offsetFlag = True
                    result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1,
                                                                                 'second': offset2}
                    # print('now para'.center(190, '-'))
                    # print(result_each_file_identify)

            except Exception as e:
                print(e)
                print("有异常情况发生")
            translateResult = Input.file_translate(path=os.path.join(self.ussd.lineEditGerberFolderPath.text(), each_file),
                                                   job=self.ussd.jobName, step=self.ussd.step, layer=each_file,
                                                   param=result_each_file_identify['parameters'])
            self.trigger.emit("translateResult:"+str(translateResult))
            if translateResult == True:
                # self.ussd.tableWidgetGerber.setItem(row, 7, QTableWidgetItem("abc"))
                self.trigger.emit("更新悦谱转图结果|"+str(row))


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.ussd.jobName, self.ussd.tempEpOutputPath)
        self.trigger.emit("已完成悦谱转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")
        from epkernel.Action import Information
        all_layers_list_job = Information.get_layers(self.ussd.jobName)
        all_step_list_job = Information.get_steps(self.ussd.jobName)
        if len(all_layers_list_job) > 0:
            print("转图成功！")
            self.trigger.emit("转图成功！")