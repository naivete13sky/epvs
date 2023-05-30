import json
import os
import shutil
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QDialog, QFileDialog
from ui.dialogImport import Ui_Dialog as DialogImport
from epkernel import Input
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





class DialogImport(QDialog,DialogImport):
    triggerDialogImportStr = QtCore.pyqtSignal(str)  # trigger传输的内容是字符串
    triggerDialogImportList = QtCore.pyqtSignal(list)
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

            Input.open_job(self.jobName, os.path.dirname(self.lineEditOdbFolderPath.text()))  # 用悦谱CAM打开料号
            currentJobSteps = Information.get_steps(self.jobName)
            self.comboBoxStepName.addItems(currentJobSteps)
            # GUI.show_layer(self.jobName,'orig','abc')

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


    def on_ok_button_clicked(self):
        # 在这里添加要执行的代码
        logger.info("用户单击了“OK”按钮")
        layer_list = Information.get_layers(self.jobName)
        self.triggerDialogImportList.emit(layer_list)
        self.step = self.comboBoxStepName.currentText()