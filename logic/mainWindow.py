import os
from PyQt5.QtCore import Qt, QDir,QUrl
from PyQt5.QtGui import QPalette, QColor, QIcon, QDesktopServices
from ui.mainWindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI, Input

from logic.help import WindowHelp
from logic.settings import DialogSettings
from logic.odbImport import DialogImport
from logic.compareG import MyThreadStartCompareG
from logic.input import DialogInput
from logic.fileListView import ListViewFile,FileNameDelegate
from logic.log import MyLog
import logic.gl as gl

logger = MyLog.log_init()


class MainWindow(QMainWindow,Ui_MainWindow):
    FlagInputA = False#料号A的Input状态为False表示还没有成功转图
    FlagInputB = False
    FlagImportA = False  # 料号A的Import状态为False表示还没有成功转图
    FlagImportB = False

    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.setGeometry(200, 30, 1200, 900)

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



        # region 是否已加载EPCAM
        if gl.FlagEPCAM == True:
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')
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


        # region 设置比图初始页面
        # 创建布局管理器，VS左侧主窗口上部的按钮区域
        layout_vs_left_top = QHBoxLayout()
        self.widget_vs_left_top.setLayout(layout_vs_left_top)
        layout_vs_left_top.addWidget(self.groupBoxJobA)
        layout_vs_left_top.addWidget(self.groupBoxVS)
        layout_vs_left_top.addWidget(self.groupBoxJobB)

        #设置QgroupBox中的部件布局,使得里面的部件大小可以随着窗口变化而自动调整
        # groupBoxJobA，创建一个网格布局
        layout_groupBoxJobA = QGridLayout(self.groupBoxJobA)
        layout_groupBoxJobA.addWidget(self.pushButtonInputA,0,0)
        layout_groupBoxJobA.addWidget(self.pushButtonImportA, 0, 1)
        layout_groupBoxJobA.addWidget(self.labelStatusJobA,1, 0)
        layout_groupBoxJobA.addWidget(self.pushButtonJobAReset, 1, 1)
        # 设置布局中各个部件的间距
        layout_groupBoxJobA.setSpacing(10)

        # groupBoxVS，创建一个网格布局
        layout_groupBoxVS = QGridLayout(self.groupBoxVS)
        layout_groupBoxVS.addWidget(self.pushButtonVS, 0, 0)
        layout_groupBoxVS.addWidget(self.comboBoxVSMethod, 1, 0)
        layout_groupBoxVS.addWidget(self.pushButtonAllReset, 2, 0)
        # 设置布局中各个部件的间距
        layout_groupBoxVS.setSpacing(10)

        # groupBoxJobB，创建一个网格布局
        layout_groupBoxJobB = QGridLayout(self.groupBoxJobB)
        layout_groupBoxJobB.addWidget(self.pushButtonInputB, 0, 0)
        layout_groupBoxJobB.addWidget(self.pushButtonImportB, 0, 1)
        layout_groupBoxJobB.addWidget(self.labelStatusJobB, 1, 0)
        layout_groupBoxJobB.addWidget(self.pushButtonJobBReset, 1, 1)
        # 设置布局中各个部件的间距
        layout_groupBoxJobB.setSpacing(10)


        # 设置左边上下2个部分可以拖拽调整大小
        splitter_tabMainVS_left = QSplitter()
        splitter_tabMainVS_left.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainVS_left.setOrientation(0)  # 设置为垂直方向分割
        # 设置分割条的比例
        # splitter_tabMainVS_left.setSizes([200, 600])
        # splitter_tabMainVS_left.setStretchFactor(0, 2)  # 设置第一个部件的比例为2
        # splitter_tabMainVS_left.setStretchFactor(1, 6)  # 设置第二个部件的比例为6
        splitter_tabMainVS_left.addWidget(self.widget_vs_left_top)
        splitter_tabMainVS_left.addWidget(self.widget_vs_left_bot)
        layout_tabMainVS_left = QHBoxLayout(self.widget_vs_left)
        layout_tabMainVS_left.addWidget(splitter_tabMainVS_left)


        # widget_vs_right_top，创建一个网格布局
        layout_widget_vs_right_top = QGridLayout(self.widget_vs_right_top)
        layout_widget_vs_right_top.addWidget(self.pushButtonLoadEPCAM, 0, 0)
        layout_widget_vs_right_top.addWidget(self.pushButtonSave, 0, 1)
        layout_widget_vs_right_top.addWidget(self.pushButtonSettings, 1, 1)
        layout_widget_vs_right_top.addWidget(self.pushButtonHelp, 2, 1)
        # 设置布局中各个部件的间距
        layout_widget_vs_right_top.setSpacing(10)


        # widget_vs_right_bot，创建一个布局
        layout_widget_vs_right_bot = QVBoxLayout(self.widget_vs_right_bot)
        layout_widget_vs_right_bot.addWidget(self.textBrowserMain)






        # 设置右边上下2个部分可以拖拽调整大小
        splitter_tabMainVS_right = QSplitter()
        splitter_tabMainVS_right.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainVS_right.setOrientation(0)  # 设置为垂直方向分割
        splitter_tabMainVS_right.addWidget(self.widget_vs_right_top)
        splitter_tabMainVS_right.addWidget(self.widget_vs_right_bot)
        layout_tabMainVS_right = QHBoxLayout(self.widget_vs_right)
        layout_tabMainVS_right.addWidget(splitter_tabMainVS_right)



        # 设置左边主窗口与右窗口2个部分可以拖拽调整大小
        splitter_tabMainVs = QSplitter()
        splitter_tabMainVs.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainVs.addWidget(self.widget_vs_left)
        splitter_tabMainVs.addWidget(self.widget_vs_right)
        layout_tabMainVs = QHBoxLayout(self.tabMainEPVS)
        layout_tabMainVs.addWidget(splitter_tabMainVs)

        # region 设置比对主表格
        layout_vs_left_bot = QHBoxLayout()
        self.widget_vs_left_bot.setLayout(layout_vs_left_bot)
        layout_vs_left_bot.addWidget(self.tableWidgetVS)
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
        self.pushButtonLoadEPCAM.clicked.connect(self.loadEPCAM)
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


    # def resizeEvent(self, event):
    #     # 在主窗口大小变化时调整表格部件的大小
    #     table_widget = self.findChild(QTableWidget)
    #     table_widget.setSizeAdjustPolicy(QTableWidget.AdjustToContents)


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

    def loadEPCAM(self):
        pass
        if gl.FlagEPCAM == False:
            from config_ep.epcam import EPCAM
            self.epcam = EPCAM()
            self.epcam.init()
            print("完成加载EPCAM!")
            gl.FlagEPCAM = True
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')
































