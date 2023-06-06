import json
import os
import shutil
from PyQt5 import QtCore
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QGridLayout, \
    QLabel, QLineEdit, QCheckBox, QRadioButton, QDialogButtonBox, QComboBox
from epkernel import GUI

from logic import gl
from ui.dialogInput import Ui_Dialog as DialogInput
from logic.translateG import MyThreadStartTranslateG
from logic.translateEP import MyThreadStartTranslateEP


from logic.log import MyLog
logger = MyLog.log_init()



class DialogInput(QDialog,DialogInput):
    triggerDialogInputStr = QtCore.pyqtSignal(str) # trigger传输的内容是字符串
    triggerDialogInputList = QtCore.pyqtSignal(list)  # trigger传输的内容是字符串
    translateMethod = None



    def __init__(self,whichJob,**kwargs):
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

        # 如果已经有一个料号设置了gerber路径，那另一个料号默认自动也设置成这个路径
        if gl.GerberFolderPath:
            self.lineEditGerberFolderPath.setText(gl.GerberFolderPath)
            self.folder_path = self.lineEditGerberFolderPath.text()
            # print('lineEditGerberFolderPath:',self.lineEditGerberFolderPath.text())
            # self.file_list = os.listdir(self.folder_path)
            # self.update_file_info_to_mainwindow()
            self.lineEditJobName.setText(
                self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
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


        input_path = kwargs.get('input_path')
        if input_path:
            print('input_path:', input_path)
            self.lineEditGerberFolderPath.setText(input_path)
            self.folder_path = input_path
            # print('basename:',os.path.basename(self.folder_path))

            # self.load_folder(folder_path)
            self.lineEditGerberFolderPath.setText(self.folder_path)

            self.lineEditJobName.setText(
                os.path.basename(self.folder_path) + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.lineEditStep.setText("orig")

            self.file_list = os.listdir(self.folder_path)
            file_count = len(self.file_list)

            self.tableWidgetGerber.setRowCount(file_count)
            for each in range(file_count):
                self.tableWidgetGerber.setItem(each, 0, QTableWidgetItem(self.file_list[each]))
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
            self.triggerDialogInputList.emit(self.file_list)







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
            gl.GerberFolderPath = self.lineEditGerberFolderPath.text()


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

    def update_file_info_to_mainwindow(self):
        self.triggerDialogInputStr.emit("子窗口已获取文件列表！")
        self.triggerDialogInputList.emit(self.file_list)

    def identify(self):
        '''
        # 用EPCAM判断文件类型
        :return:
        '''
        logger.info("ready to identify")


        # region 是否已加载EPCAM
        if gl.FlagEPCAM == False:
            from config_ep.epcam import EPCAM
            self.epcam = EPCAM()
            self.epcam.init()
            print("完成加载EPCAM!")
            gl.FlagEPCAM = True
            # self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # # 绿色
            # self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')

        # endregion

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


        # 执行了translate，可以把当前的导入参数存储下来，为另一个料号导入时用，可以省一次identify。
        gl.DialogInput = self


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



class DialogUploadTestJob(QDialog):
    def __init__(self, job_name):
        super().__init__()
        self.setWindowTitle('上传测试料号')
        self.layout = QGridLayout()

        self.label_job_parent = QLabel(self)
        self.label_job_parent.setText('主料号ID:')
        self.lineEdit_job_parent = QLineEdit(self)

        self.label_job_name = QLabel(self)
        self.label_job_name.setText('测试料号名称:')
        self.lineEdit_job_name = QLineEdit(self)
        self.lineEdit_job_name.setText(job_name)
        self.lineEdit_job_name.selectAll()

        self.label_file_type = QLabel(self)
        self.label_file_type.setText('料号文件类型:')
        self.comboBox_file_type = QComboBox()
        self.comboBox_file_type.addItems(['gerber274X','gerber274D','dxf','dwg','odb','pcb','else'])
        self.comboBox_file_type.setCurrentText('gerber274X')

        self.label_test_usage_for_epcam_module = QLabel(self)
        self.label_test_usage_for_epcam_module.setText('模块ID:')
        self.lineEdit_test_usage_for_epcam_module = QLineEdit(self)


        self.label_vs_result_ep = QLabel(self)
        self.label_vs_result_ep.setText('悦谱比图结果:')
        self.comboBox_vs_result_ep = QComboBox()
        self.comboBox_vs_result_ep.addItems(['passed', 'failed', 'none'])
        self.comboBox_vs_result_ep.setCurrentText('none')

        self.label_vs_result_g = QLabel(self)
        self.label_vs_result_g.setText('G比图结果:')
        self.comboBox_vs_result_g = QComboBox()
        self.comboBox_vs_result_g.addItems(['passed', 'failed', 'none'])
        self.comboBox_vs_result_g.setCurrentText('none')

        self.label_bug_info = QLabel(self)
        self.label_bug_info.setText('Bug信息:')
        self.lineEdit_bug_info = QLineEdit(self)



        self.label_bool_layer_info = QLabel(self)
        self.label_bool_layer_info.setText('是否有层别信息:')
        self.radioButton_bool_layer_info_false = QRadioButton('false')
        self.radioButton_bool_layer_info_false.setChecked(True)
        self.radioButton_bool_layer_info_true = QRadioButton('true')
        self.sub_layout_bool_layer_info = QHBoxLayout()
        self.sub_layout_bool_layer_info.addWidget(self.radioButton_bool_layer_info_false)
        self.sub_layout_bool_layer_info.addWidget(self.radioButton_bool_layer_info_true)



        self.label_vs_time_ep = QLabel(self)
        self.label_vs_time_ep.setText('悦谱比对时间戳:')
        self.lineEdit_vs_time_ep = QLineEdit(self)

        self.label_vs_time_g = QLabel(self)
        self.label_vs_time_g.setText('G比对时间戳:')
        self.lineEdit_vs_time_g = QLineEdit(self)


        self.label_status = QLabel(self)
        self.label_status.setText('状态:')
        self.radioButton_status_draft = QRadioButton('草稿')
        self.radioButton_status_draft.setChecked(True)
        self.radioButton_status_published = QRadioButton('正式')
        self.sub_layout_status = QHBoxLayout()
        self.sub_layout_status.addWidget(self.radioButton_status_draft)
        self.sub_layout_status.addWidget(self.radioButton_status_published)

        self.label_author = QLabel(self)
        self.label_author.setText('负责人ID:')
        self.lineEdit_author = QLineEdit(self)

        self.label_tags = QLabel(self)
        self.label_tags.setText('标签:')
        self.lineEdit_tags = QLineEdit(self)

        self.label_remark = QLabel(self)
        self.label_remark.setText('备注:')
        self.lineEdit_remark = QLineEdit(self)


        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.label_job_parent, 0, 0)
        self.layout.addWidget(self.lineEdit_job_parent, 0, 1)
        self.layout.addWidget(self.label_job_name, 1, 0)
        self.layout.addWidget(self.lineEdit_job_name,1,1)
        self.layout.addWidget(self.label_file_type, 2, 0)
        self.layout.addWidget(self.comboBox_file_type, 2, 1)
        self.layout.addWidget(self.label_test_usage_for_epcam_module,3,0)
        self.layout.addWidget(self.lineEdit_test_usage_for_epcam_module,3,1)
        self.layout.addWidget(self.label_vs_result_ep,4,0)
        self.layout.addWidget(self.comboBox_vs_result_ep,4,1)
        self.layout.addWidget(self.label_vs_result_g, 5, 0)
        self.layout.addWidget(self.comboBox_vs_result_g, 5, 1)
        self.layout.addWidget(self.label_bug_info,6,0)
        self.layout.addWidget(self.lineEdit_bug_info, 6, 1)
        self.layout.addWidget(self.label_bool_layer_info,7,0)
        self.layout.addLayout(self.sub_layout_bool_layer_info,7,1)
        self.layout.addWidget(self.label_vs_time_ep,8,0)
        self.layout.addWidget(self.lineEdit_vs_time_ep,8,1)
        self.layout.addWidget(self.label_vs_time_g, 9, 0)
        self.layout.addWidget(self.lineEdit_vs_time_g, 9, 1)
        self.layout.addWidget(self.label_status,10,0)
        self.layout.addLayout(self.sub_layout_status,10,1)
        self.layout.addWidget(self.label_author,11,0)
        self.layout.addWidget(self.lineEdit_author,11,1)
        self.layout.addWidget(self.label_tags, 12, 0)
        self.layout.addWidget(self.lineEdit_tags, 12, 1)
        self.layout.addWidget(self.label_remark, 13, 0)
        self.layout.addWidget(self.lineEdit_remark, 13, 1)

        self.layout.addWidget(self.button_box,14,1)
        self.setLayout(self.layout)