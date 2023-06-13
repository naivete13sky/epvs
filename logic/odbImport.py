import json
import os
import shutil
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QDialog, QFileDialog, QProgressDialog, QMessageBox

from logic import gl
from ui.dialogImport import Ui_Dialog as DialogImport
from epkernel import Input
from epkernel.Action import Information

from logic.log import MyLog
logger = MyLog.log_init()





class DialogImport(QDialog,DialogImport):
    triggerDialogImportStr = QtCore.pyqtSignal(str)  # trigger传输的内容是字符串
    triggerDialogImportList = QtCore.pyqtSignal(list)
    FlagImportCurrent = False
    def __init__(self,whichJob):
        super(DialogImport, self).__init__()
        self.setupUi(self)
        self.whichJob = whichJob

        self.comboBoxType.currentIndexChanged.connect(self.odbTypeSelectionChanged)

        self.pushButtonSelectOdb.clicked.connect(self.select_folder)
        self.pushButtonImport.clicked.connect(self.odbImport)
        self.buttonBox.accepted.connect(self.on_ok_button_clicked)

    def odbTypeSelectionChanged(self, index):
        if self.sender().currentText() == 'tgz':
            logger.info("tgz")


        if self.sender().currentText() == '文件夹':
            logger.info("文件夹")

        # if len(self.lineEditGerberFolderPath.text()) > 0:
        #     self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
        #     self.jobName = self.lineEditJobName.text()
        #     self.step = self.lineEditStep.text()

    def select_folder(self):
        if self.comboBoxType.currentText() == '文件夹':
            folder_dialog = QFileDialog()
            folder_dialog.setFileMode(QFileDialog.Directory)

            # 实时预览当前路径下的所有文件
            folder_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            folder_dialog.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)

            if folder_dialog.exec_() == QFileDialog.Accepted:
                self.folder_path = folder_dialog.selectedFiles()[0]

                self.lineEditOdbFolderPath.setText(self.folder_path)


                self.lineEditJobName.setText(self.folder_path.split("/")[-1])



                self.triggerDialogImportStr.emit("我是triggerDialogImportStr发的信号！")
                # self.triggerDialogInputList.emit(file_list)
        if self.comboBoxType.currentText() == 'tgz':
            file_dialog = QFileDialog()
            self.file_path, _ = file_dialog.getOpenFileName(self, 'Select File')
            if self.file_path:

                self.lineEditOdbFolderPath.setText(self.file_path)
                # self.lineEditJobName.setText(self.file_path.split("/")[-1][:-4])
                self.triggerDialogImportStr.emit("我是triggerDialogImportStr发的信号！")
                # self.triggerDialogInputList.emit(file_list)



    def odbImport(self):
        logger.info("用户单击了“Import”按钮")

        # region 是否已加载EPCAM
        if gl.FlagEPCAM == False:
            # 加载EPCAM进度条
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

            self.triggerDialogImportStr.emit('已加载EPCAM')




        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.settingsDict = json.load(cfg)  # (json格式数据)字符串 转化 为字典
        self.temp_path = self.settingsDict['general']['temp_path']
        self.temp_path_g = self.settingsDict['g']['temp_path_g']

        self.tempGOutputPathCompareResult = os.path.join(self.temp_path, r'output_compare_result')
        if not os.path.exists(self.tempGOutputPathCompareResult):
            os.mkdir(self.tempGOutputPathCompareResult)



        if self.comboBoxType.currentText() == '文件夹':
            pass



            logger.info("导入文件夹:"+str(self.lineEditOdbFolderPath.text()))
            self.jobName = self.lineEditJobName.text()
            # print("cc hello")
            # Input.open_job('naivete13sky',r'C:\job\odb')
            # print("cc hello2")





            Input.open_job(self.jobName, os.path.dirname(self.lineEditOdbFolderPath.text()))  # 用悦谱CAM打开料号
            currentJobSteps = Information.get_steps(self.jobName)
            self.comboBoxStepName.addItems(currentJobSteps)
            # GUI.show_layer(self.jobName,'orig','abc')
            self.FlagImportCurrent = True
            QMessageBox.information(self,'已完成Import','已完成Import!')

        if self.comboBoxType.currentText() == 'tgz':
            pass
            logger.info("导入tgz:"+str(self.lineEditOdbFolderPath.text()))
            self.jobName = self.lineEditJobName.text()

            #复制tgz到odb文件夹，并解压,复制单个文件
            #先删除临时文件夹temp,再创建
            temp_tgz_path = os.path.join(self.temp_path,'temp')
            if os.path.exists(temp_tgz_path):
                shutil.rmtree(temp_tgz_path)
                time.sleep(0.1)
            os.mkdir(temp_tgz_path)
            src_file = self.lineEditOdbFolderPath.text()
            dst_file = os.path.join(temp_tgz_path,os.path.basename(self.lineEditOdbFolderPath.text()))
            shutil.copy(src_file, dst_file)
            time.sleep(0.1)

            from ccMethod.ccMethod import CompressTool
            CompressTool.untgz(os.path.join(temp_tgz_path, os.listdir(temp_tgz_path)[0]),
                               temp_tgz_path)
            if os.path.exists(os.path.join(temp_tgz_path, os.path.basename(self.lineEditOdbFolderPath.text()))):
                os.remove(os.path.join(temp_tgz_path, os.path.basename(self.lineEditOdbFolderPath.text())))
            # return os.listdir(temp_compressed_path)[0].lower()
            untgz_odb_folder_name = os.listdir(temp_tgz_path)[0]

            self.lineEditJobName.setText(untgz_odb_folder_name)
            self.jobName = self.lineEditJobName.text()

            Input.open_job(self.jobName, temp_tgz_path)  # 用悦谱CAM打开料号
            # GUI.show_layer(self.jobName, 'orig', 'abc')
            currentJobSteps = Information.get_steps(self.jobName)
            self.comboBoxStepName.addItems(currentJobSteps)
            self.FlagImportCurrent = True
            QMessageBox.information(self, '已完成Import', '已完成Import!')


    def on_ok_button_clicked(self):
        # 在这里添加要执行的代码
        logger.info("用户单击了“OK”按钮")
        if not self.FlagImportCurrent:
            QMessageBox.information(self, '请先Import', '请先Import!')
            return


        layer_list = Information.get_layers(self.jobName)
        self.triggerDialogImportList.emit(layer_list)
        self.step = self.comboBoxStepName.currentText()

        self.triggerDialogImportStr.emit('料号Import完成' + '|' + self.whichJob)