import configparser
import json
import os
import shutil
import sys
import time
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QDir, QSettings, QFile, QTextStream
from PyQt5.QtGui import QFont, QPalette, QColor, QTextImageFormat, QPixmap, QIcon
from ui.mainWindow import Ui_MainWindow
from ui.dialogInput import Ui_Dialog as DialogInput
from PyQt5.QtWidgets import *
from epkernel import GUI, Input
from epkernel.Action import Information
from ui.settings import Ui_Dialog as DialogSettings
from ui.dialogImport import Ui_Dialog as DialogImport


class MainWindow(QMainWindow,Ui_MainWindow):
    FlagInputA = False#料号A的Input状态为False表示还没有成功转图
    FlagInputB = False
    FlagImportA = False  # 料号A的Import状态为False表示还没有成功转图
    FlagImportB = False

    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.setGeometry(300, 30, 1200, 800)

        # region 设置料号A的状态信息，是label控件。设置料号B也一样。
        # 创建一个QPalette对象
        palette = QPalette()
        # 设置背景颜色为白色
        # palette.setColor(QPalette.Window, QColor(255, 255, 255))
        # 设置字体颜色
        palette.setColor(QPalette.WindowText, QColor(255, 0, 0))#白色是QColor(255, 255, 255)
        # 将QPalette应用于QLabel
        self.labelStatusJobA.setPalette(palette)
        self.labelStatusJobB.setPalette(palette)
        # endregion


        # region 设置表格
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
        # endregion


        # region 连接信号槽
        self.pushButtonInputA.clicked.connect(self.inputA)
        self.pushButtonImportA.clicked.connect(self.importA)
        self.pushButtonInputB.clicked.connect(self.inputB)
        self.pushButtonImportB.clicked.connect(self.importB)
        self.pushButtonVS.clicked.connect(self.vs)
        self.pushButtonJobAReset.clicked.connect(self.jobAReset)
        self.pushButtonJobBReset.clicked.connect(self.jobBReset)
        self.pushButtonAllReset.clicked.connect(self.allReset)
        self.pushButtonSettings.clicked.connect(self.settingsShow)
        self.pushButtonHelp.clicked.connect(self.helpShow)
        # endregion

    #退出主界面的确认
    def closeEvent(self, event):
        # 创建一个消息框
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle('确认退出')
        message_box.setText('确定要退出吗？')

        # 添加确认和取消按钮
        confirm_button = message_box.addButton('确认', QMessageBox.AcceptRole)
        cancel_button = message_box.addButton('取消', QMessageBox.RejectRole)

        # 显示消息框，并等待用户响应
        message_box.exec_()

        # 判断用户点击的是哪个按钮
        if message_box.clickedButton() == confirm_button:
            event.accept()
        else:
            event.ignore()

    #料号A的Input
    def inputA(self):
        '''使用QThread'''
        print("inputA")
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
            layerName = str(message.split("|")[3])
            # 在总表中要根据层名称来更新
            for row in range(self.tableWidgetVS.rowCount()):
                if self.tableWidgetVS.item(row, 0).text().lower() == layerName:
                    pass
                    self.tableWidgetVS.setCellWidget(row, 1,
                                                     self.dialogInputA.buttonForRowTranslateEPLayerName(layerName))



        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="A":
                print("料号转图完成message:",message.split("|")[2])
                self.labelStatusJobA.setText('状态：'+'转图完成' + '|' + message.split("|")[2])

                #转图按钮设置背景色为绿色
                self.pushButtonInputA.setStyleSheet('background-color: green')
                # self.pushButtonInputA.setStyleSheet('background-color: %s' % QColor(0, 255, 0).name())
                print("转图按钮设置背景色为绿色")
                self.FlagInputA = True





    def update_text_start_input_A_get_list(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(str(message))

        #总表中存量文件数量
        self.currentMainTableFilesCount = self.tableWidgetVS.rowCount()
        print('self.currentMainTableFilesCount:',self.currentMainTableFilesCount)
        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)
            print('self.file_count2:',self.file_count,'message2:',message)
            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            print("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            self.file_count = len(message)
            i=0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    print("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
                    # print("有新文件",message[each],self.currentMainTableFilesCount -1 + i)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))


    def importA(self):
        '''使用普通方法import'''
        print("importA:")
        if not hasattr(self, 'dialogImportA') or self.dialogImportA is None:
            self.dialogImportA = DialogImport("A")
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogImportA.setWindowTitle('料号A')
            self.dialogImportA.triggerDialogImportStr.connect(self.update_text_start_import_A_get_str)  # 连接信号！
            self.dialogImportA.triggerDialogImportList.connect(self.update_text_start_import_A_get_list)
        self.dialogImportA.show()

    def update_text_start_import_A_get_str(self,message):
        self.textBrowserMain.append(message)

    def update_text_start_import_A_get_list(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(str(message))

        #总表中存量文件数量
        self.currentMainTableFilesCount = self.tableWidgetVS.rowCount()
        print('self.currentMainTableFilesCount:',self.currentMainTableFilesCount)
        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text().lower() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)
            print('self.file_count2:',self.file_count,'message2:',message)
            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
                self.tableWidgetVS.setCellWidget(each, 1,
                                                 self.buttonForRowLayerName(self.dialogImportA,message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            print("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            self.file_count = len(message)
            i=0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    print("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
                    # print("有新文件",message[each],self.currentMainTableFilesCount -1 + i)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))
                    self.tableWidgetVS.setCellWidget(self.currentMainTableFilesCount -1 + i, 1,
                                                     self.buttonForRowLayerName(self.dialogImportA,message[each]))
        if len(message)>0:
            self.pushButtonImportA.setStyleSheet('background-color: green')
            self.FlagImportA = True

    def buttonForRowLayerName(self,jobDialogImport, layerName):
        '''
        # 列表内添加按钮EP
        :param id:
        :return:
        '''
        widget = QWidget()


        # 查看
        viewBtn = QPushButton('查看')
        viewBtn.setStyleSheet(''' text-align : center;
                                  background-color : DarkSeaGreen;
                                  height : 30px;
                                  border-style: outset;
                                  font : 13px; ''')

        viewBtn.clicked.connect(lambda: self.viewLayerEPLayerName(jobDialogImport,layerName))
        hLayout = QHBoxLayout()
        hLayout.addWidget(viewBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget


    def viewLayerEPLayerName(self, jobDialogImport,layerName):
        '''
        # 用EPCAM查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass
        # print("layer id:",id)
        layerName = layerName.lower()
        print("jobName:", jobDialogImport.jobName,"layerName:", layerName)
        GUI.show_layer(jobDialogImport.jobName, jobDialogImport.step, layerName)


    def jobAReset(self):
        pass
        print("释放jobA")

        # self.dialogInputA.deleteLater()
        # self.dialogInputA = None
        # self.tableWidgetVS.clear()
        # self.tableWidgetVS.setRowCount(0)

        # if hasattr(self, 'dialogInputA') or self.dialogInputA is not None:
        if hasattr(self, 'dialogInputA') and self.dialogInputA is not None:
            print("Dialog exists!")
            self.dialogInputA.deleteLater()
            self.dialogInputA = None
            self.tableWidgetVS.clear()
            self.tableWidgetVS.setRowCount(0)

            # 设置列标签
            column_labels = ["文件名", "料号A转图结果", "比图结果", "料号B转图结果", "说明"]
            self.tableWidgetVS.setHorizontalHeaderLabels(column_labels)

        # 设置自动填充背景属性为True
        self.pushButtonInputA.setStyleSheet('')
        self.FlagInputA = False
        self.pushButtonImportA.setStyleSheet('')
        self.FlagImportA = False
        self.labelStatusJobA.setText('状态：'+"已重置")





    def inputB(self):
        print("inputB")
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
            layerName = str(message.split("|")[3])
            #在总表中要根据层名称来更新
            for row in range(self.tableWidgetVS.rowCount()):
                if self.tableWidgetVS.item(row,0).text().lower() == layerName:
                    pass
                    self.tableWidgetVS.setCellWidget(row,3,self.dialogInputB.buttonForRowTranslateEPLayerName(layerName))


        if message.split("|")[0] =="料号转图完成":
            if message.split("|")[1] =="B":
                print("料号转图完成message:",message.split("|")[2])
                self.labelStatusJobB.setText('状态：'+'转图完成' + '|' + message.split("|")[2])

                # 转图按钮设置背景色为绿色
                self.pushButtonInputB.setStyleSheet('background-color: green')
                # self.pushButtonInputA.setStyleSheet('background-color: %s' % QColor(0, 255, 0).name())
                print("转图按钮设置背景色为绿色")
                self.FlagInputB = True

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
            self.file_count = len(message)
            # 如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            i = 0
            print('self.file_count_b:',self.file_count,'message_b:',message)
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
                    # print("有新文件",message[each],self.currentMainTableFilesCount -1 + i)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))

    def importB(self):
        '''使用普通方法import'''
        print("importB:")
        if not hasattr(self, 'dialogImportB') or self.dialogImportB is None:
            self.dialogImportB = DialogImport("B")
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogImportB.setWindowTitle('料号A')
            self.dialogImportB.triggerDialogImportStr.connect(self.update_text_start_import_B_get_str)  # 连接信号！
            self.dialogImportB.triggerDialogImportList.connect(self.update_text_start_import_B_get_list)
        self.dialogImportB.show()

    def update_text_start_import_B_get_str(self,message):
        self.textBrowserMain.append(message)

    def update_text_start_import_B_get_list(self, message):
        '''
        。
        :param message:
        :return:
        '''
        self.textBrowserMain.append(str(message))

        #总表中存量文件数量
        self.currentMainTableFilesCount = self.tableWidgetVS.rowCount()
        print('self.currentMainTableFilesCount:',self.currentMainTableFilesCount)
        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text().lower() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)
            print('self.file_count2:',self.file_count,'message2:',message)
            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
                self.tableWidgetVS.setCellWidget(each, 3,
                                                 self.buttonForRowLayerName(self.dialogImportB,message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            print("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            self.file_count = len(message)
            i=0
            for each in range(self.file_count):
                if message[each] in self.currentMainTableFilesList:
                    for row in range(self.tableWidgetVS.rowCount()):
                        if self.tableWidgetVS.item(row,0).text().lower() == message[each]:
                            pass
                            self.tableWidgetVS.setCellWidget(row, 3,
                                                             self.buttonForRowLayerName(self.dialogImportB, message[each]))
                if message[each] not in self.currentMainTableFilesList:
                    print("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
                    # print("有新文件",message[each],self.currentMainTableFilesCount -1 + i)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))
                    self.tableWidgetVS.setCellWidget(self.currentMainTableFilesCount -1 + i, 3,
                                                     self.buttonForRowLayerName(self.dialogImportB,message[each]))
        if len(message)>0:
            self.pushButtonImportB.setStyleSheet('background-color: green')
            self.FlagImportB = True




    def jobBReset(self):
        pass
        print("释放jobB")
        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            print('Dialog exists!')
            self.dialogInputB.deleteLater()
            self.dialogInputB = None
            self.tableWidgetVS.clear()
            self.tableWidgetVS.setRowCount(0)
            # 设置列标签
            column_labels = ["文件名", "料号A转图结果", "比图结果", "料号B转图结果", "说明"]
            self.tableWidgetVS.setHorizontalHeaderLabels(column_labels)

        # 设置自动填充背景属性为True
        self.pushButtonInputB.setStyleSheet('')
        self.FlagInputB = False
        self.pushButtonImportB.setStyleSheet('')
        self.FlagImportB = False
        self.labelStatusJobB.setText('状态：' + "已重置")


    def vs(self):
        pass
        if self.comboBoxVSMethod.currentText()=='方案1：G比图':
            self.vsG()

    def vsG(self):
        pass
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
        self.textBrowserMain.append(message)
        if message.split("|")[0] == "更新G比图结果":
            current_row = int(message.split("|")[1])
            current_row_result = message.split("|")[2]
            self.tableWidgetVS.setCellWidget(current_row, 2, self.buttonForRowCompareG(str(current_row),current_row_result))

    def buttonForRowCompareG(self, id,button_text):
        '''
        # 列表内添加按钮
        :param id:
        :return:
        '''
        widget = QWidget()

        # 查看
        viewBtn = QPushButton(button_text)
        if button_text == '正常':
            viewBtn.setStyleSheet(''' text-align : center;
                                      background-color : DarkSeaGreen;
                                      height : 30px;
                                      border-style: outset;
                                      font : 13px; ''')
        if button_text == '错误':
            viewBtn.setStyleSheet(''' text-align : center;
                                      background-color : red;
                                      height : 30px;
                                      border-style: outset;
                                      font : 13px; ''')
        if button_text == '异常':
            # ffff00
            viewBtn.setStyleSheet(''' text-align : center;
                                      background-color : yellow;
                                      height : 30px;
                                      border-style: outset;
                                      font : 13px; ''')

        viewBtn.clicked.connect(lambda: self.viewLayerCompareResultG(id))
        hLayout = QHBoxLayout()
        hLayout.addWidget(viewBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget

    def viewLayerCompareResultG(self,id):
        '''
        # 用EPCAM查看G比图的结果
        :param id:
        :return:
        '''

        # print("layer id:",id)
        layerName = self.tableWidgetVS.item(int(id),0).text().lower()
        # print("layerName:",layerName)
        print("看图！")
        #用EPCAM打开。
        if self.FlagInputB:
            step = self.dialogInputB.step
            job1 = self.dialogInputB.jobName
        if self.FlagImportB:
            step = self.dialogImportB.step
            job1= self.dialogImportB.jobName
        self.jobNameGCompareResult = job1 + '_comRes'
        GUI.show_layer(self.jobNameGCompareResult, step, layerName)



    def allReset(self):

        print("重置所有")
        if hasattr(self, 'dialogInputA') and self.dialogInputA is not None:
            print('Dialog exists!')
            self.dialogInputA.deleteLater()
            self.dialogInputA = None
        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            print('Dialog exists!')
            self.dialogInputB.deleteLater()
            self.dialogInputB = None

        # 设置自动填充背景属性为True
        self.pushButtonInputA.setStyleSheet('')
        self.pushButtonInputB.setStyleSheet('')
        self.FlagInputA = False
        self.FlagInputB = False
        self.pushButtonImportA.setStyleSheet('')
        self.pushButtonImportB.setStyleSheet('')
        self.FlagImportA = False
        self.FlagImportB = False
        self.tableWidgetVS.clear()
        self.tableWidgetVS.setRowCount(0)
        # 设置列标签
        column_labels = ["文件名", "料号A转图结果", "比图结果", "料号B转图结果", "说明"]
        self.tableWidgetVS.setHorizontalHeaderLabels(column_labels)
        self.labelStatusJobA.setText('状态：' + "已重置")
        self.labelStatusJobB.setText('状态：' + "已重置")

    def settingsShow(self):
        pass
        if not hasattr(self, 'dialogSettings') or self.dialogSettings is None:
            print("需要创建配置窗口")
            self.dialogSettings = DialogSettings()
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            # self.dialogSettings.setWindowTitle('配置')
            # self.dialogInputA.triggerDialogInputStr.connect(self.update_text_start_input_A_get_str)  # 连接信号！

        self.dialogSettings.show()


    def helpShow(self):
        pass
        if not hasattr(self, 'windowHelp') or self.windowHelp is None:
            print("需要创建配置窗口")
            self.windowHelp = WindowHelp()
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            # self.dialogSettings.setWindowTitle('配置')
            # self.dialogInputA.triggerDialogInputStr.connect(self.update_text_start_input_A_get_str)  # 连接信号！

        self.windowHelp.show()


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
        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.temp_path = self.settings_dict['general']['temp_path']
        self.temp_path_remote = self.settings_dict['g']['temp_path_remote']
        # self.temp_path_remote = self.temp_path.replace(r'C:\cc',r'\\vmware-host\Shared Folders')

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
            # print("self.gateway_path:", self.gateway_path)
            self.gSetupType = self.json['g']['gSetupType']
            if self.gSetupType == 'local':
                # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                shutil.rmtree(self.tempGerberPath)
            if self.gSetupType == 'vmware':
                #使用PsExec通过命令删除远程机器的文件
                from ccMethod.ccMethod import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path='C:\cc\python\epwork\epvs\ccMethod',computer='192.168.1.3', username='administrator', password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = os.path.join(self.temp_path_remote,'gerber',self.jobName)
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)

                print("remote delete finish")
                # time.sleep(20)

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
                print("料号转图完成message:",message.split("|")[2])
                self.triggerDialogInputStr.emit(message)

            if message.split("|")[1] =="B":
                print("料号转图完成message:",message.split("|")[2])
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
        # print("layer id:",id)
        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()
        # print("layerName:",layerName)
        GUI.show_layer(self.jobName, self.step, layerName)

    def viewLayerGLayerName(self, layerName):
        '''
        # 用G查看悦谱转图的结果
        :param id:
        :return:
        '''
        pass
        # print("layer id:",id)
        layerName = layerName.lower()
        print("layerName:", layerName)
        GUI.show_layer(self.jobName, self.step, layerName)


    def on_ok_button_clicked(self):
        pass
        # currnet_layer_list = Information.get_layers(self.jobName)
        # if len(currnet_layer_list)>0:
        #     self.triggerDialogInputStr.emit(self.whichJob + "_" + "highLight")
        self.close()


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


class MyThreadStartTranslateG(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    #下面这个init方法，是通常用法。一般在QThread中不需要直接获取窗口控件时使用。
    # def __init__(self, parent=None):
    #     super(MyThreadStartEPCAM, self).__init__(parent)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc,whichJob,whichTranslateMethod):
        super(MyThreadStartTranslateG, self).__init__()
        self.ussd = cc
        self.whichJob = whichJob
        self.whichTranslateMethod = whichTranslateMethod



    def run(self): # 很多时候都必重写run方法, 线程start后自动运行
        self.my_function()

    def my_function(self):
        self.trigger.emit("开始G转图！")
        self.trigger.emit("正在G转图！")
        from config_g.g import G
        from epkernel import Input
        from epkernel.Action import Information
        from epkernel import GUI

        #如果料号名被更改了，那么要重新copy一份gerber文件来。
        self.ussd.jobName = self.ussd.lineEditJobName.text()
        self.ussd.tempGerberPath = os.path.join(self.ussd.tempGerberParentPath, self.ussd.jobName)
        if os.path.exists(self.ussd.tempGerberPath):
            # 读取配置文件
            with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
                self.json = json.load(cfg)
            self.gSetupType = self.json['g']['gSetupType']
            self.temp_path = self.json['general']['temp_path']
            if self.gSetupType == 'local':
                # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                shutil.rmtree(self.ussd.tempGerberPath)
            if self.gSetupType == 'vmware':
                # 使用PsExec通过命令删除远程机器的文件
                from ccMethod.ccMethod import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path=r'ccMethod', computer='192.168.1.3',
                                        username='administrator', password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = os.path.join(self.ussd.temp_path_remote, 'gerber', self.ussd.jobName)
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)




            shutil.copytree(self.ussd.folder_path, self.ussd.tempGerberPath)
        else:
            shutil.copytree(self.ussd.folder_path, self.ussd.tempGerberPath)

        # 读取配置文件
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.json = json.load(cfg)
        self.gateway_path = self.json['g']['gateway_path']  # (json格式数据)字符串 转化 为字典
        print("self.gateway_path:", self.gateway_path)
        self.gSetupType = self.json['g']['gSetupType']
        self.temp_path_remote = self.json['g']['temp_path_remote']
        self.GENESIS_DIR = self.json['g']['GENESIS_DIR']


        self.g = G(self.gateway_path,gSetupType=self.gSetupType,GENESIS_DIR=self.GENESIS_DIR)
        # 先清空料号
        if self.gSetupType == 'local':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path_remote,r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path_remote,r'job_list.txt'))
        if self.gSetupType == 'vmware':
            self.g.clean_g_all_pre_get_job_list(os.path.join(self.temp_path_remote, r'job_list.txt'))
            self.g.clean_g_all_do_clean(os.path.join(self.temp_path, r'job_list.txt'))
            # self.g.clean_g_all_pre_get_job_list(r'//vmware-host/Shared Folders/share/epvs/job_list.txt')
            # self.g.clean_g_all_do_clean(r'C:\cc\share\epvs\job_list.txt')

        gerberList_path = []
        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            each_dict = {}
            gerberFolderPathG = os.path.join(r"Z:\share", r'epvs\gerber', self.ussd.jobName)
            print('gerberFolderPathG:', gerberFolderPathG)
            each_dict['path'] = os.path.join(gerberFolderPathG, self.ussd.tableWidgetGerber.item(row, 0).text())
            if self.ussd.tableWidgetGerber.item(row, 1).text() in ['Excellon2', 'excellon2', 'Excellon', 'excellon']:
                each_dict['file_type'] = 'excellon'
                each_dict_para = {}
                each_dict_para['zeroes'] = self.ussd.tableWidgetGerber.item(row, 2).text()
                each_dict_para['nf1'] = int(self.ussd.tableWidgetGerber.item(row, 3).text())
                each_dict_para['nf2'] = int(self.ussd.tableWidgetGerber.item(row, 4).text())
                each_dict_para['units'] = self.ussd.tableWidgetGerber.item(row, 5).text()
                each_dict_para['tool_units'] = self.ussd.tableWidgetGerber.item(row, 6).text()
                each_dict['para'] = each_dict_para
            elif self.ussd.tableWidgetGerber.item(row, 1).text() in ['Gerber274x', 'gerber274x']:
                each_dict['file_type'] = 'gerber'
            else:
                each_dict['file_type'] = ''
            gerberList_path.append(each_dict)
        print("gerberList_path:", gerberList_path)

        # gerberList_path = [{"path": r"C:\temp\gerber\nca60led\Polaris_600_LED.DRD", "file_type": "excellon"},
        #                    {"path": r"C:\temp\gerber\nca60led\Polaris_600_LED.TOP", "file_type": "gerber274x"}]

        self.g.input_init(job=self.ussd.jobName, step=self.ussd.step, gerberList_path=gerberList_path,jsonPath=r'settings\epvs.json')

        out_path_g = os.path.join(r'Z:\share', r'epvs\odb')
        self.g.g_export(self.ussd.jobName, out_path_g, mode_type='directory')

        out_path_local = self.ussd.tempODBParentPath
        Input.open_job(self.ussd.jobName, out_path_local)  # 用悦谱CAM打开料号
        # GUI.show_layer(self.jobNameG, self.step, "")

        # G转图情况，更新到表格中
        all_layers_list_job = Information.get_layers(self.ussd.jobName)
        print("all_layers_list_job:", all_layers_list_job)
        # print('self.ussd.tableWidgetGerber.rowCount():',self.ussd.tableWidgetGerber.rowCount())
        for row in range(self.ussd.tableWidgetGerber.rowCount()):
            # print("row:",row)
            current_layerName = self.ussd.tableWidgetGerber.item(row, 0).text().lower()
            if current_layerName in all_layers_list_job:
                self.trigger.emit("更新料号"+self.whichJob+'转图结果|'+self.ussd.translateMethod+'|'+str(row)+'|'+current_layerName)

        self.trigger.emit("已完成G转图！")
        self.ussd.textBrowserLog.append("我可以直接在Qthread中设置窗口")
        all_step_list_job = Information.get_steps(self.ussd.jobName)
        if len(all_layers_list_job) > 0:
            self.trigger.emit("料号转图完成|"+self.whichJob+'|'+self.ussd.translateMethod)
        #把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。
        print("把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。")
        self.g.input_reset(self.ussd.jobName)


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
        print("self.gateway_path:", self.gateway_path)
        self.gSetupType = self.json['g']['gSetupType']
        self.g = G(self.gateway_path,gSetupType=self.gSetupType)




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
            # print('jobAList:', jobAList)
            jobBList = [(self.ussd.dialogInputB.tableWidgetGerber.item(each, 0).text(),self.ussd.dialogInputB.tableWidgetGerber.item(each, 1).text()) for each in
                        range(self.ussd.dialogInputB.tableWidgetGerber.rowCount())]
            # print('jobBList:', jobBList)
            setA = set(jobAList)
            setB = set(jobBList)
            intersection = setA.intersection(setB)
            jobABList = list(intersection)
            # print('jobABList:',jobABList)
            jobABLayerNameList = [each[0] for each in jobABList]
            # print('jobABLayerNameList:', jobABLayerNameList)

            layerInfo = []
            print('self.ussd.tableWidgetVS.rowCount():',self.ussd.tableWidgetVS.rowCount())
            for row in range(self.ussd.tableWidgetVS.rowCount()):
                if self.ussd.tableWidgetVS.item(row, 0).text() in jobABLayerNameList:
                    pass
                    each_dict = {}
                    each_file = self.ussd.tableWidgetVS.item(row, 0).text()
                    print('each_file:',each_file)
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
            print("料号A与料号B至少有一个不是Input转图的，这个时候要比图的层通过总表来判断，看看哪些层是2个料号里都存在转图成功的。")

            # job1 = self.ussd.dialogInputB.jobName
            # job2 = self.ussd.dialogInputA.jobName
            # step1 = self.ussd.dialogInputB.step
            # step2 = self.ussd.dialogInputA.step

            # layerInfo = []
            # for row in range(self.ussd.tableWidgetVS.rowCount()):
            #     if isinstance(self.ussd.tableWidgetVS.cellWidget(row,1),QPushButton) and isinstance(self.ussd.tableWidgetVS.cellWidget(row,3),QPushButton):
            #         print("i find it:")
            #         each_dict = {}
            #         each_file = self.ussd.tableWidgetVS.item(row, 0).text()
            #         print('each_file:', each_file)
            #         each_dict["layer"] = each_file.lower()
            #         each_dict['layer_type'] = ''#所有层都不区分是gerber还是孔了。
            #         layerInfo.append(each_dict)

            # 找出料号A与料号B共同的层名。只有共同层才需要比图。
            jobAList = [(each,"") for each in Information.get_layers(job2)]
            # print('jobAList:', jobAList)
            jobBList = [(each,"") for each in Information.get_layers(job1)]
            # print('jobBList:', jobBList)
            setA = set(jobAList)
            setB = set(jobBList)
            intersection = setA.intersection(setB)
            jobABList = list(intersection)
            # print('jobABList:',jobABList)
            jobABLayerNameList = [each[0] for each in jobABList]
            print('jobABLayerNameList:',jobABLayerNameList)
            layerInfo = []
            print('self.ussd.tableWidgetVS.rowCount():', self.ussd.tableWidgetVS.rowCount())
            for row in range(self.ussd.tableWidgetVS.rowCount()):
                if self.ussd.tableWidgetVS.item(row, 0).text().lower() in jobABLayerNameList:
                    pass
                    each_dict = {}
                    each_file = self.ussd.tableWidgetVS.item(row, 0).text()
                    print('each_file:', each_file)
                    each_dict["layer"] = each_file.lower()
                    each_dict['layer_type'] = ''#所有层都不区分是gerber还是孔了。
                    layerInfo.append(each_dict)




        print('layerInfo:',layerInfo)





        # 先清空料号
        self.g.clean_g_all_pre_get_job_list(r'//vmware-host/Shared Folders/share/job_list.txt')
        self.g.clean_g_all_do_clean(r'C:\cc\share\job_list.txt')

        #导料号
        self.g.import_odb_folder(os.path.join(r'Z:\share',  r'epvs\odb',job1))
        self.g.import_odb_folder(os.path.join(r'Z:\share', r'epvs\odb', job2))

        self.g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)
        compareResult = self.g.layer_compare(temp_path=r'c:\cc\share\epvs',temp_path_vm_parent=r'Z:\share',
            job1=job1, step1=step1,
            job2=job2, step2=step2,
            layerInfo=layerInfo,
            adjust_position=False,jsonPath=r'settings/epvs.json')
        print('compareResult:',compareResult)
        self.trigger.emit("compareResult:"+str(compareResult))

        for row in range(self.ussd.tableWidgetVS.rowCount()):
            pass
            each_file = self.ussd.tableWidgetVS.item(row, 0).text().lower()
            each_file_compare_result = compareResult.get('all_result_g').get(each_file)
            print('each_file_compare_result:',each_file,each_file_compare_result)
            self.trigger.emit(each_file_compare_result)
            self.trigger.emit("更新G比图结果|" + str(row) + '|' + str(each_file_compare_result))

        # if translateResult == True:
        #     # self.ussd.tableWidgetGerber.setItem(row, 7, QTableWidgetItem("abc"))
        #     self.trigger.emit("更新悦谱转图结果|"+str(row))


        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        # BASE.save_job_as(self.ussd.jobName, self.ussd.tempEpOutputPath)

        #G比图后保存一下jobNameG
        self.g.save_job(job1)
        out_path_g_with_compare_result = os.path.join(r'Z:\share',  r'epvs', r'output_compare_result')
        self.g.g_export(job1, out_path_g_with_compare_result, mode_type='directory')
        # 改一下odb料号名称
        self.ussd.jobNameGCompareResult = job1 + '_comRes'
        if os.path.exists(os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult)):
            shutil.rmtree(os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult))
            time.sleep(0.8)

        os.rename(os.path.join(tempGOutputPathCompareResult, job1),
                  os.path.join(tempGOutputPathCompareResult, self.ussd.jobNameGCompareResult))
        #用EPCAM打开比过图的jobNameG_comRes
        Input.open_job(self.ussd.jobNameGCompareResult, tempGOutputPathCompareResult)  # 用悦谱CAM打开料号
        self.trigger.emit("已完成G比图！")
        self.ussd.textBrowserMain.append("我可以直接在Qthread中设置窗口")

        # 把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。
        print("把G软件的input 重置一下，防止主系统中无法删除gerber路径中的gerber文件。")
        self.g.input_reset(job1)


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
            print("tgz")


        if self.sender().currentText() == '文件夹':
            print("文件夹")

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
                print('folder_path:',self.folder_path)
                # self.load_folder(folder_path)
                self.lineEditOdbFolderPath.setText(self.folder_path)


                self.lineEditJobName.setText(self.folder_path.split("/")[-1])



                self.triggerDialogImportStr.emit("我是triggerDialogImportStr发的信号！")
                # self.triggerDialogInputList.emit(file_list)
        if self.comboBoxType.currentText() == 'tgz':
            file_dialog = QFileDialog()
            self.file_path, _ = file_dialog.getOpenFileName(self, 'Select File')
            if self.file_path:
                print(f"Selected File: {self.file_path}")
                self.lineEditOdbFolderPath.setText(self.file_path)
                # self.lineEditJobName.setText(self.file_path.split("/")[-1][:-4])
                self.triggerDialogImportStr.emit("我是triggerDialogImportStr发的信号！")
                # self.triggerDialogInputList.emit(file_list)



    def odbImport(self):
        print("用户单击了“Import”按钮")

        self.temp_path = os.path.join(r"C:\cc\share\epvs")
        self.temp_path_remote = self.temp_path.replace(r'C:\cc', r'\\vmware-host\Shared Folders')

        self.tempGOutputPathCompareResult = os.path.join(self.temp_path, r'output_compare_result')
        if not os.path.exists(self.tempGOutputPathCompareResult):
            os.mkdir(self.tempGOutputPathCompareResult)



        if self.comboBoxType.currentText() == '文件夹':
            pass
            print("导入文件夹:", self.lineEditOdbFolderPath.text())
            self.jobName = self.lineEditJobName.text()

            Input.open_job(self.jobName, os.path.dirname(self.lineEditOdbFolderPath.text()))  # 用悦谱CAM打开料号
            currentJobSteps = Information.get_steps(self.jobName)
            self.comboBoxStepName.addItems(currentJobSteps)
            # GUI.show_layer(self.jobName,'orig','abc')

        if self.comboBoxType.currentText() == 'tgz':
            pass
            print("导入tgz:", self.lineEditOdbFolderPath.text())
            self.jobName = self.lineEditJobName.text()

            #复制tgz到odb文件夹，并解压,复制单个文件
            #先删除临时文件夹temp,再创建
            temp_tgz_path =  r'c:/cc/share/epvs/temp'
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
        print("用户单击了“OK”按钮")
        layer_list = Information.get_layers(self.jobName)
        self.triggerDialogImportList.emit(layer_list)
        self.step = self.comboBoxStepName.currentText()



class DialogSettings(QDialog,DialogSettings):
    triggerDialogSettings = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    def __init__(self):
        super(DialogSettings,self).__init__()
        self.setupUi(self)

        # 参数
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.settingsDict = json.load(cfg)  # (json格式数据)字符串 转化 为字典
            # print("self.settingsDict:", self.settingsDict)
        # for k,v in self.settingsDict.items():
        #     print(k,v)

        self.treeWidgetSettings.setColumnCount(2)
        # 设置表头
        self.treeWidgetSettings.setHeaderLabels(['项目', '值'])
        self.treeWidgetSettings.setColumnWidth(0, 300)
        # self.treeWidgetSettings.setColumnWidth(1, 100)

        # # 创建根节点
        # root = QTreeWidgetItem(self.treeWidgetSettings, ['Root', ''])
        # self.add_dict_to_tree_widget(self.treeWidgetSettings,root,self.settingsDict)



        self.addTreeItems(self.treeWidgetSettings, self.settingsDict)
        self.treeWidgetSettings.itemDoubleClicked.connect(self.editItem)
        self.pushButtonSave.clicked.connect(self.settingsSave)

        self.treeWidgetSettings.expandAll()

    def addTreeItems(self, parent, data):
        # Add items to the tree widget recursively
        for key, value in data.items():
            if isinstance(value, dict):
                item = QTreeWidgetItem(parent, [key, ''])
                self.addTreeItems(item, value)
            else:
                item = QTreeWidgetItem(parent, [key, str(value)])


    def add_dict_to_tree_widget(self,tree_widget, parent_item, dict_obj):
        for key, value in dict_obj.items():
            # 如果当前值是字典，递归调用add_dict_to_tree_widget函数
            if isinstance(value, dict):
                # 创建一个新的节点，并将其作为当前节点的子节点
                child_item = QTreeWidgetItem(parent_item, [key, ''])
                self.add_dict_to_tree_widget(tree_widget, child_item, value)
            # 如果当前值不是字典，将其添加到当前节点
            else:
                child_item = QTreeWidgetItem(parent_item, [key, str(value)])


    def editItem(self, item, column):
        # Create a QLineEdit widget and set it as the editor for the clicked cell
        editor = QLineEdit(item.text(column), self)
        self.treeWidgetSettings.setItemWidget(item, column, editor)

        # When the user presses enter, update the cell's value and remove the editor widget
        editor.editingFinished.connect(lambda: self.updateItem(item, column, editor.text()))
        editor.editingFinished.connect(editor.deleteLater)
        editor.setFocus()

    def updateItem(self, item, column, text):
        # Update the tree widget item's value and set it back to read-only
        self.treeWidgetSettings.setItemWidget(item, column, None)
        item.setText(column, text)


    def printTree(self):
        # Print the contents of the tree widget to the console
        def printItems(parent, indent=0):
            for i in range(parent.childCount()):
                item = parent.child(i)
                print(' ' * indent + item.text(0) + ': ' + item.text(1))
                if item.childCount() > 0:
                    printItems(item, indent + 2)

        printItems(self.tree.invisibleRootItem())


    def settingsSave(self):
        parent = QTreeWidgetItem(self.treeWidgetSettings)
        root = self.treeWidgetSettings.invisibleRootItem()
        dict_data = self.tree_widget_to_dict(root)
        print(dict_data)
        # 转换为JSON对象并打印
        json_data = json.dumps(dict_data, indent=4)
        print(json_data)

        # 将JSON对象写入文件
        with open(r'settings/epvs.json', 'w',encoding='utf-8') as f:
            json.dump(dict_data, f,ensure_ascii=False,indent=4)


    def settingsSave2(self):
        root = self.treeWidgetSettings.invisibleRootItem()
        result = [self.tree_to_dict(root.child(i)) for i in range(root.childCount())]
        json_data = json.dumps(result)
        print(json_data)
        # 将JSON对象写入文件
        with open(r'settings/data.json', 'w') as f:
            json.dump(result, f,indent=4)




    def tree_widget_to_dict(self,item):
        """
        将QTreeWidget中的项目转换为字典
        只要对象形式，不要数组形式
        """
        result = {}
        for index in range(item.childCount()):
            child = item.child(index)
            if child.childCount() > 0:
                result[child.text(0)] = self.tree_widget_to_dict(child)
            else:
                result[child.text(0)] = child.text(1)
        return result


    def tree_to_dict(self,item):
        result = {}
        if item.childCount() == 0:
            result[item.text(0)] = item.text(1)

        else:
            result[item.text(0)] = [self.tree_to_dict(item.child(i)) for i in range(item.childCount())]

        return result


    def tree_to_dict_with_text_value(self,item):
        result = {}
        if item.childCount() == 0:
            result['text'] = item.text(0)
            result['value'] = item.text(1)
        else:
            result['text'] = item.text(0)
            result['children'] = [self.tree_to_dict(item.child(i)) for i in range(item.childCount())]
        return result




    def translateMethodSelectionChanged(self, index):
        pass


    def select_folder(self):
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)

        # 实时预览当前路径下的所有文件
        folder_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        folder_dialog.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)

        if folder_dialog.exec_() == QFileDialog.Accepted:
            self.folder_path = folder_dialog.selectedFiles()[0]
            print('folder_path:',self.folder_path)
            # # self.load_folder(folder_path)
            # self.lineEditGerberFolderPath.setText(self.folder_path)
            #
            #
            # self.lineEditJobName.setText(self.folder_path.split("/")[-1] + '_' + self.whichJob.lower() + '_' + self.whichTranslateMethod)
            # self.lineEditStep.setText("orig")
            #
            # # print('返回指定目录下的所有文件和目录名：', os.listdir(folder_path))
            # file_list = os.listdir(self.folder_path)
            # file_count = len(file_list)
            # # print(file_count)
            # self.tableWidgetGerber.setRowCount(file_count)
            # for each in range(file_count):
            #     self.tableWidgetGerber.setItem(each, 0, QTableWidgetItem(file_list[each]))
            # # 设置固定宽度为多少像素
            # self.tableWidgetGerber.setColumnWidth(0, 200)
            # self.tableWidgetGerber.setColumnWidth(1, 80)
            # self.tableWidgetGerber.setColumnWidth(2, 70)
            # self.tableWidgetGerber.setColumnWidth(3, 50)
            # self.tableWidgetGerber.setColumnWidth(4, 50)
            # self.tableWidgetGerber.setColumnWidth(5, 50)
            # self.tableWidgetGerber.setColumnWidth(6, 60)
            # # 设置自适应宽度
            # header = self.tableWidgetGerber.horizontalHeader()
            #
            # self.triggerDialogInputStr.emit("子窗口已获取文件列表！")
            # self.triggerDialogInputList.emit(file_list)


class WindowHelp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个QTextEdit控件
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # 创建一个菜单项和工具栏
        self.font_size_action = QAction('字体大小', self)
        self.font_size_action.triggered.connect(self.set_font_size)
        self.bold_action = QAction('加粗', self)
        # self.bold_action.triggered.connect(self.set_bold)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.italic_action = QAction('斜体', self)
        self.italic_action.triggered.connect(self.set_italic)
        self.underline_action = QAction('下划线', self)
        self.underline_action.triggered.connect(self.set_underline)
        self.color_action = QAction('颜色', self)
        self.color_action.triggered.connect(self.set_color)
        self.insert_image_action = QAction('插入图片', self)
        self.insert_image_action.triggered.connect(self.insert_image)

        self.save_action = QAction('保存', self)
        self.save_action.triggered.connect(self.save_text)

        self.load_action = QAction('加载', self)
        self.load_action.triggered.connect(self.load_text)


        menu = self.menuBar()
        file_menu = menu.addMenu('文件')
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)

        edit_menu = menu.addMenu('编辑')
        edit_menu.addAction(self.font_size_action)
        edit_menu.addAction(self.bold_action)
        edit_menu.addAction(self.italic_action)
        edit_menu.addAction(self.underline_action)
        edit_menu.addAction(self.color_action)
        edit_menu.addAction(self.insert_image_action)

        toolbar = self.addToolBar('文件')
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.load_action)
        toolbar = self.addToolBar('编辑')
        toolbar.addAction(self.font_size_action)
        toolbar.addAction(self.bold_action)
        toolbar.addAction(self.italic_action)
        toolbar.addAction(self.underline_action)
        toolbar.addAction(self.color_action)
        toolbar.addAction(self.insert_image_action)

        self.setGeometry(400, 100,1000, 800)

        # 加载上一次保存的文本内容
        settings = QSettings('MyCompany', 'MyApp')
        self.text_edit.setHtml(settings.value('text', ''))


    def save_text(self):
        filename, _ = QFileDialog.getSaveFileName(self, '保存文件', '.', 'Text files (*.txt)')
        if filename:
            file = QFile(filename)
            if file.open(QFile.WriteOnly | QFile.Text):
                stream = QTextStream(file)
                stream << self.text_edit.toHtml()
                file.close()

    def load_text(self):
        filename, _ = QFileDialog.getOpenFileName(self, '加载文件', '.', 'Text files (*.txt)')
        if filename:
            file = QFile(filename)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                self.text_edit.setHtml(stream.readAll())
                file.close()


    def set_font_size(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_edit.setFont(font)

    def set_bold(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setBold(not font.bold())
            self.text_edit.setCurrentFont(font)

    def toggle_bold(self):
        font = self.text_edit.currentFont()
        if font.weight() == QFont.Bold:
            font.setWeight(QFont.Normal)
        else:
            font.setWeight(QFont.Bold)
        self.text_edit.setCurrentFont(font)


    def set_italic(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontItalic(not text_format.fontItalic())
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setItalic(not font.italic())
            self.text_edit.setCurrentFont(font)

    def set_underline(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontUnderline(not text_format.fontUnderline())
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setUnderline(not font.underline())
            self.text_edit.setCurrentFont(font)

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                text_format = cursor.charFormat()
                text_format.setForeground(color)
                cursor.mergeCharFormat(text_format)
            else:
                self.text_edit.setTextColor(color)

    def insert_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择图片', '.', 'Image files (*.jpg *.gif *.png)')
        if filename:
            image = QTextImageFormat()
            image.setName(filename)
            pixmap = QPixmap(filename)
            image.setWidth(pixmap.width())
            image.setHeight(pixmap.height())
            cursor = self.text_edit.textCursor()
            cursor.insertImage(image)


    def closeEvent(self, event):
        # 保存当前文本内容
        settings = QSettings('MyCompany', 'MyApp')
        settings.setValue('text', self.text_edit.toHtml())
        event.accept()


