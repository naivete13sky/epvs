import os
import shutil
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QDir
from PyQt5.QtGui import QFont, QPalette, QColor

from ui.mainWindow import Ui_MainWindow
from ui.dialogInput import Ui_Dialog as DialogInput
from PyQt5.QtWidgets import *
from epkernel import GUI

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)

        # 设置label
        # 创建一个QPalette对象
        palette = QPalette()
        # 设置背景颜色为白色
        # palette.setColor(QPalette.Window, QColor(255, 255, 255))
        # 设置字体颜色
        palette.setColor(QPalette.WindowText, QColor(255, 0, 0))
        # 将QPalette应用于QLabel
        self.labelStatusJobA.setPalette(palette)
        self.labelStatusJobB.setPalette(palette)


        # 设置表格大小
        self.tableWidgetVS.setRowCount(0)
        self.tableWidgetVS.setColumnCount(5)
        # 设置列标签
        column_labels = ["文件名", "料号A转图结果", "比图结果", "料号B转图结果", "说明"]
        self.tableWidgetVS.setHorizontalHeaderLabels(column_labels)
        # 设置固定宽度为多少像素
        self.tableWidgetVS.setColumnWidth(0, 200)
        self.tableWidgetVS.setColumnWidth(1, 100)
        self.tableWidgetVS.setColumnWidth(2, 300)
        self.tableWidgetVS.setColumnWidth(3, 100)
        self.tableWidgetVS.setColumnWidth(4, 200)
        # 设置自适应宽度
        header = self.tableWidgetVS.horizontalHeader()

        # 连接信号槽
        self.pushButtonInputA.clicked.connect(self.inputA)
        self.pushButtonInputB.clicked.connect(self.inputB)

    def inputA(self):
        pass

        if not hasattr(self, 'dialogInputA') or self.dialogInputA is None:
            self.dialogInputA = DialogInput("A")
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogInputA.setWindowTitle('料号A')
            self.dialogInputA.triggerDialogInputStr.connect(self.update_text_start_input_A_get_str)  # 连接信号！
            self.dialogInputA.triggerDialogInputList.connect(self.update_text_start_input_A_get_list)
        self.dialogInputA.show()


    def update_text_start_input_A_get_str(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(message)


        if message.split("|")[0] == "更新料号A转图结果":
            current_row = int(message.split("|")[2])
            self.tableWidgetVS.setCellWidget(current_row, 1, self.dialogInputA.buttonForRowTranslateEP(str(current_row)))

        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="A":
                print("料号转图完成message:",message.split("|")[2])
                self.labelStatusJobA.setText('状态：'+'转图完成' + '|' + message.split("|")[2])



    def update_text_start_input_A_get_list(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(str(message))

        #总表中存量文件数量
        self.currentMainTableFilesCount = self.tableWidgetVS.rowCount()
        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)
            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            print("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    pass
                    print("有新文件")




    def inputB(self):
        if not hasattr(self, 'dialogInputB') or self.dialogInputB is None:
            self.dialogInputB = DialogInput("B")
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogInputB.setWindowTitle('料号B')
            self.dialogInputB.triggerDialogInputStr.connect(self.update_text_start_input_B_get_str)  # 连接信号！
            self.dialogInputB.triggerDialogInputList.connect(self.update_text_start_input_B_get_list)
        self.dialogInputB.show()


    def update_text_start_input_B_get_str(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(message)


        if message.split("|")[0] == "更新料号B转图结果":
            current_row = int(message.split("|")[2])
            layerName = self.tableWidgetVS.item(current_row, 0).text()
            self.tableWidgetVS.setCellWidget(current_row, 3, self.dialogInputB.buttonForRowTranslateEPLayerName(layerName))

        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="B":
                print("料号转图完成message:",message.split("|")[2])
                self.labelStatusJobB.setText('状态：'+'转图完成' + '|' + message.split("|")[2])


    def update_text_start_input_B_get_list(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(str(message))
        # 总表中存量文件数量
        self.currentMainTableFilesCount = self.tableWidgetVS.rowCount()
        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text() for each in
                                          range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            # 本次要处理的文件数量
            self.file_count = len(message)
            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            print("说明已有一些文件信息在总表中了")
            # 如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            i = 0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.file_count+i)
                    # print("有新文件",message[each],self.currentMainTableFilesCount -1 + i)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))



class DialogInput(QDialog,DialogInput):
    triggerDialogInputStr = QtCore.pyqtSignal(str) # trigger传输的内容是字符串
    triggerDialogInputList = QtCore.pyqtSignal(list)  # trigger传输的内容是字符串
    translateMethod = None


    def __init__(self,whichJob):
        super(DialogInput,self).__init__()
        self.setupUi(self)
        self.whichJob = whichJob
        # 设置表格大小
        self.tableWidgetGerber.setRowCount(0)
        self.tableWidgetGerber.setColumnCount(8)
        # 设置列标签
        column_labels = ["文件名", "类型", "省零", "整数", "小数", "单位", "工具单位", "转图结果"]
        self.tableWidgetGerber.setHorizontalHeaderLabels(column_labels)

        #设置转图方案combo box的currentIndexChanged槽连接
        self.whichTranslateMethod = 'ep'#默认是悦谱转图
        self.comboBoxInputMethod.currentIndexChanged.connect(self.translateMethodSelectionChanged)

        # 界面按钮的槽连接
        self.pushButtonSelectGerber.clicked.connect(self.select_folder)
        self.pushButtonIdentify.clicked.connect(self.identify)
        self.pushButtonTranslate.clicked.connect(self.translate)
        self.pushButtonOK.clicked.connect(self.close)


    def translateMethodSelectionChanged(self, index):
        if self.sender().currentText() == '方案1：悦谱':
            print("方案1：悦谱")
            self.whichTranslateMethod = 'ep'

        if self.sender().currentText() == '方案2：G':
            print("方案2：g")
            self.whichTranslateMethod = 'g'
        if self.sender().currentText() == '方案3：待实现':
            print("方案3：else")
            self.whichTranslateMethod = 'else'

        if len(self.lineEditGerberFolderPath.text()) > 0:
            self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)


    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)

        # 实时预览当前路径下的所有文件
        folder_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        folder_dialog.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)

        if folder_dialog.exec_() == QFileDialog.Accepted:
            self.folder_path = folder_dialog.selectedFiles()[0]
            print('folder_path:',self.folder_path)
            # self.load_folder(folder_path)
            self.lineEditGerberFolderPath.setText(self.folder_path)


            self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
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

            self.triggerDialogInputStr.emit("子窗口已获取文件列表！")
            self.triggerDialogInputList.emit(file_list)


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
        # self.temp_path = os.path.join(r"C:\cc\share", self.vs_time + '_' + self.jobName)
        self.temp_path = os.path.join(r"C:\cc\share\epvs")
        # if os.path.exists(self.temp_path):
        #     os.remove(self.temp_path)
        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

        self.tempGerberParentPath = os.path.join(self.temp_path, r'gerber')
        if not os.path.exists(self.tempGerberParentPath):
            os.mkdir(self.tempGerberParentPath)

        # self.tempEpPath = os.path.join(self.temp_path, r'ep')
        # if not os.path.exists(self.tempEpPath):
        #     os.mkdir(self.tempEpPath)

        self.tempODBParentPath = os.path.join(self.temp_path, r'odb')
        if not os.path.exists(self.tempODBParentPath):
            os.mkdir(self.tempODBParentPath)

        # self.tempGPath = os.path.join(self.temp_path, r'g')
        # if not os.path.exists(self.tempGPath):
        #     os.mkdir(self.tempGPath)

        # self.tempGOutputPath = os.path.join(self.tempGPath, r'odb')
        # if not os.path.exists(self.tempGOutputPath):
        #     os.mkdir(self.tempGOutputPath)

        self.tempGOutputPathCompareResult = os.path.join(self.temp_path, r'output_compare_result')
        if not os.path.exists(self.tempGOutputPathCompareResult):
            os.mkdir(self.tempGOutputPathCompareResult)

        self.tempGerberPath = os.path.join(self.tempGerberParentPath, self.jobName)
        if os.path.exists(self.tempGerberPath):
            # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
            shutil.rmtree(self.tempGerberPath)
            shutil.copytree(self.folder_path, self.tempGerberPath)
        else:
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


    def translate(self):
        pass
        if self.comboBoxInputMethod.currentText()=='方案1：悦谱':
            self.translateEP()

        if self.comboBoxInputMethod.currentText()=='方案2：G':
            self.translateG()



    def translateEP(self):
        '''
         #悦谱转图2：在方法中调用QThread类来执行转图
        :return:
        '''
        self.translateMethod = '方案1：悦谱'
        #先清空历史
        for row in range(self.tableWidgetGerber.rowCount()):
            self.tableWidgetGerber.removeCellWidget(row,7)

        self.thread = MyThreadStartTranslateEP(self,self.whichJob,self.whichTranslateMethod)  # 创建线程
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
        if message.split("|")[0] =="更新料号A转图结果":
            current_row = int(message.split("|")[2])
            self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateEP(str(current_row)))
            self.triggerDialogInputStr.emit(message)


        if message.split("|")[0] =="更新料号B转图结果":
            current_row = int(message.split("|")[2])
            self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateEP(str(current_row)))
            self.triggerDialogInputStr.emit(message)


        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="A":
                print("料号转图完成message:",message.split("|")[2])
                self.triggerDialogInputStr.emit(message)

            if message.split("|")[1] =="B":
                print("料号转图完成message:",message.split("|")[2])
                self.triggerDialogInputStr.emit(message)


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

    #根据ID有时会有错乱，因为总表中的层顺序和各个料的Input层顺序可能是不一样的。所以总表总查看层图像时需要根据层名称来。
    def buttonForRowTranslateEPLayerName(self, layerName):
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

        viewBtn.clicked.connect(lambda: self.viewLayerEPLayerName(layerName))

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
        print("layerName:",layerName)
        GUI.show_layer(self.jobName, self.step, layerName)

    def viewLayerEPLayerName(self, layerName):
        '''
        # 用EPCAM查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass
        # print("layer id:",id)
        layerName = layerName.lower()
        print("layerName:", layerName)
        GUI.show_layer(self.jobName, self.step, layerName)


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



        gerberList_path = []
        for row in range(self.tableWidgetGerber.rowCount()):
            each_dict = {}
            gerberFolderPathG = os.path.join(r"Z:\share",r'epvs\gerber',self.jobName)
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

        self.g.input_init(job=self.jobName, step=self.step, gerberList_path=gerberList_path)

        out_path_g = os.path.join(r'Z:\share', r'epvs\odb')
        self.g.g_export(self.jobName, out_path_g,mode_type='directory')

        out_path_local = self.tempODBParentPath
        Input.open_job(self.jobName, out_path_local)  # 用悦谱CAM打开料号
        # GUI.show_layer(self.jobNameG, self.step, "")

        #G转图情况，更新到表格中
        all_layers_list_job_g = Information.get_layers(self.jobName)
        print("all_layers_list_job_g:",all_layers_list_job_g)
        for row in range(self.tableWidgetGerber.rowCount()):
            pass
            if self.tableWidgetGerber.item(row,0).text().lower() in  all_layers_list_job_g:
                self.tableWidgetGerber.setCellWidget(row, 7, self.buttonForRowTranslateG(str(row)))


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
        GUI.show_layer(self.jobName, self.step, layerName)



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
                self.trigger.emit("更新料号"+self.whichJob+'转图结果|'+self.ussd.translateMethod+'|'+str(row))


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(self.ussd.jobName, self.ussd.tempODBParentPath)
        self.trigger.emit("已完成悦谱转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")
        from epkernel.Action import Information
        all_layers_list_job = Information.get_layers(self.ussd.jobName)
        all_step_list_job = Information.get_steps(self.ussd.jobName)
        if len(all_layers_list_job) > 0:
            self.trigger.emit("料号转图完成|"+self.whichJob+'|'+self.ussd.translateMethod)
