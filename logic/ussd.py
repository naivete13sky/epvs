import os
import shutil
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer


from ui.ussd import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI

class Ussd(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Ussd,self).__init__()
        self.setupUi(self)
        # 设置表格大小
        self.tableWidgetGerber.setRowCount(0)
        self.tableWidgetGerber.setColumnCount(12)
        # 设置列标签
        column_labels = ["文件名", "类型", "省零", "整数", "小数", "单位", "工具单位","悦谱转图结果","第三方转图结果","悦谱比图结果","第三方比图结果","说明"]
        self.tableWidgetGerber.setHorizontalHeaderLabels(column_labels)

        self.pushButtonSelectGerber.clicked.connect(self.selectGerber)
        self.pushButtonLoadEPCAM.clicked.connect(self.loadEPCAM)
        self.pushButtonIdentify.clicked.connect(self.identify)
        self.pushButtonTranslateEP.clicked.connect(self.translateEP2)
        self.pushButtonTranslateG.clicked.connect(self.translateG)
        self.pushButtonCompareEp.clicked.connect(self.compareEp)
        self.pushButtonCompareG.clicked.connect(self.compareG)

        # time.sleep(0.1)
        # 加载EPCAM
        # self.thread = MyThreadStartEPCAM(self)  # 创建线程
        # self.thread.trigger.connect(self.update_text_start_EPCAM)  # 连接信号！
        # self.thread.start()  # 启动线程






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
            header.setSectionResizeMode(9, QHeaderView.Stretch)


    def loadEPCAM(self):
        '''
        # 手工加载EPCAM，需要点击”加载EPCAM按钮“
        :return:
        '''
        print("ready to load EPCAM")
        from config_ep.epcam import EPCAM
        self.epcam = EPCAM()
        self.epcam.init()
        self.pushButtonLoadEPCAM.setText("已加载EPCAM")
        self.pushButtonLoadEPCAM.setStyleSheet("background-color: green")
        print("Finish load EPCAM")


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


    def translateG(self):
        '''
        G转图
        :return:
        '''
        from config_g.g import G
        from epkernel import Input
        from epkernel.Action import Information
        from epkernel import GUI
        self.g = G(r"C:\cc\python\epwork\epvs\config_g\bin\gateway.exe")
        #先清空料号
        self.g.clean_g_all_pre_get_job_list(r'//vmware-host/Shared Folders/share/job_list.txt')
        self.g.clean_g_all_do_clean(r'C:\cc\share\job_list.txt')

        self.jobNameG = self.jobName + "_g"

        gerberList_path = []
        for row in range(self.tableWidgetGerber.rowCount()):
            each_dict = {}
            gerberFolderPathG = os.path.join(r"Z:\share",self.vs_time + '_' + self.jobName,r'gerber',self.jobName)
            print('gerberFolderPathG:',gerberFolderPathG)
            each_dict['path'] = os.path.join(gerberFolderPathG,self.tableWidgetGerber.item(row, 0).text())
            if self.tableWidgetGerber.item(row, 1).text() in ['Excellon2','excellon2','Excellon','excellon']:
                each_dict['file_type'] = 'excellon'
                each_dict_para = {}
                each_dict_para['zeroes'] = self.tableWidgetGerber.item(row,2).text()
                each_dict_para['nf1'] = int(self.tableWidgetGerber.item(row,3).text())
                each_dict_para['nf2'] = int(self.tableWidgetGerber.item(row,4).text())
                each_dict_para['units'] = self.tableWidgetGerber.item(row, 5).text()
                each_dict_para['tool_units'] = self.tableWidgetGerber.item(row, 6).text()
                each_dict['para'] = each_dict_para
            elif self.tableWidgetGerber.item(row, 1).text() in ['Gerber274x','gerber274x']:
                each_dict['file_type'] = 'gerber'
            else:
                each_dict['file_type'] = ''
            gerberList_path.append(each_dict)
        print("gerberList_path:",gerberList_path)

        # gerberList_path = [{"path": r"C:\temp\gerber\nca60led\Polaris_600_LED.DRD", "file_type": "excellon"},
        #                    {"path": r"C:\temp\gerber\nca60led\Polaris_600_LED.TOP", "file_type": "gerber274x"}]

        self.g.input_init(job=self.jobNameG, step=self.step, gerberList_path=gerberList_path)

        out_path_g = os.path.join(r'Z:\share', self.vs_time + '_' + self.jobName, r'g', r'output')
        self.g.g_export(self.jobNameG, out_path_g,mode_type='directory')

        out_path_local = self.tempGOutputPath
        Input.open_job(self.jobNameG, out_path_local)  # 用悦谱CAM打开料号
        # GUI.show_layer(self.jobNameG, self.step, "")

        #G转图情况，更新到表格中
        all_layers_list_job_g = Information.get_layers(self.jobNameG)
        print("all_layers_list_job_g:",all_layers_list_job_g)
        for row in range(self.tableWidgetGerber.rowCount()):
            pass
            if self.tableWidgetGerber.item(row,0).text().lower() in  all_layers_list_job_g:
                self.tableWidgetGerber.setCellWidget(row, 8, self.buttonForRowTranslateG(str(row)))

    def compareEp(self):
        '''
         #悦谱比图：在方法中调用QThread类来执行比图
        :return:
        '''

        self.thread = MyThreadStartCompareEP(self)  # 创建线程
        self.thread.trigger.connect(self.update_text_start_compare_ep)  # 连接信号！
        self.thread.start()  # 启动线程

    def update_text_start_compare_ep(self, message):
        '''
        悦谱比图在QThread中实现时，
        比图后要把每一层是否通过的信息更新到窗口上，需要通过在QThread中emit信号，在这里接收到信号后做出窗口调整处理。
        :param message:
        :return:
        '''
        self.textBrowserLog.append(message)
        # if message.split("|")[0] == "更新悦谱转图结果":
        #     current_row = int(message.split("|")[1])
        #     self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateEP(str(current_row)))


    def compareG(self):
        '''
         #悦谱比图：在方法中调用QThread类来执行比图
        :return:
        '''

        self.thread = MyThreadStartCompareG(self)  # 创建线程
        self.thread.trigger.connect(self.update_text_start_compare_g)  # 连接信号！
        self.thread.start()  # 启动线程

    def update_text_start_compare_g(self, message):
        '''
        G比图在QThread中实现时，
        比图后要把每一层是否通过的信息更新到窗口上，需要通过在QThread中emit信号，在这里接收到信号后做出窗口调整处理。
        :param message:
        :return:
        '''
        self.textBrowserLog.append(message)
        # if message.split("|")[0] == "更新悦谱转图结果":
        #     current_row = int(message.split("|")[1])
        #     self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateEP(str(current_row)))



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


    def viewLayerG(self,id):
        '''
        #用EPCAM查看G转图的结果
        :param id:
        :return:
        '''
        pass
        # print("layer id:",id)
        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()
        # print("layerName:",layerName)
        GUI.show_layer(self.jobNameG, self.step, layerName)


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


    def buttonForRowTranslateG(self, id):
        '''
        # 列表内添加按钮G
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

        viewBtn.clicked.connect(lambda: self.viewLayerG(id))

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


    def translateEP(self):
        '''
        #悦谱转图，在方法中直接写转图的逻辑操作
        :return:
        '''
        from epkernel.Edition import Job,Matrix
        print("ready to traslateEp")
        from epkernel import Input,BASE

        # 创建一个空料号
        Job.create_job(self.jobName)
        # 创建一个空step
        Matrix.create_step(self.jobName, self.step)
        # 开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        offsetFlag = False
        offset1 = 0
        offset2 = 0
        for row in range(self.tableWidgetGerber.rowCount()):
            each_file = self.tableWidgetGerber.item(row, 0).text()
            # print(each_file)
            result_each_file_identify = Input.file_identify(os.path.join(self.lineEditGerberFolderPath.text(), each_file))
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']
            # print("orig min_1,min_2:", min_1, ":", min_2)
            # 如果是孔的话，可能要调整参数的。
            try:
                if result_each_file_identify["format"] == "Excellon2":
                    print('need to set the para for drill excellon2'.center(190, '-'))
                    print('原来导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                    result_each_file_identify['parameters']['zeroes_omitted'] = self.tableWidgetGerber.item(row,2).text()
                    result_each_file_identify['parameters']['Number_format_integer'] = int(self.tableWidgetGerber.item(row,3).text())
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(self.tableWidgetGerber.item(row,4).text())
                    result_each_file_identify['parameters']['units'] = self.tableWidgetGerber.item(row, 5).text()
                    result_each_file_identify['parameters']['tool_units'] = self.tableWidgetGerber.item(row,6).text()
                    print('现在导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                if result_each_file_identify["format"] == "Gerber274x":
                    # print("我是Gerber274x")
                    # print('orig para'.center(190, '-'))
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
            translateResult = Input.file_translate(path=os.path.join(self.lineEditGerberFolderPath.text(), each_file), job=self.jobName, step=self.step, layer=each_file,
                                 param=result_each_file_identify['parameters'])
            # print("translateResult:",translateResult)
            if translateResult == True:
                # self.tableWidgetGerber.setItem(row, 7,QTableWidgetItem("已转"))
                self.tableWidgetGerber.setCellWidget(row, 7, self.buttonForRowTranslateEP(str(row)))

        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.jobName, self.tempEpOutputPath)


    def start_demo(self):
        thread =MyThreadDemo(self) # 创建线程
        thread.trigger.connect(self.update_text_demo) # 连接信号！
        thread.start() # 启动线程



    def update_text_demo(self, message):
        self.textBrowserLog.append(message)



class MyThreadDemo(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串
    def __init__(self, parent=None):
        super(MyThreadDemo, self).__init__(parent)

    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        # 把代码中的print全部改为trigger.emit
        # print u"线程启动了！"
        self.trigger.emit("开始处理了！")


class MyThreadStartTranslateEP(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, ussd):
        super(MyThreadStartTranslateEP, self).__init__()
        self.ussd = ussd

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

class MyThreadStartCompareEP(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, ussd):
        super(MyThreadStartCompareEP, self).__init__()
        self.ussd = ussd

    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始悦谱比图！")
        self.trigger.emit("正在悦谱比图！")
        from epkernel.Edition import Job, Matrix,Layers
        from epkernel import Input, BASE

        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            each_file = self.ussd.tableWidgetGerber.item(row, 0).text()
            # print(each_file)
            job1 = self.ussd.jobName
            job2 = self.ussd.jobNameG
            step1 = self.ussd.step
            step2 = self.ussd.step
            layer1 = each_file.upper()
            layer2 = each_file.upper()

            compareResult = Layers.layer_compare_point(job1, step1, layer1, job2, step2, layer2, tol=22860, isGlobal=True,
                                       consider_SR=True, map_layer_resolution=5080000)
            print("compareResult:",row,each_file,compareResult)

            self.trigger.emit("compareResult:"+str(compareResult))
            # if translateResult == True:
            #     # self.ussd.tableWidgetGerber.setItem(row, 7, QTableWidgetItem("abc"))
            #     self.trigger.emit("更新悦谱转图结果|"+str(row))


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.ussd.jobName, self.ussd.tempEpOutputPath)
        self.trigger.emit("已完成悦谱转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")

class MyThreadStartCompareG(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, ussd):
        super(MyThreadStartCompareG, self).__init__()
        self.ussd = ussd

    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始G比图！")
        self.trigger.emit("正在G比图！")
        from epkernel.Edition import Job, Matrix,Layers
        from epkernel import Input, BASE

        layerInfo = []
        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            each_dict = {}
            each_file = self.ussd.tableWidgetGerber.item(row, 0).text()
            # print(each_file)
            each_dict["layer"] = each_file
            if self.ussd.tableWidgetGerber.item(row, 1).text() in ['Excellon2','excellon2','Excellon','excellon']:
                each_dict['layer_type'] = 'drill'
            else:
                each_dict['layer_type'] = ''

            layerInfo.append(each_dict)
        print('layerInfo:',layerInfo)



        job1 = self.ussd.jobNameG
        job2 = self.ussd.jobName
        step1 = self.ussd.step
        step2 = self.ussd.step
        layer1 = each_file.lower()
        layer2 = each_file.lower()

        # from config_g.g import G
        # g = G(r"C:\cc\python\epwork\epvs\config_g\bin\gateway.exe")
        self.ussd.g.import_odb_folder(os.path.join(r'Z:\share', self.ussd.vs_time + '_' + self.ussd.jobName, r'ep', r'output',self.ussd.jobName))

        self.ussd.g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)
        res = self.ussd.g.layer_compare(
            vs_time_g=self.ussd.vs_time, temp_path=self.ussd.temp_path,temp_path_vm_parent=r'Z:\share',
            job1=job1, step1=step1,
            job2=job2, step2=step2,
            layerInfo=layerInfo)
        print('res:',res)



        # print("compareResult:",row,each_file,compareResult)
        #
        # self.trigger.emit("compareResult:"+str(compareResult))
        # if translateResult == True:
        #     # self.ussd.tableWidgetGerber.setItem(row, 7, QTableWidgetItem("abc"))
        #     self.trigger.emit("更新悦谱转图结果|"+str(row))


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.ussd.jobName, self.ussd.tempEpOutputPath)
        self.trigger.emit("已完成悦谱转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")






