import json
import os
import shutil
import sys
import time
from pathlib import Path
import send2trash
import logic.gl as gl

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QDir, QSize, QRect, QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon, QTextDocument, QAbstractTextDocumentLayout, QKeySequence, QClipboard, QDesktopServices
from ui.mainWindow import Ui_MainWindow
from ui.dialogInput import Ui_Dialog as DialogInput
from PyQt5.QtWidgets import *
from epkernel import GUI, Input
from epkernel.Action import Information


from logic.help import WindowHelp
from logic.settings import DialogSettings
from logic.odbImport import DialogImport
from logic.compareG import MyThreadStartCompareG
from logic.translateG import MyThreadStartTranslateG


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

        # region 为了使得tab widget随着主窗口大小变化跟着调整
        layout_main = QVBoxLayout()
        # 将Tab Widget放置在布局管理器中
        layout_main.addWidget(self.tabWidget)
        # 创建一个容器窗口部件
        central_widget = QWidget()
        # 将布局管理器设置为容器窗口部件的布局
        central_widget.setLayout(layout_main)
        # 将容器窗口部件设置为主窗口的中央部件
        self.setCentralWidget(central_widget)
        # endregion

        # region 设置料号A的状态信息，是label控件。设置料号B也一样。
        palette = QPalette()
        # 设置背景颜色为白色
        # palette.setColor(QPalette.Window, QColor(255, 255, 255))
        # 设置字体颜色
        palette.setColor(QPalette.WindowText, QColor(255, 0, 0))#白色是QColor(255, 255, 255)
        # 将QPalette应用于QLabel
        self.labelStatusJobA.setPalette(palette)
        self.labelStatusJobB.setPalette(palette)
        # endregion

        # region 设置比对主表格
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
        # header = self.tableWidgetVS.horizontalHeader()
        # endregion

        # region 设置文件管理初始页面
        self.current_folder = ""  # 当前所选文件夹的路径
        self.back_history = []  # 文件夹路径的历史记录
        self.forward_history = []  # 前进路径的历史记录
        # 创建布局管理器，常用文件夹
        layout = QVBoxLayout()
        self.widgetLeftSiderTop.setLayout(layout)
        # 创建常用文件夹列表
        folder_list = QListWidget()
        folder_list.setStyleSheet("background-color: lightgray;")
        # 添加常用文件夹项
        folder_list.addItem("桌面")
        folder_list.addItem("下载")
        folder_list.addItem("文档")
        folder_list.addItem("图片")
        folder_list.addItem("音乐")
        folder_list.addItem("视频")
        # 将子QListWidget添加到布局管理器中
        layout.addWidget(folder_list)

        # 创建布局管理器，文件系统，树形结构
        layout = QVBoxLayout()
        self.widgetLeftSiderBot.setLayout(layout)
        # 创建文件树视图
        file_tree_view = QTreeView()
        file_tree_view.setStyleSheet("background-color: lightgray;")
        file_tree_view.setHeaderHidden(True)
        # 创建文件系统模型
        file_system_model = QFileSystemModel()
        file_system_model.setRootPath(QDir.rootPath())
        file_tree_view.setModel(file_system_model)
        # 隐藏文件类型和时间列
        file_tree_view.setColumnHidden(1, True)  # 文件类型列
        file_tree_view.setColumnHidden(2, True)  # 修改时间列
        file_tree_view.setColumnHidden(3, True)  # 修改时间列
        # 将子QListWidget添加到布局管理器中
        layout.addWidget(file_tree_view)

        # 创建布局管理器，右侧主窗口
        layout = QVBoxLayout()
        self.widgetMainFileExplorerRightMain.setLayout(layout)
        # 创建主体窗口B部件
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: white;")
        content_widget.setObjectName("content_widget")
        content_layout = QGridLayout(content_widget)
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)

        # 设置top与 bot 2个部分可以拖拽调整大小
        splitter_tabMainFileExplorer_top_bot = QSplitter()
        splitter_tabMainFileExplorer_top_bot.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_top_bot.setOrientation(0)  # 设置为垂直方向分割
        splitter_tabMainFileExplorer_top_bot.addWidget(self.widget_fileExplorer_top)
        splitter_tabMainFileExplorer_top_bot.addWidget(self.widget_fileExplorer_bot)
        layout_tabMainFileExplorer = QHBoxLayout(self.tabMainFileExplorer)
        layout_tabMainFileExplorer.addWidget(splitter_tabMainFileExplorer_top_bot)

        # 设置top里的多个部分可以拖拽调整大小
        splitter_tabMainFileExplorer_top = QSplitter()
        splitter_tabMainFileExplorer_top.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_top.addWidget(self.pushButtonMainFileExplorerBack)
        splitter_tabMainFileExplorer_top.addWidget(self.pushButtonMainFileExplorerForward)
        splitter_tabMainFileExplorer_top.addWidget(self.pushButtonMainFileExplorerUp)
        splitter_tabMainFileExplorer_top.addWidget(self.comboBoxMainFileExplorerPath)
        splitter_tabMainFileExplorer_top.addWidget(self.lineEditMainFileExplorerSearch)
        layout_tabMainFileExplorerTop = QHBoxLayout(self.widget_fileExplorer_top)
        layout_tabMainFileExplorerTop.addWidget(splitter_tabMainFileExplorer_top)

        # 设置底部的侧边栏与右边主窗口2个部分可以拖拽调整大小
        splitter_tabMainFileExplorer_bot = QSplitter()
        splitter_tabMainFileExplorer_bot.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_bot.addWidget(self.widgetMainFileExplorerSideBar)
        splitter_tabMainFileExplorer_bot.addWidget(self.widgetMainFileExplorerRightMain)
        # layout_tabMainFileExplorerBot = QHBoxLayout(self.widget_fileExplorer_bot)
        # layout_tabMainFileExplorerBot = QHBoxLayout(self.tabMainFileExplorer)
        layout_tabMainFileExplorerBot = QHBoxLayout(self.widget_fileExplorer_bot)
        layout_tabMainFileExplorerBot.addWidget(splitter_tabMainFileExplorer_bot)

        # 设置侧边栏上下2个部分可以拖拽调整大小
        splitter_tabMainFileExplorer_SideBar = QSplitter()
        splitter_tabMainFileExplorer_SideBar.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_SideBar.setOrientation(0)  # 设置为垂直方向分割
        splitter_tabMainFileExplorer_SideBar.addWidget(self.widgetLeftSiderTop)
        splitter_tabMainFileExplorer_SideBar.addWidget(self.widgetLeftSiderBot)
        layout_tabMainFileExplorerSideBar = QHBoxLayout(self.widgetMainFileExplorerSideBar)
        layout_tabMainFileExplorerSideBar.addWidget(splitter_tabMainFileExplorer_SideBar)
        # endregion




        # region 连接信号槽
        self.pushButtonMainFileExplorerBack.clicked.connect(self.go_to_back_history_folder)
        self.pushButtonMainFileExplorerForward.clicked.connect(self.go_forward)
        self.pushButtonMainFileExplorerUp.clicked.connect(self.go_up)
        folder_list.itemClicked.connect(self.common_folder_clicked)
        file_tree_view.clicked.connect(self.folder_selected)

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





    def common_folder_clicked(self, item):
        '''点击常用文件夹'''
        folder_name = item.text()
        if folder_name == "桌面":
            folder_path = QDir.homePath() + "/Desktop"
        elif folder_name == "下载":
            folder_path = QDir.homePath() + "/Downloads"
        elif folder_name == "文档":
            folder_path = QDir.homePath() + "/Documents"
        elif folder_name == "图片":
            folder_path = QDir.homePath() + "/Pictures"
        elif folder_name == "音乐":
            folder_path = QDir.homePath() + "/Music"
        elif folder_name == "视频":
            folder_path = QDir.homePath() + "/Videos"
        else:
            return

        self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
        self.current_folder = folder_path  # 更新当前文件夹路径
        self.update_folder_contents(folder_path)

    def go_to_back_history_folder(self):
        '''文件夹导航，后退'''
        print("后退:",self.back_history)
        if self.back_history:
            back_folder = self.back_history.pop()
            # self.forward_history.append(parent_folder)
            print('back_folder:',back_folder)
            self.update_folder_contents(back_folder)


    def go_forward(self):
        '''文件夹导航，前进'''
        print("前进",self.forward_history)
        if self.forward_history:
            forward_folder = self.forward_history.pop()
            forward_folder = self.forward_history.pop()
            self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
            self.current_folder = forward_folder  # 更新当前文件夹路径
            print('forward_folder:',forward_folder)
            self.update_folder_contents(forward_folder)


    def go_up(self):
        '''文件夹导航，向上'''
        up_folder = os.path.dirname(self.comboBoxMainFileExplorerPath.currentText())
        print("父目录:",up_folder)
        self.update_folder_contents(up_folder)


    def folder_selected(self, index):
        '''选中文件夹'''
        folder_model = index.model()
        if folder_model.isDir(index):
            self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
            # self.forward_history.append(self.current_folder)  # 将当前文件夹路径添加到forward记录中
            self.current_folder = folder_model.filePath(index)  # 更新当前文件夹路径
            self.update_folder_contents(self.current_folder)
        else:
            # 处理选择的是文件的情况
            file_path = folder_model.filePath(index)
            print("open file:", file_path)
            url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(url)


    def update_folder_contents(self, path):
        '''更新文件夹视图'''
        content_widget = self.findChild(QWidget, "content_widget")

        # 清空内容
        while content_widget.layout().count():
            child = content_widget.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 创建文件夹内容部件
        folder_contents_widget = QWidget()
        folder_contents_layout = QGridLayout(folder_contents_widget)
        folder_contents_layout.setContentsMargins(10, 10, 10, 10)
        folder_contents_layout.setSpacing(10)


        self.folder_list_view = ListViewFile(path)

        # 设置自定义委托来绘制文件名的自动换行
        delegate = FileNameDelegate(self.folder_list_view)
        self.folder_list_view.setItemDelegate(delegate)


        self.folder_list_view.doubleClicked.connect(self.folder_selected)

        # 将文件夹内容部件添加到布局中
        folder_contents_layout.addWidget(self.folder_list_view)


        #右击菜单
        # 创建上下文菜单
        self.context_menu = QMenu(self)
        self.open_action = QAction("打开", self)
        self.copy_action = QAction("复制", self)
        self.paste_action = QAction("粘贴", self)
        self.cut_action = QAction("剪切", self)
        self.delete_action = QAction("删除", self)
        self.rar_action = QAction("RAR", self)

        self.context_menu.addAction(self.open_action)
        self.context_menu.addAction(self.copy_action)
        self.context_menu.addAction(self.paste_action)
        self.context_menu.addAction(self.cut_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addAction(self.rar_action)




        # 设置上下文菜单策略
        self.folder_list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.folder_list_view.customContextMenuRequested.connect(self.show_context_menu)

        self.open_action.triggered.connect(self.folder_list_view.open_selected)
        self.copy_action.triggered.connect(self.folder_list_view.copy_selected)
        self.paste_action.triggered.connect(self.folder_list_view.paste_selected)
        self.cut_action.triggered.connect(self.folder_list_view.cut_selected)
        self.delete_action.triggered.connect(self.folder_list_view.delete_selected)
        self.rar_action.triggered.connect(self.folder_list_view.rar_selected)



        # 将文件夹内容部件设置为右边窗口B的子部件
        content_widget.layout().addWidget(folder_contents_widget)

        # 将当前文件夹路径添加到前进路径的历史记录
        self.forward_history.append(path)


        # 更新地址栏
        self.comboBoxMainFileExplorerPath.setCurrentText(path)

        self.folder_list_view.set_path(path)  # 更新path


    def show_context_menu(self, position):
        # 显示上下文菜单
        self.context_menu.exec_(self.folder_list_view.mapToGlobal(position))




    def navigate_to_url(self):
        url = self.address_bar.text()
        # 处理根据地址跳转的逻辑
        # ...



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
                self.labelStatusJobA.setText('状态：'+'转图完成' + '|' + message.split("|")[2])

                #转图按钮设置背景色为绿色
                self.pushButtonInputA.setStyleSheet('background-color: green')
                # self.pushButtonInputA.setStyleSheet('background-color: %s' % QColor(0, 255, 0).name())
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
        logger.info('self.currentMainTableFilesCount:'+str(self.currentMainTableFilesCount))
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
            logger.info("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            self.file_count = len(message)
            i=0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    logger.info("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))

    def importA(self):
        '''使用普通方法import'''
        logger.info("importA:")
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

        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text().lower() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)

            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
                self.tableWidgetVS.setCellWidget(each, 1,
                                                 self.buttonForRowLayerName(self.dialogImportA,message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            logger.info("说明已有一些文件信息在总表中了")
            #如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            self.file_count = len(message)
            i=0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    logger.info("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)
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

        layerName = layerName.lower()

        GUI.show_layer(jobDialogImport.jobName, jobDialogImport.step, layerName)

    def jobAReset(self):
        pass
        logger.info("释放jobA")

        # self.dialogInputA.deleteLater()
        # self.dialogInputA = None
        # self.tableWidgetVS.clear()
        # self.tableWidgetVS.setRowCount(0)

        # if hasattr(self, 'dialogInputA') or self.dialogInputA is not None:
        if hasattr(self, 'dialogInputA') and self.dialogInputA is not None:
            logger.info("Dialog exists!")
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
        logger.info("inputB")
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
                logger.info("料号转图完成message:"+str(message.split("|")[2]))
                self.labelStatusJobB.setText('状态：'+'转图完成' + '|' + message.split("|")[2])

                # 转图按钮设置背景色为绿色
                self.pushButtonInputB.setStyleSheet('background-color: green')
                # self.pushButtonInputA.setStyleSheet('background-color: %s' % QColor(0, 255, 0).name())
                logger.info("转图按钮设置背景色为绿色")
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
            logger.info("说明已有一些文件信息在总表中了")
            self.file_count = len(message)
            # 如果已有一些文件信息在总表中了，那么本次新增的列表要和原有的列表比较一下，做追加处理
            i = 0
            for each in range(self.file_count):
                if message[each] not in self.currentMainTableFilesList:
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)

                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))

    def importB(self):
        '''使用普通方法import'''
        logger.info("importB:")
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

        # 总表中存量文件名放到一个列表里
        self.currentMainTableFilesList = [self.tableWidgetVS.item(each, 0).text().lower() for each in range(self.currentMainTableFilesCount)]
        if self.currentMainTableFilesCount == 0:
            #本次要处理的文件数量
            self.file_count = len(message)

            self.tableWidgetVS.setRowCount(self.file_count)
            for each in range(self.file_count):
                pass
                self.tableWidgetVS.setItem(each, 0, QTableWidgetItem(message[each]))
                self.tableWidgetVS.setCellWidget(each, 3,
                                                 self.buttonForRowLayerName(self.dialogImportB,message[each]))
        if self.currentMainTableFilesCount > 0:
            pass
            logger.info("说明已有一些文件信息在总表中了")
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
                    logger.info("has new file")
                    i = i +1
                    self.tableWidgetVS.setRowCount(self.tableWidgetVS.rowCount() + 1)

                    self.tableWidgetVS.setItem(self.currentMainTableFilesCount -1 + i, 0, QTableWidgetItem(message[each]))
                    self.tableWidgetVS.setCellWidget(self.currentMainTableFilesCount -1 + i, 3,
                                                     self.buttonForRowLayerName(self.dialogImportB,message[each]))
        if len(message)>0:
            self.pushButtonImportB.setStyleSheet('background-color: green')
            self.FlagImportB = True

    def jobBReset(self):
        pass
        logger.info("释放jobB")
        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            logger.info('Dialog exists!')
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

        if message.split("|")[0] == "比图结果料号已导出！":
            QMessageBox.information(self, "完成", "比图已完成！")



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


        layerName = self.tableWidgetVS.item(int(id),0).text().lower()

        logger.info("看图！")
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

        logger.info("重置所有")
        if hasattr(self, 'dialogInputA') and self.dialogInputA is not None:
            logger.info('Dialog exists!')
            self.dialogInputA.deleteLater()
            self.dialogInputA = None
        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            logger.info('Dialog exists!')
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
        self.dialogSettings = DialogSettings()
        pass



        self.dialogSettings.show()


    def helpShow(self):
        pass
        if not hasattr(self, 'windowHelp') or self.windowHelp is None:
            logger.info("需要创建配置窗口")
            self.windowHelp = WindowHelp()
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            # self.dialogSettings.setWindowTitle('配置')
            # self.dialogInputA.triggerDialogInputStr.connect(self.update_text_start_input_A_get_str)  # 连接信号！

        self.windowHelp.show()


class ListViewFile(QListView):
    def __init__(self,path):
        super().__init__()
        self.path = path
        # 加载文件夹内容
        folder_model = QFileSystemModel()
        folder_model.setRootPath(path)
        self.setModel(folder_model)
        self.setRootIndex(folder_model.index(path))
        self.setIconSize(QSize(64, 64))
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(120, 120))  # 设置图标的固定宽度和高度
        self.setSpacing(20)  # 设置图标之间的间距

        # 添加快捷键
        self.create_shortcuts()

    def set_path(self,path):
        pass
        print("更新path",path)
        self.path = path


    #可以在按下鼠标时获取当前项目的信息，暂时用不到
    # def mousePressEvent(self, event):
    #     index = self.indexAt(event.pos())
    #     if index.isValid() and event.button() == Qt.LeftButton:
    #         self.filePath = index.data(Qt.DisplayRole)
    #         # print("选中的文件路径:", file_path)
    #     super().mousePressEvent(event)

    def open_selected(self):
        print("open:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pass
                url = QUrl.fromLocalFile(self.absolutePath)
                QDesktopServices.openUrl(url)

        if not selected_indexes:
            return


    def copy_selected(self):
        print("copy:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.absolutePath)

        if not selected_indexes:
            return


    def cut_selected(self):
        print("cut:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                gl.cutFlag = True
                # 将文件路径设置到剪贴板
                clipboard = qApp.clipboard()
                clipboard.setText(self.absolutePath, QClipboard.Clipboard)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('Files have been cut.')
                msg_box.exec_()

                print('gl.cutFlag', gl.cutFlag)

        if not selected_indexes:
            return


    def paste_selected(self):
        print('gl.cutFlag', gl.cutFlag)
        clipboard = QApplication.clipboard()
        self.absolutePath = clipboard.text(QClipboard.Clipboard)
        if self.absolutePath:
            # Perform paste operation with the file_path
            print('Pasting file:', self.absolutePath)


            if os.path.isfile(self.absolutePath):
                #如果是文件
                print('file,self.path for paste',self.path)

                if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                    #已存在同名文件
                    print("Destination file already exists.")
                    overwrite_type = QMessageBox.question(None, "确认", "目标文件已存在，要覆盖吗？",
                                                  QMessageBox.Yes | QMessageBox.No)
                    if overwrite_type != QMessageBox.Yes:
                        print("不覆盖")
                        return


                try:
                    if gl.cutFlag == True:

                        #剪切后粘贴
                        try:
                            # 使用shutil.move移动文件，如果目标文件存在，则覆盖
                            # shutil.move(self.absolutePath, self.path,copy_function=shutil.copy)
                            os.replace(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        except Exception as e:
                            print(f'Error while pasting file: {e}')

                    else:
                        # 复制后粘贴
                        shutil.copy(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        print("File copied successfully!")
                except IOError as e:
                    print(f"Unable to copy file. {e}")

            if os.path.isdir(self.absolutePath):
                #如果是文件夹
                print('folder,self.path for paste',self.path)

                if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                    #已存在同名文件
                    print("Destination folder already exists.")
                    overwrite_type = QMessageBox.question(None, "确认", "目标文件夹已存在，要覆盖吗？",
                                                  QMessageBox.Yes | QMessageBox.No)
                    if overwrite_type != QMessageBox.Yes:
                        print("不覆盖")#不覆盖时直接返回
                        return


                try:
                    if gl.cutFlag == True:

                        #剪切后粘贴
                        try:
                            # 删除已存在的目标文件夹
                            if os.path.exists(os.path.join(self.path, os.path.basename(self.absolutePath))):
                                shutil.rmtree(os.path.join(self.path, os.path.basename(self.absolutePath)))
                            # 使用shutil.move移动文件，如果目标文件存在，则覆盖
                            shutil.move(self.absolutePath, os.path.join(self.path, os.path.basename(self.absolutePath)),copy_function=shutil.copy)

                        except Exception as e:
                            print(f'粘贴文件夹时发生错误: {e}')

                    else:
                        # 删除已存在的目标文件夹
                        if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                            shutil.rmtree(os.path.join(self.path,os.path.basename(self.absolutePath)))
                        # 复制后粘贴
                        shutil.copytree(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        print("已成功复制文件夹!")
                except IOError as e:
                    print(f"未能复制文件夹. {e}")


        gl.cutFlag = False#重置


    def delete_selected(self):
        print("delete:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pathStandard = Path(self.absolutePath).resolve().as_posix()
                pathStandard = pathStandard.replace('/','\\')

                print('pathStandard:',pathStandard)
                # 将文件移动到回收站
                send2trash.send2trash(pathStandard)

                # # 下面方法是永久删除
                # if os.path.isfile(self.absolutePath):
                #     os.remove(self.absolutePath)
                # if os.path.isdir(self.absolutePath):
                #     shutil.rmtree(self.absolutePath)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('已删除！')
                msg_box.exec_()



        if not selected_indexes:
            return


    def rar_selected(self):
        print("rar:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pass
                print("rara do something")



                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('已完成！')
                msg_box.exec_()



        if not selected_indexes:
            return


    def copy_file(source_path, destination_path):
        if os.path.exists(destination_path):
            print("Destination file already exists.")
            overwrite = input("Do you want to overwrite the file? (y/n): ")
            if overwrite.lower() != 'y':
                print("File not copied.")
                return

        try:
            shutil.copy(source_path, destination_path)
            print("File copied successfully!")
        except IOError as e:
            print(f"Unable to copy file. {e}")




    def create_shortcuts(self):
        # # 创建快捷键
        # shortcut_open = QShortcut(QKeySequence(Qt.Key_Enter), self)  # 复制
        # # 绑定快捷键到槽函数
        # shortcut_open.activated.connect(self.open_selected)
        # 创建快捷键
        shortcut_copy = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self)  # 复制
        # 绑定快捷键到槽函数
        shortcut_copy.activated.connect(self.copy_selected)
        # 创建快捷键
        shortcut_paste = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self)  # 复制
        # 绑定快捷键到槽函数
        shortcut_paste.activated.connect(self.paste_selected)
        # 创建快捷键
        shortcut_cut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_cut.activated.connect(self.cut_selected)
        # 创建快捷键
        shortcut_delete = QShortcut(QKeySequence(Qt.Key_Delete), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_delete.activated.connect(self.delete_selected)

    # 在PyQt5中，如果您在QListView中按下回车键，通常不会自动触发任何操作。QShortcut类主要用于全局快捷键而不是特定于某个小部件的快捷键。
    # 如果您想要在按下回车键时触发操作，您可以使用QListView的keyPressEvent事件来捕获回车键并执行所需的操作。
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 在这里执行按下回车键后的操作
            print("Enter key pressed!")
            self.open_selected()
        else:
            super().keyPressEvent(event)



class FileNameDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # 获取文件名和图标
        file_model = index.data(Qt.DisplayRole)
        file_icon = index.data(Qt.DecorationRole)

        # 获取绘制区域和边距
        rect = option.rect
        margins = 4

        # 绘制背景
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())

        # 绘制图标
        icon_rect = QRect(rect.x(), rect.y(), rect.width(), rect.height() - 20)  # 调整图标区域的高度
        file_icon.paint(painter, icon_rect, Qt.AlignCenter, QIcon.Normal, QIcon.Off)

        # 绘制文件名，自动换行且居中对齐
        text_rect = QRect(rect.x(), rect.y() + icon_rect.height(), rect.width(), rect.height() - icon_rect.height())
        doc = QTextDocument()
        doc.setDefaultStyleSheet("p { margin: 0; text-align: center; }")
        doc.setHtml('<p>{}</p>'.format(file_model))
        doc.setTextWidth(text_rect.width())
        layout = doc.documentLayout()
        painter.translate(text_rect.topLeft())
        layout.draw(painter, QAbstractTextDocumentLayout.PaintContext())
        painter.restore()


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
























