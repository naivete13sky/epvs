import json
import os
import shutil
from PyQt5 import QtCore
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget
from epkernel import GUI
from ui.dialogInput import Ui_Dialog as DialogInput
from logic.translateG import MyThreadStartTranslateG
from logic.translateEP import MyThreadStartTranslateEP


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



class DialogInput(QDialog,DialogInput):
    triggerDialogInputStr = QtCore.pyqtSignal(str) # trigger传输的内容是字符串
    triggerDialogInputList = QtCore.pyqtSignal(list)  # trigger传输的内容是字符串
    translateMethod = None



    def __init__(self,whichJob):
        super(DialogInput,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.whichJob = whichJob
        # 设置表格大小
        self.tableWidgetGerber.setRowCount(0)
        self.tableWidgetGerber.setColumnCount(8)
        # 设置列标签
        column_labels = ["文件名", "类型", "省零", "整数", "小数", "单位", "工具单位", "转图结果"]
        self.tableWidgetGerber.setHorizontalHeaderLabels(column_labels)

        self.setGeometry(400,200, 1000, 800)

        #设置转图方案combo box的currentIndexChanged槽连接
        self.whichTranslateMethod = 'ep'#默认是悦谱转图
        self.comboBoxInputMethod.currentIndexChanged.connect(self.translateMethodSelectionChanged)

        # 界面按钮的槽连接
        self.pushButtonSelectGerber.clicked.connect(self.select_folder)
        self.pushButtonIdentify.clicked.connect(self.identify)
        self.pushButtonTranslate.clicked.connect(self.translate)
        # self.pushButtonOK.clicked.connect(self.close)
        self.pushButtonOK.clicked.connect(self.on_ok_button_clicked)


    def translateMethodSelectionChanged(self, index):
        if self.sender().currentText() == '方案1：悦谱':
            logger.info("方案1：悦谱")
            self.whichTranslateMethod = 'ep'

        if self.sender().currentText() == '方案2：G':
            logger.info("方案2：g")
            self.whichTranslateMethod = 'g'
        if self.sender().currentText() == '方案3：待实现':
            logger.info("方案3：else")
            self.whichTranslateMethod = 'else'

        if len(self.lineEditGerberFolderPath.text()) > 0:
            self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.jobName = self.lineEditJobName.text()
            self.step = self.lineEditStep.text()


    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)

        # 实时预览当前路径下的所有文件
        folder_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        folder_dialog.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)

        if folder_dialog.exec_() == QFileDialog.Accepted:
            self.folder_path = folder_dialog.selectedFiles()[0]

            # self.load_folder(folder_path)
            self.lineEditGerberFolderPath.setText(self.folder_path)


            self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.lineEditStep.setText("orig")


            file_list = os.listdir(self.folder_path)
            file_count = len(file_list)

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
        logger.info("ready to identify")
        from epkernel import Input

        self.jobName = self.lineEditJobName.text()
        self.step = self.lineEditStep.text()

        # 复制一份原稿到临时文件夹
        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.temp_path = self.settings_dict['general']['temp_path']
        self.temp_path_g = self.settings_dict['g']['temp_path_g']


        if not os.path.exists(self.temp_path):
            os.mkdir(self.temp_path)

        self.tempGerberParentPath = os.path.join(self.temp_path, r'gerber')
        if not os.path.exists(self.tempGerberParentPath):
            os.mkdir(self.tempGerberParentPath)



        self.tempODBParentPath = os.path.join(self.temp_path, r'odb')
        if not os.path.exists(self.tempODBParentPath):
            os.mkdir(self.tempODBParentPath)



        self.tempGOutputPathCompareResult = os.path.join(self.temp_path, r'output_compare_result')
        if not os.path.exists(self.tempGOutputPathCompareResult):
            os.mkdir(self.tempGOutputPathCompareResult)

        self.tempGerberPath = os.path.join(self.tempGerberParentPath, self.jobName)
        if os.path.exists(self.tempGerberPath):

            # 读取配置文件
            with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            # self.gateway_path = self.json['g']['gateway_path']  # (json格式数据)字符串 转化 为字典

            self.gSetupType = self.json['g']['gSetupType']
            if self.gSetupType == 'local':
                # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                shutil.rmtree(self.tempGerberPath)
            if self.gSetupType == 'vmware':
                #使用PsExec通过命令删除远程机器的文件
                from ccMethod.ccMethod import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path='ccMethod',computer='192.168.1.3', username='administrator', password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = os.path.join(self.temp_path_g,'gerber',self.jobName)
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)

                logger.info("remote delete finish")
                # time.sleep(20)

            shutil.copytree(self.folder_path, self.tempGerberPath)
        else:
            # shutil.copy(folder_path, tempGerberPath)
            shutil.copytree(self.folder_path, self.tempGerberPath)


        for row in range(self.tableWidgetGerber.rowCount()):

            result_each_file_identify = Input.file_identify(os.path.join(self.tempGerberPath,self.tableWidgetGerber.item(row, 0).text()))

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
                logger.info("料号转图完成message:"+str(message.split("|")[2]))
                self.triggerDialogInputStr.emit(message)

            if message.split("|")[1] =="B":
                logger.info("料号转图完成message:"+str(message.split("|")[2]))
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

        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()

        GUI.show_layer(self.jobName, self.step, layerName)

    def viewLayerEPLayerName(self, layerName):
        '''
        # 用EPCAM查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass
        layerName = layerName.lower()
        GUI.show_layer(self.jobName, self.step, layerName)





    def translateG(self):
        '''
         #G转图2：在方法中调用QThread类来执行转图
        :return:
        '''
        self.translateMethod = '方案2：G'
        #先清空历史
        for row in range(self.tableWidgetGerber.rowCount()):
            self.tableWidgetGerber.removeCellWidget(row,7)

        self.thread = MyThreadStartTranslateG(self,self.whichJob,self.whichTranslateMethod)  # 创建线程
        self.thread.trigger.connect(self.update_text_start_translate_g)  # 连接信号！
        self.thread.start()  # 启动线程

    def update_text_start_translate_g(self, message):
        '''
        g转图在QThread中实现时，
        转图后要把每一层是否成功转成功的信息更新到窗口上，需要通过在QThread中emit信号，在这里接收到信号后做出窗口调整处理。
        :param message:
        :return:
        '''
        self.textBrowserLog.append(message)
        if message.split("|")[0] =="更新料号A转图结果":
            current_row = int(message.split("|")[2])
            self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateG(str(current_row)))
            self.triggerDialogInputStr.emit(message)


        if message.split("|")[0] =="更新料号B转图结果":
            current_row = int(message.split("|")[2])
            self.tableWidgetGerber.setCellWidget(current_row, 7, self.buttonForRowTranslateG(str(current_row)))
            self.triggerDialogInputStr.emit(message)


        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="A":
                logger.info("料号转图完成message:"+str(message.split("|")[2]))
                self.triggerDialogInputStr.emit(message)

            if message.split("|")[1] =="B":
                logger.info("料号转图完成message:"+str(message.split("|")[2]))
                self.triggerDialogInputStr.emit(message)


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

        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()

        GUI.show_layer(self.jobName, self.step, layerName)

    def viewLayerGLayerName(self, layerName):
        '''
        # 用G查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass

        layerName = layerName.lower()
        GUI.show_layer(self.jobName, self.step, layerName)


    def on_ok_button_clicked(self):
        pass
        # currnet_layer_list = Information.get_layers(self.jobName)
        # if len(currnet_layer_list)>0:
        #     self.triggerDialogInputStr.emit(self.whichJob + "_" + "highLight")
        self.close()