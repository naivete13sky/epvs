import json
import os
import shutil
import time
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QDir, QUrl, QRect
from PyQt5.QtGui import QPalette, QColor, QIcon, QDesktopServices
from ui.mainWindow import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI
from logic.help import WindowHelp
from logic.settings import DialogSettings
from logic.odbImport import DialogImport
from logic.compareG import MyThreadStartCompareG
from logic.input import DialogInput,DialogUploadTestJob
from logic.fileListView import ListViewFile,FileNameDelegate,ListViewFileForList
from logic.log import MyLog
import logic.gl as gl
from logic.QListWidgetCommonFolder import QListWidgetCommonFolder


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

        # region 为了使得tab widget随着主窗口大小变化跟着调整,需要设置一下layout。
        layout_main = QVBoxLayout()
        # 将Tab Widget放置在布局管理器中
        layout_main.addWidget(self.tabWidget)
        # layout_main.addWidget(self.tabWidget, alignment=Qt.AlignTop)

        # 创建一个容器窗口部件
        central_widget = QWidget()
        # 将布局管理器设置为容器窗口部件的布局
        central_widget.setLayout(layout_main)
        # 将容器窗口部件设置为主窗口的中央部件
        self.setCentralWidget(central_widget)
        # endregion



        # region 设置文件管理初始页面
        self.current_folder = ""  # 当前所选文件夹的路径
        self.back_history = []  # 文件夹路径的历史记录
        self.forward_history = []  # 前进路径的历史记录
        # 创建布局管理器，常用文件夹
        layout = QVBoxLayout()
        self.widgetLeftSiderTop.setLayout(layout)
        # 创建常用文件夹列表
        self.folder_list = QListWidgetCommonFolder()
        self.folder_list.triggerQListWidgetCommonFolderStr.connect(self.triggerQListWidgetCommonFolderStr_update)
        # 将子QListWidget添加到布局管理器中
        layout.addWidget(self.folder_list)


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
        # splitter_tabMainFileExplorer_top_bot.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_top_bot.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        # 设置手柄宽度为1个像素
        splitter_tabMainFileExplorer_top_bot.setHandleWidth(1)

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
        splitter_tabMainFileExplorer_top.setHandleWidth(1)

        # Qt设计师画的Qcombox没有回车事件，为了实现这个效果，需要自己写一个类来实现，这在个类中重写keyPressEvent方法
        self.comboBoxMainFileExplorerPath = CustomComboBox(self)
        self.comboBoxMainFileExplorerPath.triggerStr.connect(self.comboBoxMainFileExplorerPath_enter_do)  # 连接信号！
        self.comboBoxMainFileExplorerPath.setEditable(True)
        splitter_tabMainFileExplorer_top.addWidget(self.comboBoxMainFileExplorerPath)

        splitter_tabMainFileExplorer_top.addWidget(self.lineEditMainFileExplorerSearch)
        layout_tabMainFileExplorerTop = QHBoxLayout(self.widget_fileExplorer_top)
        layout_tabMainFileExplorerTop.addWidget(splitter_tabMainFileExplorer_top)
        splitter_tabMainFileExplorer_top.setSizes([20, 20,20,800,200])

        # 设置底部的侧边栏与右边主窗口2个部分可以拖拽调整大小
        splitter_tabMainFileExplorer_bot = QSplitter()
        splitter_tabMainFileExplorer_bot.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainFileExplorer_bot.addWidget(self.widgetMainFileExplorerSideBar)
        splitter_tabMainFileExplorer_bot.addWidget(self.widgetMainFileExplorerRightMain)
        splitter_tabMainFileExplorer_bot.setHandleWidth(1)
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
        splitter_tabMainFileExplorer_SideBar.setHandleWidth(1)
        layout_tabMainFileExplorerSideBar = QHBoxLayout(self.widgetMainFileExplorerSideBar)
        layout_tabMainFileExplorerSideBar.addWidget(splitter_tabMainFileExplorer_SideBar)

        # 设置搜索栏
        self.lineEditMainFileExplorerSearch.setPlaceholderText("搜索")

        # endregion


        # region 设置比图初始页面
        # 启动主界面时重置全局变量，清除历史信息
        gl.GerberFolderPath = None
        gl.DialogInput = None

        # region 设置料号A的状态信息，是label控件。设置料号B也一样。
        palette = QPalette()
        # 设置背景颜色为白色
        # palette.setColor(QPalette.Window, QColor(255, 255, 255))
        # 设置字体颜色
        palette.setColor(QPalette.WindowText, QColor(255, 0, 0))  # 白色是QColor(255, 255, 255)
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
        splitter_tabMainVS_left.setHandleWidth(1)
        layout_tabMainVS_left = QHBoxLayout(self.widget_vs_left)
        layout_tabMainVS_left.addWidget(splitter_tabMainVS_left)


        # widget_vs_right_top，创建一个网格布局
        layout_widget_vs_right_top = QGridLayout(self.widget_vs_right_top)
        layout_widget_vs_right_top.addWidget(self.pushButtonLoadEPCAM, 0, 0)
        layout_widget_vs_right_top.addWidget(self.pushButtonSaveDMS, 0, 1)
        if gl.login_user_type != 'dms':
            self.pushButtonSaveDMS.setDisabled(True)
        layout_widget_vs_right_top.addWidget(self.pushButtonSaveLocal, 1, 1)
        layout_widget_vs_right_top.addWidget(self.pushButtonSettings, 2, 1)
        layout_widget_vs_right_top.addWidget(self.pushButtonHelp, 3, 1)
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
        splitter_tabMainVS_right.setHandleWidth(1)
        layout_tabMainVS_right = QHBoxLayout(self.widget_vs_right)
        layout_tabMainVS_right.addWidget(splitter_tabMainVS_right)



        # 设置左边主窗口与右窗口2个部分可以拖拽调整大小
        splitter_tabMainVs = QSplitter()
        splitter_tabMainVs.setStyleSheet("QSplitter::handle { background-color: darkGray; }")
        splitter_tabMainVs.addWidget(self.widget_vs_left)
        splitter_tabMainVs.addWidget(self.widget_vs_right)
        splitter_tabMainVs.setHandleWidth(1)
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
        # 设置表格的水平表头
        header = self.tableWidgetVS.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        # 设置列宽的比例
        self.set_column_width_ratios([15, 15, 40, 15, 15])




        # endregion


        # endregion


        # region QtabWidget设置tab页名称横向
        tab_bar = self.tabWidget.tabBar()
        # 旋转文本
        for i in range(self.tabWidget.count()):
            tab_text = self.tabWidget.tabText(i)
            self.tabWidget.setTabText(i, '')  # 清空原有文本
            rotated_label = QLabel(tab_text, self.tabWidget)
            # rotated_label.setStyleSheet("transform: rotate(90deg);")
            tab_bar.setTabButton(i, QTabBar.LeftSide, rotated_label)
        # endregion


        # region 连接信号槽
        self.pushButtonMainFileExplorerBack.clicked.connect(self.go_to_back_history_folder)
        self.pushButtonMainFileExplorerForward.clicked.connect(self.go_forward)
        self.pushButtonMainFileExplorerUp.clicked.connect(self.go_up)
        self.folder_list.itemClicked.connect(self.common_folder_clicked)
        # self.folder_list
        file_tree_view.clicked.connect(self.folder_selected)
        self.comboBoxMainFileExplorerPath.activated.connect(self.on_comboBoxMainFileExplorerPath_activated)
        #我也不知道哪里的原因导致的returnPressed有异常：回车一次会响应两次。通过disconnect可以先断开。
        self.lineEditMainFileExplorerSearch.returnPressed.disconnect()
        self.lineEditMainFileExplorerSearch.returnPressed.connect(self.on_lineEditMainFileExplorerSearch_returnPressed)



        self.pushButtonInputA.clicked.connect(self.inputA)
        self.pushButtonImportA.clicked.connect(self.importA)
        self.pushButtonInputB.clicked.connect(self.inputB)
        self.pushButtonImportB.clicked.connect(self.importB)
        self.pushButtonVS.clicked.connect(self.vs)
        self.pushButtonAllReset.clicked.connect(self.allReset)
        self.pushButtonSettings.clicked.connect(self.settingsShow)
        self.pushButtonHelp.clicked.connect(self.helpShow)
        self.pushButtonLoadEPCAM.clicked.connect(self.loadEPCAM)
        self.pushButtonSaveDMS.clicked.connect(self.vs_result_to_dms)
        # endregion


    def common_folder_clicked(self, item):
        '''点击常用文件夹'''
        folder_name = item.text()

        # 设置自定义常用文件夹，从配置文件读取
        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.common_folder_dict = self.settings_dict['general']['common_folder']  # (json格式数据)字符串 转化 为字典



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
        elif len(self.common_folder_dict)>0:
            pass
            for k, v in self.common_folder_dict.items():
                # print(k,v)
                if folder_name == k:
                    # print("k:", k)
                    folder_path = v
        else:
            return





        self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
        self.current_folder = folder_path  # 更新当前文件夹路径
        self.update_folder_contents(folder_path)

    def go_to_back_history_folder(self):
        '''文件夹导航，后退'''

        if self.back_history:
            back_folder = self.back_history.pop()
            # self.forward_history.append(parent_folder)

            self.update_folder_contents(back_folder)

    def go_forward(self):
        '''文件夹导航，前进'''

        if self.forward_history:
            if len(self.forward_history)>0:
                forward_folder = self.forward_history.pop()
            if len(self.forward_history) > 0:
                forward_folder = self.forward_history.pop()
            self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
            self.current_folder = forward_folder  # 更新当前文件夹路径

            self.update_folder_contents(forward_folder)

    def go_up(self):
        '''文件夹导航，向上'''
        up_folder = os.path.dirname(self.comboBoxMainFileExplorerPath.currentText())
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
            url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(url)

    def search_result_selected(self, index):
        '''选中文件夹'''
        item = self.folder_list_view.model.itemFromIndex(index)
        path_str = item.text()
        if os.path.isdir(path_str):
            self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
            # self.forward_history.append(self.current_folder)  # 将当前文件夹路径添加到forward记录中
            self.current_folder = path_str  # 更新当前文件夹路径
            self.update_folder_contents(self.current_folder)
        else:
            # 处理选择的是文件的情况
            file_path = path_str

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
        self.folder_list_view.triggerListViewFileStr.connect(self.update_triggerListViewFileStr)
        self.folder_list_view.triggerListViewFileStrVsInputA.connect(self.update_triggerListViewFileStrVsInputA)
        self.folder_list_view.triggerListViewFileStrVsInputB.connect(self.update_triggerListViewFileStrVsInputB)
        self.folder_list_view.triggerListViewFileStrSwitchTab.connect(self.update_triggerListViewFileStrSwitchTab)

        # 将文件夹内容部件添加到布局中
        folder_contents_layout.addWidget(self.folder_list_view)

        # 将文件夹内容部件设置为右边窗口B的子部件
        content_widget.layout().addWidget(folder_contents_widget)

        # 将当前文件夹路径添加到前进路径的历史记录
        self.forward_history.append(path)

        # 更新地址栏
        # self.comboBoxMainFileExplorerPath.setCurrentText(path)

        self.folder_list_view.set_path(path)  # 更新path

        #更新历史记录到地址栏
        items_list = [each for each in self.back_history if len(each)>0]
        items_list = list(set(items_list))
        self.comboBoxMainFileExplorerPath.clear()
        self.comboBoxMainFileExplorerPath.addItems(items_list)
        # 更新地址栏
        self.comboBoxMainFileExplorerPath.setCurrentText(path)

    def show_context_menu(self, position):
        # 显示上下文菜单
        self.context_menu.exec_(self.folder_list_view.mapToGlobal(position))

    def navigate_to_url(self):
        url = self.address_bar.text()
        # 处理根据地址跳转的逻辑
        # ...

    def update_file_view_for_comboBoxMainFileExplorerPath(self):
        comboBoxMainFileExplorerPath = self.comboBoxMainFileExplorerPath.currentText()
        # self.back_history.append(self.current_folder)  # 将当前文件夹路径添加到历史记录中
        self.current_folder = comboBoxMainFileExplorerPath  # 更新当前文件夹路径
        self.update_folder_contents(self.current_folder)

    def comboBoxMainFileExplorerPath_enter_do(self):
        self.update_folder_contents(self.comboBoxMainFileExplorerPath.currentText())

    def on_comboBoxMainFileExplorerPath_activated(self):
        pass
        # print("c:")
        self.update_folder_contents(self.comboBoxMainFileExplorerPath.currentText())


    def on_lineEditMainFileExplorerSearch_returnPressed(self):
        pass
        keyword = self.lineEditMainFileExplorerSearch.text()
        if keyword:
            # print('keyword:',keyword)
            import glob
            search_path = self.comboBoxMainFileExplorerPath.currentText()
            # print("search_path,",search_path)
            file_paths = glob.glob(f'{search_path}**/*{keyword}*', recursive=True)

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

            self.folder_list_view = ListViewFileForList(file_paths)

            self.folder_list_view.doubleClicked.connect(self.search_result_selected)

            # 将文件夹内容部件添加到布局中
            folder_contents_layout.addWidget(self.folder_list_view)

            # 将文件夹内容部件设置为右边窗口B的子部件
            content_widget.layout().addWidget(folder_contents_widget)
        else:
            pass
            self.update_folder_contents(self.comboBoxMainFileExplorerPath.currentText())


    def update_triggerListViewFileStr(self,message):
        pass
        # print('message:',message)
        self.folder_list.addItem(message.split("|")[0])
        self.folder_list.repaint()

    def triggerQListWidgetCommonFolderStr_update(self,message):
        pass
        self.folder_list.takeItem(int(message))
        self.folder_list.repaint()


    def update_triggerListViewFileStrVsInputA(self,message):
        pass
        # print("message:",message)
        '''使用QThread'''
        if hasattr(self, 'dialogInputA') and self.dialogInputA is not None:
            logger.info("Dialog exists!")
            self.dialogInputA.deleteLater()
            self.dialogInputA = None


        if not hasattr(self, 'dialogInputA') or self.dialogInputA is None:
            self.dialogInputA = DialogInput("A",input_path=message)
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogInputA.setWindowTitle('料号A')
            self.dialogInputA.triggerDialogInputStr.connect(self.update_text_start_input_A_get_str)  # 连接信号！
            self.dialogInputA.triggerDialogInputList.connect(self.update_text_start_input_A_get_list)
        self.dialogInputA.show()
        self.dialogInputA.update_file_info_to_mainwindow()


    def update_triggerListViewFileStrVsInputB(self,message):
        pass
        # print("message:",message)
        '''使用QThread'''

        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            logger.info("Dialog exists!")
            self.dialogInputB.deleteLater()
            self.dialogInputB = None

        if not hasattr(self, 'dialogInputB') or self.dialogInputB is None:
            self.dialogInputB = DialogInput("B",input_path=message)
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogInputB.setWindowTitle('料号B')
            self.dialogInputB.triggerDialogInputStr.connect(self.update_text_start_input_B_get_str)  # 连接信号！
            self.dialogInputB.triggerDialogInputList.connect(self.update_text_start_input_B_get_list)
        self.dialogInputB.show()
        self.dialogInputB.update_file_info_to_mainwindow()


    def update_triggerListViewFileStrSwitchTab(self,message):
        pass
        if message == '切换到转图比对Tab':
            self.tabWidget.setCurrentWidget(self.tabMainEPVS)

    def resizeEvent(self, event):
        # 在主窗口大小变化时调整表格部件的大小
        # table_widget = self.findChild(QTableWidget)
        # table_widget.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        super().resizeEvent(event)
        self.set_column_width_ratios([15, 15, 40, 15, 15])

    def set_column_width_ratios(self, ratios):
        total_width = self.tableWidgetVS.viewport().width()
        header = self.tableWidgetVS.horizontalHeader()

        for i, ratio in enumerate(ratios):
            # 设置列为自动调整模式
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            # 设置列宽为比例乘以总宽度
            width = int(total_width * ratio / 100)
            header.resizeSection(i, width)

        # 最后一列设置为自动填充剩余空间
        header.setSectionResizeMode(len(ratios) - 1, QHeaderView.Stretch)

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
    def inputA(self,**kwargs):
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
        # print('cc:',message)
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

        if message.split("|")[0] == "已加载EPCAM":
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')


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
        if message.split("|")[0] == "已加载EPCAM":
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')


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
        #重置全局变量
        gl.GerberFolderPath = ''
        gl.DialogInput = None



    def inputB(self):
        logger.info("inputB")
        if not hasattr(self, 'dialogInputB') or self.dialogInputB is None:
            self.dialogInputB = DialogInput("B")
            # self.dialogInput.setModal(True)  # 设置对话框为模态
            self.dialogInputB.setWindowTitle('料号B')
            self.dialogInputB.comboBoxInputMethod.setCurrentText('方案2：G')
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
        if message.split("|")[0] == "已加载EPCAM":
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')

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
        if (self.FlagInputA or self.FlagImportA) and (self.FlagInputB or self.FlagImportB):
            #先清除历史比图结果
            # 清除第3列的内容
            for row in range(self.tableWidgetVS.rowCount()):
                self.tableWidgetVS.setCellWidget(row, 2, None)
            if self.comboBoxVSMethod.currentText()=='方案1：G比图':
                if gl.FlagComparingG == True:
                    pass
                    QMessageBox.information(self,"正在G比图！","正在G比图！请稍后再试！")
                else:
                    self.vsG()
        else:
            QMessageBox.information(self, "请先完成转图", "请先完成转图！")
            return


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
            self.dialogInputA.close_job()
            self.dialogInputA.deleteLater()
            self.dialogInputA = None
        if hasattr(self, 'dialogInputB') and self.dialogInputB is not None:
            logger.info('Dialog exists!')
            self.dialogInputB.close_job()
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

        #删除临时文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.temp_path = self.settings_dict['general']['temp_path']
        self.temp_path_g = self.settings_dict['g']['temp_path_g']
        self.gSetupType = self.settings_dict['g']['gSetupType']

        if self.gSetupType == 'local':
            if os.path.exists(self.temp_path):
                shutil.rmtree(self.temp_path)
        if self.gSetupType == 'vmware':
            if os.path.exists(self.temp_path):
                # 使用PsExec通过命令删除远程机器的文件
                from ccMethod.ccMethod import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path='ccMethod', computer='192.168.1.3', username='administrator', password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = self.temp_path_g
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)

        # 重置全局变量
        gl.GerberFolderPath = ''


        logger.info("remote delete finish")



    def settingsShow(self):
        self.dialogSettings = DialogSettings()
        self.dialogSettings.show()

    def helpShow(self):
        pass
        if not hasattr(self, 'windowHelp') or self.windowHelp is None:
            logger.info("需要创建配置窗口")
            self.windowHelp = WindowHelp()

        self.windowHelp.show()

    def loadEPCAM(self):
        pass
        if gl.FlagEPCAM == False:
            # 加载EPCAM进度条
            from logic.ProgressBarWindow import ProgressBarWindowLoadEPCAM
            self.progress_window = ProgressBarWindowLoadEPCAM()
            self.progress_window.show()

            # from config_ep.epcam import EPCAM
            # self.epcam = EPCAM()
            # self.epcam.init()
            # print("完成加载EPCAM!")
            # gl.FlagEPCAM = True
            self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # 绿色
            self.pushButtonLoadEPCAM.setStyleSheet('background-color: green')

    def vs_result_to_dms(self):
        print('vs_result_to_dms')
        vs_time_g = str(int(time.time()))  # 比对时间
        self.epvs_search_id = gl.login_username + '_' + vs_time_g
        print('epvs_search_id:',self.epvs_search_id)

        self.job_name=self.dialogInputA.jobName
        self.dialog_upload_test_job = DialogUploadTestJob(job_name=self.job_name)
        if self.dialog_upload_test_job.exec_() == QDialog.Accepted:

            self.job_parent = self.dialog_upload_test_job.lineEdit_job_parent.text()
            self.job_name = self.dialog_upload_test_job.lineEdit_job_name.text()
            self.file_type = self.dialog_upload_test_job.comboBox_file_type.currentText()
            self.test_usage_for_epcam_module = self.dialog_upload_test_job.lineEdit_test_usage_for_epcam_module.text()
            self.vs_result_ep = self.dialog_upload_test_job.comboBox_vs_result_ep.currentText()
            self.vs_result_g = self.dialog_upload_test_job.comboBox_vs_result_g.currentText()
            self.bug_info = self.dialog_upload_test_job.lineEdit_bug_info.text()

            self.bool_layer_info = 'false'
            if self.dialog_upload_test_job.radioButton_bool_layer_info_false.isChecked():
                self.bool_layer_info = 'false'
            if self.dialog_upload_test_job.radioButton_bool_layer_info_true.isChecked():
                self.bool_layer_info = 'true'

            self.vs_time_ep = self.dialog_upload_test_job.lineEdit_vs_time_ep.text()
            self.vs_time_g = self.dialog_upload_test_job.lineEdit_vs_time_g.text()

            self.status = 'draft'
            if self.dialog_upload_test_job.radioButton_status_draft.isChecked():
                self.status = 'draft'
            if self.dialog_upload_test_job.radioButton_status_published.isChecked():
                self.status = 'published'

            self.author = self.dialog_upload_test_job.lineEdit_author.text()

            self.tags = self.dialog_upload_test_job.lineEdit_tags.text()
            self.remark = self.dialog_upload_test_job.lineEdit_remark.text()


            # 压缩org为rar文件
            # 压缩到当前路径
            from ccMethod.ccMethod import CompressTool
            #在临时文件夹中把gerber文件夹名称改加原始名称，如去掉‘_a_ep’
            with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                self.settings_dict = json.load(cfg)
            self.temp_path = self.settings_dict['general']['temp_path']
            old_folder_name = os.path.join(self.temp_path,'gerber',self.dialogInputA.jobName)
            new_folder_name = os.path.join(self.temp_path,'gerber',os.path.basename(self.dialogInputA.lineEditGerberFolderPath.text()))
            try:
                os.rename(old_folder_name, new_folder_name)# 使用os.rename()函数修改文件夹名称
                # print(f"文件夹 {old_folder_name} 已成功修改为 {new_folder_name}")
            except OSError as e:
                print(f"修改文件夹名称失败: {e}")



            org_path = new_folder_name





            CompressTool.compress_with_winrar(org_path)
            self.file_path_org = org_path + '.rar'
            with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
                self.settings_dict = json.load(cfg)
            self.temp_path = self.settings_dict['general']['temp_path']
            if self.dialogInputA.comboBoxInputMethod.currentText() == '方案2：G':
                self.file_path_std = os.path.join(self.temp_path, 'odb',self.dialogInputA.lineEditJobName.text()) + '.tgz'
            if self.dialogInputB.comboBoxInputMethod.currentText() == '方案2：G':
                self.file_path_std = os.path.join(self.temp_path,'odb',self.dialogInputB.lineEditJobName.text()) + '.tgz'
            print('self.file_path_std:',self.file_path_std)

            if self.job_name and self.file_type and self.vs_result_ep and self.vs_result_g and self.status and self.tags and self.file_path_org and self.file_path_std:
                print("hihihi")

                from dms.dms import DMS
                dms = DMS()
                dms.login(gl.login_username, gl.login_password)


                dms.add_test_job(job_parent=self.job_parent,
                                 job_name=self.job_name,
                                 file_type=self.file_type,
                                 test_usage_for_epcam_module=self.test_usage_for_epcam_module,
                                 vs_result_ep=self.vs_result_ep,
                                 vs_result_g=self.vs_result_g,
                                 bug_info=self.bug_info,
                                 bool_layer_info=self.bool_layer_info,
                                 vs_time_ep=self.vs_time_ep,
                                 vs_time_g=self.vs_time_g,
                                 status=self.status,
                                 author=self.author,
                                 tags=self.tags,
                                 remark=self.remark,
                                 epvs_search_id=self.epvs_search_id,
                                 file_path_org=self.file_path_org,
                                 file_path_std=self.file_path_std)
                from ccMethod.ccMethod import GetInfoFromDMS
                sql = "SELECT a.* from eptest_job_for_test a where a.epvs_search_id = '{}'".format(self.epvs_search_id)
                # print('sql:',sql)
                pd_info = GetInfoFromDMS.exe_sql_return_pd(sql)
                # print(pd_info)
                self.test_job_id = str(pd_info.iloc[0]['id'])
                # print('self.test_job_id:',self.test_job_id)
                dms.get_layer_name_from_org(self.test_job_id)

                job_id = self.test_job_id
                print('job_id:',job_id)

                for row in range(self.dialogInputB.tableWidgetGerber.rowCount()):
                    if self.dialogInputB.tableWidgetGerber.item(row,1).text() in ['Excellon2']:
                        #更新孔参数
                        layer_name = self.dialogInputB.tableWidgetGerber.item(row,0).text()
                        print('layer_name:',layer_name)
                        sql = "SELECT a.* from eptest_layer a where a.job_id = '{}' and a.layer_ORG = '{}'".format(job_id,layer_name)
                        pd_info = GetInfoFromDMS.exe_sql_return_pd(sql)
                        test_layer_id = pd_info.iloc[0]['id']
                        print('test_layer_id:',test_layer_id)


                        job = job_id
                        layer = layer_name
                        layer_org = layer_name
                        vs_result_manual = 'none'
                        vs_result_ep = 'none'
                        vs_result_g = 'none'
                        layer_file_type = 'excellon2'
                        layer_type = 'drill'
                        features_count = 0
                        units = self.dialogInputB.tableWidgetGerber.item(row, 5).text()
                        coordinates = 'none'
                        zeroes_omitted = self.dialogInputB.tableWidgetGerber.item(row, 2).text()
                        number_format_A = self.dialogInputB.tableWidgetGerber.item(row, 3).text()
                        number_format_B = self.dialogInputB.tableWidgetGerber.item(row, 4).text()
                        # 悦谱转图tool_units_ep,先得知道是dialogInputA还是dialogInputB？
                        if self.dialogInputA.comboBoxInputMethod.currentText() == '方案1：悦谱':
                            tool_units_ep = self.dialogInputA.tableWidgetGerber.item(row, 6).text()
                        if self.dialogInputB.comboBoxInputMethod.currentText() == '方案1：悦谱':
                            tool_units_ep = self.dialogInputB.tableWidgetGerber.item(row, 6).text()

                        if self.dialogInputA.comboBoxInputMethod.currentText() == '方案2：G':
                            tool_units_g = self.dialogInputA.tableWidgetGerber.item(row, 6).text()
                        if self.dialogInputB.comboBoxInputMethod.currentText() == '方案2：G':
                            tool_units_g = self.dialogInputB.tableWidgetGerber.item(row, 6).text()
                        author = ''
                        status = 'published'
                        vs_time_ep = ''
                        vs_time_g = ''
                        remark = 'epvs_update'

                        dms.update_layer_para(test_layer_id=test_layer_id,
                                              job=job,
                                              layer=layer,
                                              layer_org=layer_org,
                                              vs_result_manual=vs_result_manual,
                                              vs_result_ep=vs_result_ep,
                                              vs_result_g=vs_result_g,
                                              layer_file_type=layer_file_type,
                                              layer_type=layer_type,
                                              features_count=features_count,
                                              units=units,
                                              coordinates=coordinates,
                                              zeroes_omitted=zeroes_omitted,
                                              number_format_A=number_format_A,
                                              number_format_B=number_format_B,
                                              tool_units_ep=tool_units_ep,
                                              tool_units_g=tool_units_g,
                                              author=author,
                                              status=status,
                                              vs_time_ep=vs_time_ep,
                                              vs_time_g=vs_time_g,
                                              remark=remark)
                QMessageBox.information(self, '比对结果上传DMS', '比对结果已上传至DMS！')


class CustomComboBox(QComboBox):
    triggerStr = QtCore.pyqtSignal(str)  # trigger传输的内容是字符串

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            text = self.currentText()  # 获取当前文本
            print("回车键按下，当前文本为:", text)
            # 在这里可以执行任何你想要的操作
            self.triggerStr.emit('enter')

        else:
            # print('cc2')
            super().keyPressEvent(event)
