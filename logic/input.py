import json
import os
import shutil
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QDir, QEventLoop, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QGridLayout, \
    QLabel, QLineEdit, QCheckBox, QRadioButton, QDialogButtonBox, QComboBox, QMessageBox, QProgressDialog, QButtonGroup, \
    QVBoxLayout
from epkernel import GUI
from epkernel.Edition import Job

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

    flag_identified = False



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



        input_path = kwargs.get('input_path')
        if input_path:
            # print('input_path:', input_path)
            self.lineEditGerberFolderPath.setText(input_path)
            self.folder_path = input_path
            self.lineEditGerberFolderPath.setText(self.folder_path)

            # print('cc:',self.folder_path,os.path.basename(self.folder_path))

            self.lineEditJobName.setText(
                os.path.basename(self.folder_path) + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.lineEditStep.setText("orig")

            self.file_list = os.listdir(self.folder_path)
            # print('self.file_list:',self.file_list)
            # 因为G软件不识别一些字符，需要转换一下文件名称。
            # 读取配置文件
            with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            illegal_character = self.json['general']['illegal_character']
            self.file_list_new = []
            for each in self.file_list:
                for char in illegal_character:
                    each = each.replace(char, '_')
                self.file_list_new.append(each)


            self.file_list = self.file_list_new
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

            # gerber路径保存到全局变量
            gl.GerberFolderPath = self.lineEditGerberFolderPath.text()
            gl.DialogInput = self

        # 如果已经有一个料号设置了gerber路径，那另一个料号默认自动也设置成这个路径
        if gl.GerberFolderPath:
            self.lineEditGerberFolderPath.setText(gl.GerberFolderPath)
            self.folder_path = self.lineEditGerberFolderPath.text()

            self.lineEditJobName.setText(
                os.path.basename(self.folder_path) + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.lineEditStep.setText("orig")

            file_list = os.listdir(self.folder_path)
            file_count = len(file_list)

            self.tableWidgetGerber.setRowCount(file_count)



            for each in range(file_count):
                if gl.DialogInput.tableWidgetGerber.item(each, 0):
                    self.tableWidgetGerber.setItem(each, 0,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 0).text()))


                if gl.DialogInput.tableWidgetGerber.item(each, 1):
                    self.tableWidgetGerber.setItem(each, 1, QTableWidgetItem(
                        gl.DialogInput.tableWidgetGerber.item(each, 1).text()))

                if gl.DialogInput.tableWidgetGerber.item(each, 2):
                    self.tableWidgetGerber.setItem(each, 2,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 2).text()))
                if gl.DialogInput.tableWidgetGerber.item(each, 3):
                    self.tableWidgetGerber.setItem(each, 3,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 3).text()))
                if gl.DialogInput.tableWidgetGerber.item(each, 4):
                    self.tableWidgetGerber.setItem(each, 4,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 4).text()))
                if gl.DialogInput.tableWidgetGerber.item(each, 5):
                    self.tableWidgetGerber.setItem(each, 5,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 5).text()))
                if gl.DialogInput.tableWidgetGerber.item(each, 6):
                    self.tableWidgetGerber.setItem(each, 6,
                                                   QTableWidgetItem(
                                                       gl.DialogInput.tableWidgetGerber.item(each, 6).text()))

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

            # 设置一下路径，没有的要创建一下，gerber文件复制一下
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
            self.jobName = self.lineEditJobName.text()
            self.step = self.lineEditStep.text()
            self.tempGerberPath = os.path.join(self.tempGerberParentPath, self.jobName)
            if os.path.exists(self.tempGerberPath):

                # 读取配置文件
                with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                    self.json = json.load(cfg)
                # self.gateway_path = self.json['g']['gateway_path']  # (json格式数据)字符串 转化 为字典

                self.gSetupType = self.json['g']['gSetupType']
                if self.gSetupType == 'local':
                    # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                    shutil.rmtree(self.tempGerberPath)
                if self.gSetupType == 'vmware':
                    # 使用PsExec通过命令删除远程机器的文件
                    from ccMethod.ccMethod import RemoteCMD
                    myRemoteCMD = RemoteCMD(psexec_path='ccMethod', computer='192.168.1.3',
                                            username='administrator',
                                            password='cc')
                    command_operator = 'rd /s /q'
                    command_folder_path = os.path.join(self.temp_path_g, 'gerber', self.jobName)
                    command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                    myRemoteCMD.run_cmd(command)

                    logger.info("remote delete finish")
                    # time.sleep(20)

            shutil.copytree(self.folder_path, self.tempGerberPath)
            #更改临时gerber文件夹中的文件名称
            # 读取配置文件
            with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            illegal_character = self.json['general']['illegal_character']

            for each in os.listdir(self.tempGerberPath):
                old_filename = each
                new_filename = each
                for char in illegal_character:
                    new_filename = new_filename.replace(char, '_')
                os.rename(os.path.join(self.tempGerberPath,old_filename), os.path.join(self.tempGerberPath,new_filename))
                # print(f'旧文件名：{old_filename}')
                # print(f'新文件名：{new_filename}')

            file_list = os.listdir(self.tempGerberPath)
            self.triggerDialogInputStr.emit("子窗口已获取文件列表！")
            self.triggerDialogInputList.emit(file_list)

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
            self.lineEditJobName.setText(os.path.basename(self.folder_path) + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
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


            self.lineEditJobName.setText(os.path.basename(self.folder_path) + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            self.lineEditStep.setText("orig")


            self.file_list = os.listdir(self.folder_path)

            # 因为G软件不识别一些字符，需要转换一下文件名称。
            # 读取配置文件
            with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            illegal_character = self.json['general']['illegal_character']
            self.file_list_new = []
            for each in self.file_list:
                for char in illegal_character:
                    each = each.replace(char, '_')
                self.file_list_new.append(each)


            self.file_list = self.file_list_new




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
            gl.DialogInput = self

    def update_file_info_to_mainwindow(self):
        self.triggerDialogInputStr.emit("子窗口已获取文件列表！")

        if hasattr(self,'file_list'):
            self.triggerDialogInputList.emit(self.file_list)

    def identify(self):
        '''
        # 用EPCAM判断文件类型
        :return:
        '''
        logger.info("ready to identify")


        if not os.path.isdir(self.lineEditGerberFolderPath.text()):
            pass
            QMessageBox.information(self,"请先选择料号路径","请先选择料号路径！然后再试！")
            return


        # region 是否已加载EPCAM
        if gl.FlagEPCAM == False:
            # 加载EPCAM进度条


            # from config_ep.epcam import EPCAM
            # self.epcam = EPCAM()
            # self.epcam.init()
            # print("完成加载EPCAM!")
            # gl.FlagEPCAM = True

            # 创建进度条对话框
            progress_dialog = QProgressDialog(self)
            progress_dialog.setWindowTitle('正在加载EPCAM')
            progress_dialog.setLabelText('正在加载EPCAM...')
            progress_dialog.setCancelButtonText('取消')
            progress_dialog.setWindowModality(Qt.ApplicationModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.setFixedSize(300, 100)  # 设置对话框的宽度为 400，高度为 200

            from logic.ProgressBarWindow import ProgressDialogThreadLoadEPCAM
            progress_thread = ProgressDialogThreadLoadEPCAM(self)
            progress_thread.progressChanged.connect(progress_dialog.setValue)
            progress_thread.finished.connect(progress_dialog.close)
            progress_thread.start()

            progress_dialog.exec_()

            # 执行后续操作
            print("Continuing with next steps")

            self.triggerDialogInputStr.emit('已加载EPCAM')




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
        # 更改临时gerber文件夹中的文件名称
        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.json = json.load(cfg)
        illegal_character = self.json['general']['illegal_character']

        for each in os.listdir(self.tempGerberPath):
            old_filename = each
            new_filename = each
            for char in illegal_character:
                new_filename = new_filename.replace(char, '_')
            os.rename(os.path.join(self.tempGerberPath, old_filename), os.path.join(self.tempGerberPath, new_filename))
            # print(f'旧文件名：{old_filename}')
            # print(f'新文件名：{new_filename}')

        file_list = os.listdir(self.tempGerberPath)


        for row in range(self.tableWidgetGerber.rowCount()):
            from ccMethod.ccMethod import TextMethod
            if TextMethod.is_chinese(os.path.join(self.tempGerberPath,self.tableWidgetGerber.item(row, 0).text())):
                QMessageBox.information(self,'路径异常','路径中有中文，请先去除！')
                return False

            result_each_file_identify = Input.file_identify(os.path.join(self.tempGerberPath,self.tableWidgetGerber.item(row, 0).text()))
            self.tableWidgetGerber.setItem(row, 1, QTableWidgetItem(result_each_file_identify["format"]))
            self.tableWidgetGerber.setItem(row, 2, QTableWidgetItem(result_each_file_identify["parameters"]['zeroes_omitted']))
            self.tableWidgetGerber.setItem(row, 3, QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_integer'])))
            self.tableWidgetGerber.setItem(row, 4,QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_decimal'])))
            self.tableWidgetGerber.setItem(row, 5,QTableWidgetItem(result_each_file_identify["parameters"]['units']))
            self.tableWidgetGerber.setItem(row, 6,QTableWidgetItem(result_each_file_identify["parameters"]['tool_units']))

        # self.flag_identified = True


    def translate(self):
        # if not self.flag_identified:
        #     QMessageBox.information(self, "请先Identify", "请先Identify！")
        #     return

        if not self.tableWidgetGerber.item(0,1):
            QMessageBox.information(self, "请先Identify", "请先Identify！")
            return


        pass
        if self.comboBoxInputMethod.currentText()=='方案1：悦谱':
            if gl.FlagTranslatingEP == True:
                pass
                QMessageBox.information(self,"提示：正在悦谱转图中","提示：正在悦谱转图中!请稍后再试！")
            else:
                self.translateEP()

        if self.comboBoxInputMethod.currentText()=='方案2：G':
            if gl.FlagTranslatingG == True:
                pass
                QMessageBox.information(self,"提示：正在G转图中","提示：正在G转图中!请稍后再试！")
            else:
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


    def close_job(self):
        pass
        Job.close_job(self.jobName)


class DialogUploadTestJob(QDialog):
    def __init__(self, job_name):
        super().__init__()
        self.setWindowTitle('上传测试料号')
        self.layout = QGridLayout()

        self.label_job_parent = QLabel(self)
        self.label_job_parent.setText('主料号ID:')
        self.lineEdit_job_parent = QLineEdit(self)
        #根据job_name精确查找主料号名称，如果有多个，则返回多个，之间用-隔开。
        from ccMethod.ccMethod import GetInfoFromDMS
        sql = "select * from job_job a where a.job_name ILIKE '{}'".format(job_name[:-5])
        pd_info = GetInfoFromDMS.exe_sql_return_pd(sql)
        print('pd_info:',pd_info)
        # self.test_job_id = str(pd_info.iloc[0]['id'])
        # 遍历 "id" 列并将其值存储在列表中
        column_id_values = []
        for index, value in pd_info['id'].items():
            column_id_values.append(str(value))
        # id_str = '-'.join(map(str, column_id_values))
        # self.lineEdit_job_parent.setText(id_str)
        if len(column_id_values)==0:
            QMessageBox.information(self,'请注意！','未找到同名称的主料号！请人工处理！')
        elif len(column_id_values)==1:
            self.lineEdit_job_parent.setText(column_id_values[0])
        elif len(column_id_values)>1:
            dialog = CustomMessageBox(column_id_values)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                if dialog.selected_option:
                    # QMessageBox.information(None, '选择结果', f'你选择了：{dialog.selected_option}')
                    self.lineEdit_job_parent.setText(dialog.selected_option)
                else:
                    QMessageBox.warning(None, '选择结果', '未选择任何选项')









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
        self.lineEdit_test_usage_for_epcam_module.setText('8')


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
        self.qButtonGroup_bool_layer_info = QButtonGroup()
        self.qButtonGroup_bool_layer_info.addButton(self.radioButton_bool_layer_info_false)
        self.qButtonGroup_bool_layer_info.addButton(self.radioButton_bool_layer_info_true)
        self.qButtonGroup_bool_layer_info.setExclusive(True)
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
        self.qButtonGroup_status = QButtonGroup()
        self.qButtonGroup_status.addButton(self.radioButton_status_draft)
        self.qButtonGroup_status.addButton(self.radioButton_status_published)
        self.qButtonGroup_status.setExclusive(True)
        self.sub_layout_status = QHBoxLayout()
        self.sub_layout_status.addWidget(self.radioButton_status_draft)
        self.sub_layout_status.addWidget(self.radioButton_status_published)

        self.label_author = QLabel(self)
        self.label_author.setText('负责人ID:')
        self.lineEdit_author = QLineEdit(self)
        from ccMethod.ccMethod import GetInfoFromDMS
        sql = "SELECT a.* from auth_user a where a.username = '{}'".format(gl.login_username)
        # print('sql:',sql)
        pd_info = GetInfoFromDMS.exe_sql_return_pd(sql)
        # print(pd_info)
        self.user_id = str(pd_info.iloc[0]['id'])
        self.lineEdit_author.setText(self.user_id)



        self.label_tags = QLabel(self)
        self.label_tags.setText('标签:')
        self.lineEdit_tags = QLineEdit(self)
        self.lineEdit_tags.setText('test')

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



class CustomMessageBox(QDialog):
    def __init__(self, options):
        super().__init__()

        self.options = options
        self.selected_option = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('选择一个选项')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.radio_buttons = []

        for option in self.options:
            radio_button = QRadioButton(option, self)
            radio_button.clicked.connect(self.radio_button_clicked)
            layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def radio_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            self.selected_option = sender.text()