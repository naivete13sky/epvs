import json
import os.path
import subprocess

from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QObject, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QLineEdit, QMessageBox, QTableWidgetItem, QPushButton, QWidget, \
    QLabel, QComboBox, QGridLayout, QVBoxLayout, QListWidget, QGroupBox, QSplitter, QListWidgetItem, QHBoxLayout, \
    QTextEdit

from ui.settings import Ui_Dialog as DialogSettings



from logic.log import MyLog
logger = MyLog.log_init()


class DialogSettings(QDialog,DialogSettings):
    triggerDialogSettings = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    def __init__(self):


        logger.info("init")
        super(DialogSettings,self).__init__()
        self.setupUi(self)
        self.setGeometry(200, 50, 1600, 950)
        self.tabWidgetSettings.setGeometry(10, 10, 1580, 930)

        # 初始化显示全局参数
        self.init_global_para()

        # 初始化显示通用设置
        self.init_common_para()

        # 配置DMS
        self.init_dms()


        #连接信号槽
        self.treeWidgetSettings.itemDoubleClicked.connect(self.editItem)
        self.pushButtonSaveSettingsAll.clicked.connect(self.settingsSave)
        self.pushButtonSaveSettingsCommon.clicked.connect(self.settingsSave)
        self.comboBoxSettingsGSetupType.currentIndexChanged.connect(self.gSetupTypeSelectionChanged)
        self.comboBoxSettingsGSetupPath.currentIndexChanged.connect(self.gSetupPathSelectionChanged)
        self.lineEditSettingsCommonGUserName.textChanged.connect(self.gUserNameChanged)

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

        # 转换为JSON对象并打印
        json_data = json.dumps(dict_data, indent=4)


        # 将JSON对象写入文件
        with open(r'settings/epvs.json', 'w',encoding='utf-8') as f:
            json.dump(dict_data, f,ensure_ascii=False,indent=4)
        QMessageBox.information(self, "完成", "操作已完成。")

    def settingsSave2(self):
        root = self.treeWidgetSettings.invisibleRootItem()
        result = [self.tree_to_dict(root.child(i)) for i in range(root.childCount())]
        json_data = json.dumps(result)

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


    def gSetupTypeSelectionChanged(self, index):
        item_name = 'gSetupType'
        found_item = None

        root_item = self.treeWidgetSettings.invisibleRootItem()
        found_item = self.find_item(root_item, item_name)

        if found_item is not None:
            logger.info("Found item:"+str(found_item.text(0)))
        else:
            logger.info("Item not found.")
        if self.sender().currentText() == 'vmware':
            logger.info("vmware")
            found_item.setText(1, 'vmware')

        if self.sender().currentText() == 'local':
            logger.info("local")
            found_item.setText(1, 'local')



    def find_item(self,item, name):
        if item.text(0) == name:
            return item
        for i in range(item.childCount()):
            child = item.child(i)
            found = self.find_item(child, name)
            if found is not None:
                return found
        return None

    def closeEvent(self, event):
        # # 清空对话框内容
        # self.treeWidgetSettings.clear()
        # event.accept()

        self.deleteLater()
        # self = None


    def gSetupPathSelectionChanged(self, index):
        item_name = 'GENESIS_DIR'
        found_item = None

        root_item = self.treeWidgetSettings.invisibleRootItem()
        found_item = self.find_item(root_item, item_name)

        if found_item is not None:
            logger.info("Found item:"+str(found_item.text(0)))
            found_item.setText(1, self.sender().currentText())
        else:
            logger.info("Item not found.")


    def gUserNameChanged(self):
        item_name = 'gUserName'
        found_item = None

        root_item = self.treeWidgetSettings.invisibleRootItem()
        found_item = self.find_item(root_item, item_name)

        if found_item is not None:
            logger.info("Found item:"+str(found_item.text(0)))
            found_item.setText(1, self.lineEditSettingsCommonGUserName.text())
        else:
            logger.info("Item not found.")


    def init_global_para(self):
        # 初始化显示全局参数
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settingsDict = json.load(cfg)  # (json格式数据)字符串 转化 为字典
        self.treeWidgetSettings.setColumnCount(2)
        # 设置表头
        self.treeWidgetSettings.setHeaderLabels(['项目', '值'])
        self.treeWidgetSettings.setColumnWidth(0, 300)
        # self.treeWidgetSettings.setColumnWidth(1, 100)
        self.addTreeItems(self.treeWidgetSettings, self.settingsDict)
        self.treeWidgetSettings.expandAll()


    def init_common_para(self):
        # 初始化显示通用设置
        root_item = self.treeWidgetSettings.invisibleRootItem()

        item_name = 'gSetupType'
        found_item = None
        found_item = self.find_item(root_item, item_name)
        if found_item is not None:
            logger.info("Found item:" + str(found_item.text(0)))
            self.comboBoxSettingsGSetupType.setCurrentText(found_item.text(1))
        else:
            logger.info("Item not found.")

        item_name = 'GENESIS_DIR'
        found_item = None
        found_item = self.find_item(root_item, item_name)
        if found_item is not None:
            logger.info("Found item:" + str(found_item.text(0)))
            self.comboBoxSettingsGSetupPath.setCurrentText(found_item.text(1))
        else:
            logger.info("Item not found.")

        item_name = 'gUserName'
        found_item = None
        found_item = self.find_item(root_item, item_name)
        if found_item is not None:
            self.lineEditSettingsCommonGUserName.setText(found_item.text(1))
        else:
            logger.info("Item not found.")


    def init_dms(self):
        pass
        # DMS部署tab页初始化
        self.communicateTabDMS = CommunicateTabDMS()
        # 连接自定义信号与槽函数
        self.communicateTabDMS.signal_str.connect(self.on_signal_str)

        title_font = QFont("微软雅黑", 12, QFont.Bold)  # 创建并设置微软雅黑字体，并加粗
        # 创建一个 QFont 对象并设置字体加粗
        font = QFont()
        font.setBold(True)

        # 创建一个QSplitter来划分子页面为左右两大部分。
        splitter_dms = QSplitter(self.tabDMSDeployment)
        self.tabDMSDeploymentLayout = QVBoxLayout(self.tabDMSDeployment)
        self.tabDMSDeploymentLayout.addWidget(splitter_dms)

        # 创建左侧区域
        splitter_dms_left = QSplitter()
        splitter_dms_left.setOrientation(0)
        splitter_dms.addWidget(splitter_dms_left)#把左侧的splitter_dms_left加入到splitter_dms（主splitter）

        # 创建多个QGroupBox并垂直划分左侧区域
        self.group_box_install_python = QGroupBox("安装Python")
        self.group_box_install_python.setFont(title_font)
        # 设置标题颜色为紫色
        self.group_box_install_python.setStyleSheet("QGroupBox { color: purple; }")
        self.group_box_install_python_layout = QGridLayout()
        self.group_box_install_python_layout.setColumnStretch(0, 1)  # 第1列宽度为1
        self.group_box_install_python_layout.setColumnStretch(1, 3)  # 第2列宽度为3
        self.group_box_install_python_layout.setColumnStretch(2, 1)  # 第3列宽度为1
        self.group_box_install_python_layout.setColumnStretch(3, 1)  # 第4列宽度为1
        self.group_box_install_python_layout.setColumnStretch(4, 1)  # 第5列宽度为1
        # 设置行的高度比例
        # self.group_box_install_python_layout.setRowStretch(0, 2)
        # self.group_box_install_python_layout.setRowMinimumHeight(1, 50)

        self.labelInstallPython = QLabel('安装Python解释器：', self)
        self.labelInstallPython.setFont(font)
        # layout_grid.addWidget(self.labelInstallPython, 0, 0, 1,1)  # 第一个参数是控件，后两个参数是行和列，最后两个参数是行跨度和列跨度
        self.group_box_install_python_layout.addWidget(self.labelInstallPython, 0, 0)  # 第一个参数是控件，后两个参数是行和列

        # 从安装包路径中设置
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:  # 读取配置文件
            self.settings_dict = json.load(cfg)
        self.software_path = self.settings_dict['dms']['software_path']  # json格式数据)字符串 转化 为字典
        self.python_installer_path = os.path.join(self.software_path, 'python')
        python_installer_list = os.listdir(self.python_installer_path)
        self.comboBox_Python = QComboBox(self)
        for each in python_installer_list:
            self.comboBox_Python.addItem(each)
        self.group_box_install_python_layout.addWidget(self.comboBox_Python, 0, 1)

        self.labelInstallPythonRemark = QLabel('请选择Python3.10.2版本', self)
        self.labelInstallPythonRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelInstallPythonRemark.setFont(font)  # 应用加粗字体
        self.group_box_install_python_layout.addWidget(self.labelInstallPythonRemark, 0, 2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonInstallPython = QPushButton('安装Python')
        button_font = QFont("微软雅黑", 10, QFont.Bold)  # 创建并设置微软雅黑字体，并加粗
        self.buttonInstallPython.setFont(button_font)
        self.group_box_install_python_layout.addWidget(self.buttonInstallPython, 0, 3)

        self.labelSetPip = QLabel('设置pip安装源：')
        self.labelSetPip.setFont(font)
        self.group_box_install_python_layout.addWidget(self.labelSetPip, 1, 0)
        self.user_folder = os.path.expanduser("~")
        self.labelUserPath = QLabel(f'复制pip到当前用户路径{self.user_folder}下')
        self.group_box_install_python_layout.addWidget(self.labelUserPath, 1, 1)
        self.labelSetPipRemark = QLabel('非必须操作，设置了可加快在线下载包速度', self)
        self.labelSetPipRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelSetPipRemark.setFont(font)  # 应用加粗字体
        self.group_box_install_python_layout.addWidget(self.labelSetPipRemark, 1, 2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonSetPip = QPushButton('复制pip')
        self.buttonSetPip.setFont(button_font)
        self.group_box_install_python_layout.addWidget(self.buttonSetPip, 1, 3)

        self.labelInstallVirtualTools = QLabel('安装虚拟环境工具：')
        self.labelInstallVirtualTools.setFont(font)
        self.group_box_install_python_layout.addWidget(self.labelInstallVirtualTools, 2, 0)
        # 创建一个 QListWidget
        self.listWidgetVirtualToolsPackage = QListWidget()
        self.listWidgetVirtualToolsPackage.setMaximumHeight(80)  # 设置最大高度为200像素，根据需要调整高度
        self.listWidgetVirtualToolsPackage.setMinimumHeight(80)  # 设置最小高度为200像素，根据需要调整高度
        python_virtual_tools_installer_list = []
        self.python_virtual_tools_path = os.path.join(self.software_path, 'python_virtual_tools')
        with open(os.path.join(self.python_virtual_tools_path, 'requirements.txt'), 'r',
                  encoding='utf-8') as file:  # 读取配置文件
            for line in file:
                # print(line.strip())  # 使用strip()方法去除行末尾的换行符
                python_virtual_tools_installer_list.append(line)
        for each in python_virtual_tools_installer_list:
            item = QListWidgetItem(each)
            custom_height = 20  # 设置自定义的高度
            item.setSizeHint(QSize(item.sizeHint().width(), custom_height))  # 设置项目的高度
            self.listWidgetVirtualToolsPackage.addItem(item)
            # self.listWidgetVirtualToolsPackage.addItem(each)
        # 创建一个 QWidget 用于放置 QListWidget
        self.widgetVirtualToolsPackage = QWidget()
        self.group_box_install_python_layout.addWidget(self.listWidgetVirtualToolsPackage, 2, 1)
        self.labelInstallVirtualToolsRemark = QLabel('安装工具是为了创建虚拟环境')
        self.labelInstallVirtualToolsRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelInstallVirtualToolsRemark.setFont(font)  # 应用加粗字体
        self.group_box_install_python_layout.addWidget(self.labelInstallVirtualToolsRemark, 2, 2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonInstallVirtualTools = QPushButton('安装虚拟环境管理工具')
        self.buttonInstallVirtualTools.setFont(button_font)
        self.group_box_install_python_layout.addWidget(self.buttonInstallVirtualTools, 2, 3)

        # 创建epdms虚拟环境
        self.labelCreateVirualenv_epdms = QLabel('创建epdms虚拟环境：')
        self.labelCreateVirualenv_epdms.setFont(font)
        self.group_box_install_python_layout.addWidget(self.labelCreateVirualenv_epdms, 3, 0)
        self.lineEdit_dms_create_epdms = QLineEdit()
        self.lineEdit_dms_create_epdms.setText("mkvirtualenv -p python3.10.2 epdms")
        self.lineEdit_dms_create_epdms.setFixedHeight(30)  # 设置 QLineEdit 控件的高度为40
        self.group_box_install_python_layout.addWidget(self.lineEdit_dms_create_epdms, 3, 1)
        self.labelCreateVirualenv_epdmsRemark = QLabel('创建epdms虚拟环境')
        self.labelCreateVirualenv_epdmsRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelCreateVirualenv_epdmsRemark.setFont(font)  # 应用加粗字体
        self.group_box_install_python_layout.addWidget(self.labelCreateVirualenv_epdmsRemark, 3,
                                                       2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonCreateVirualenv_epdms = QPushButton('创建虚拟环境epdms')
        self.buttonCreateVirualenv_epdms.setFont(button_font)
        self.group_box_install_python_layout.addWidget(self.buttonCreateVirualenv_epdms, 3, 3)

        self.buttonInstallPythonCheck = QPushButton('检查')
        self.buttonInstallPythonCheck.setFont(button_font)
        self.group_box_install_python_layout.addWidget(self.buttonInstallPythonCheck, 3, 4)

        self.group_box_install_python.setLayout(self.group_box_install_python_layout)  # layout


        # 创建QGroupBox并将其添加到垂直布局中
        self.group_box_set_epdms = QGroupBox("配置DMS环境")
        self.group_box_set_epdms.setFont(title_font)
        # 设置标题颜色为紫色
        self.group_box_set_epdms.setStyleSheet("QGroupBox { color: purple; }")
        # self.layout_dms_left.addWidget(self.group_box_set_epdms)
        self.group_box_set_epdms_layout = QGridLayout()
        self.group_box_set_epdms_layout.setColumnStretch(0, 1)  # 第1列宽度为1
        self.group_box_set_epdms_layout.setColumnStretch(1, 3)  # 第2列宽度为3
        self.group_box_set_epdms_layout.setColumnStretch(2, 1)  # 第3列宽度为1
        self.group_box_set_epdms_layout.setColumnStretch(3, 1)  # 第4列宽度为1
        self.group_box_set_epdms_layout.setColumnStretch(4, 1)  # 第5列宽度为1
        self.labelInstallPostgreSQL = QLabel('安装PostgreSQL数据库：')
        self.labelInstallPostgreSQL.setFont(font)
        self.group_box_set_epdms_layout.addWidget(self.labelInstallPostgreSQL, 0, 0)  # 第一个参数是控件，后两个参数是行和列
        # 从安装包路径中设置
        self.PostgreSQL_installer_path = os.path.join(self.software_path, 'PostgreSQL')
        PostgreSQL_installer_list = os.listdir(self.PostgreSQL_installer_path)
        self.comboBox_PostgreSQL = QComboBox(self)
        for each in PostgreSQL_installer_list:
            self.comboBox_PostgreSQL.addItem(each)
        self.group_box_set_epdms_layout.addWidget(self.comboBox_PostgreSQL, 0, 1)

        self.labelInstallPostgreSQLRemark = QLabel('请选择13.7-1-windows-x64版本，密码设置为cc，不安装stack builder', self)
        self.labelInstallPostgreSQLRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelInstallPostgreSQLRemark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.labelInstallPostgreSQLRemark, 0, 2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonInstallPostgreSQL = QPushButton('安装PostgreSQL')
        self.buttonInstallPostgreSQL.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.buttonInstallPostgreSQL, 0, 3)

        self.labelCreateDB_epdms = QLabel('创建数据库：')
        self.labelCreateDB_epdms.setFont(font)
        self.group_box_set_epdms_layout.addWidget(self.labelCreateDB_epdms, 1, 0)  # 第一个参数是控件，后两个参数是行和列
        self.lineEdit_dms_create_db_epdms = QLineEdit()
        self.db_name = self.settings_dict['dms']['db_name']  # json格式数据)字符串 转化 为字典
        self.lineEdit_dms_create_db_epdms.setText(self.db_name)
        self.lineEdit_dms_create_db_epdms.setFixedHeight(30)  # 设置 QLineEdit 控件的高度为40
        self.group_box_set_epdms_layout.addWidget(self.lineEdit_dms_create_db_epdms, 1, 1)
        self.labelCreateDB_epdmsRemark = QLabel(f'创建数据库，默认名为{self.db_name}')
        self.labelCreateDB_epdmsRemark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.labelCreateDB_epdmsRemark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.labelCreateDB_epdmsRemark, 1,
                                                       2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonCreateDB_epdms = QPushButton('创建数据库epdms')
        self.buttonCreateDB_epdms.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.buttonCreateDB_epdms, 1, 3)

        self.label_dms_set_db = QLabel('修改数据库配置：')
        self.label_dms_set_db.setFont(font)
        self.group_box_set_epdms_layout.addWidget(self.label_dms_set_db, 2, 0)  # 第一个参数是控件，后两个参数是行和列
        self.lineEdit_dms_set_db = QLineEdit()
        import socket
        host_name = socket.gethostname() # 获取计算机的主机名
        ethernet_ip = socket.gethostbyname(host_name) # 通过主机名获取以太网IP地址
        print(f"以太网IP地址: {ethernet_ip}")
        self.lineEdit_dms_set_db.setText(ethernet_ip)
        self.lineEdit_dms_set_db.setFixedHeight(30)  # 设置 QLineEdit 控件的高度为40
        self.group_box_set_epdms_layout.addWidget(self.lineEdit_dms_set_db, 2, 1)
        self.label_dms_set_db_remark = QLabel('修改数据库配置，支持远程访问数据库')
        self.label_dms_set_db_remark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.label_dms_set_db_remark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.label_dms_set_db_remark, 2,
                                                  2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonDMSSetDB = QPushButton('修改数据库配置')
        self.buttonDMSSetDB.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.buttonDMSSetDB, 2, 3)

        self.label_dms_install_dms_packages = QLabel('装DMS用的Python包：')
        self.label_dms_install_dms_packages.setFont(font)
        self.group_box_set_epdms_layout.addWidget(self.label_dms_install_dms_packages, 3, 0)  # 第一个参数是控件，后两个参数是行和列
        self.listWidget_dms_packages = QListWidget()
        self.listWidget_dms_packages.setMaximumHeight(80)  # 设置最大高度为200像素，根据需要调整高度
        self.listWidget_dms_packages.setMinimumHeight(80)  # 设置最小高度为200像素，根据需要调整高度
        dms_packages_list = []
        self.dms_packages_path = os.path.join(self.software_path, 'python_dms_packages')
        with open(os.path.join(self.dms_packages_path, 'requirements.txt'), 'r',
                  encoding='utf-8') as file:  # 读取配置文件
            for line in file:
                # print(line.strip())  # 使用strip()方法去除行末尾的换行符
                dms_packages_list.append(line)
        for each in dms_packages_list:
            item = QListWidgetItem(each)
            custom_height = 20  # 设置自定义的高度
            item.setSizeHint(QSize(item.sizeHint().width(), custom_height))  # 设置项目的高度
            self.listWidget_dms_packages.addItem(item)
        self.group_box_set_epdms_layout.addWidget(self.listWidget_dms_packages, 3, 1)
        self.label_dms_packages_remark = QLabel('装DMS用的Python包')
        self.label_dms_packages_remark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.label_dms_packages_remark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.label_dms_packages_remark, 3,
                                                  2)  # 第一个参数是控件，后两个参数是行和列
        self.buttonDMSInstallPackages = QPushButton('装DMS用的Python包')
        self.buttonDMSInstallPackages.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.buttonDMSInstallPackages, 3, 3)

        self.label_dms_deploy_epdms = QLabel('部署DMS代码：')
        self.label_dms_deploy_epdms.setFont(font)
        self.group_box_set_epdms_layout.addWidget(self.label_dms_deploy_epdms, 4, 0)  # 第一个参数是控件，后两个参数是行和列
        self.lineEdit_dms_deploy_epdms = QLineEdit()
        self.dms_path = self.settings_dict['dms']['dms_path']  # json格式数据)字符串 转化 为字典
        self.epdms_path = os.path.join(self.dms_path,'epdms')
        self.lineEdit_dms_deploy_epdms.setText(self.dms_path)
        self.lineEdit_dms_deploy_epdms.setFixedHeight(30)  # 设置 QLineEdit 控件的高度为40
        self.group_box_set_epdms_layout.addWidget(self.lineEdit_dms_deploy_epdms, 4, 1)
        self.label_dms_deploy_epdms_remark = QLabel(f'默认部署在{self.dms_path}路径下')
        self.label_dms_deploy_epdms_remark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.label_dms_deploy_epdms_remark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.label_dms_deploy_epdms_remark, 4,
                                                  2)  # 第一个参数是控件，后两个参数是行和列
        self.button_dms_deploy_epdms = QPushButton('解压DMS代码')
        self.button_dms_deploy_epdms.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.button_dms_deploy_epdms, 4, 3)
        self.textEdit_dms_init_db_table = QTextEdit()
        init_db_table_commands_list = [
            '',
            ''
        ]

        self.group_box_set_epdms_layout.addWidget(self.textEdit_dms_init_db_table, 5, 1)
        self.label_dms_deploy_epdms_init_db_table_remark = QLabel(f'初始化数据库表')
        self.label_dms_deploy_epdms_init_db_table_remark.setStyleSheet("color: red;")  # 设置标签文本颜色为红色
        self.label_dms_deploy_epdms_init_db_table_remark.setFont(font)  # 应用加粗字体
        self.group_box_set_epdms_layout.addWidget(self.label_dms_deploy_epdms_init_db_table_remark, 5,
                                                  2)  # 第一个参数是控件，后两个参数是行和列
        self.button_dms_deploy_epdms_init_db_table = QPushButton('初始化数据库表')
        self.button_dms_deploy_epdms_init_db_table.setFont(button_font)
        self.group_box_set_epdms_layout.addWidget(self.button_dms_deploy_epdms_init_db_table, 5, 3)


        self.group_box_set_epdms.setLayout(self.group_box_set_epdms_layout)  # layout


        # 创建QGroupBox并将其添加到垂直布局中
        self.group_box_set_apache = QGroupBox("部署DMS到Apache")
        self.group_box_set_apache.setFont(title_font)
        # 设置标题颜色为紫色
        self.group_box_set_apache.setStyleSheet("QGroupBox { color: purple; }")
        # self.layout_dms_left.addWidget(self.group_box_set_apache)

        # 创建QGroupBox并将其添加到垂直布局中
        self.group_box_set_pytest = QGroupBox("部署Pytest框架")
        self.group_box_set_pytest.setFont(title_font)
        # 设置标题颜色为紫色
        self.group_box_set_pytest.setStyleSheet("QGroupBox { color: purple; }")
        # self.layout_dms_left.addWidget(self.group_box_set_pytest)

        splitter_dms_left.addWidget(self.group_box_install_python)
        splitter_dms_left.addWidget(self.group_box_set_epdms)
        splitter_dms_left.addWidget(self.group_box_set_apache)
        splitter_dms_left.addWidget(self.group_box_set_pytest)

        # 创建右侧区域并添加多行文本框
        rightWidget = QWidget()
        splitter_dms.addWidget(rightWidget)

        # 设置左右比例
        splitter_dms.setSizes([900, 300])

        self.textEdit = QTextEdit()
        rightLayout = QVBoxLayout(rightWidget)
        rightLayout.addWidget(self.textEdit)


        # 信号槽连接
        self.buttonInstallPython.clicked.connect(self.on_buttonInstallPythonClicked)
        self.buttonSetPip.clicked.connect(self.on_buttonSetPipClicked)
        self.buttonInstallVirtualTools.clicked.connect(self.on_buttonInstallVirtualToolsClicked)
        self.buttonInstallPythonCheck.clicked.connect(self.on_buttonInstallPythonCheckClicked)
        self.buttonCreateVirualenv_epdms.clicked.connect(self.on_buttonCreateVirualenv_epdmsClicked)

        self.buttonInstallPostgreSQL.clicked.connect(self.on_buttonInstallPostgreSQLClicked)
        self.buttonCreateDB_epdms.clicked.connect(self.on_buttonCreateDB_epdmsClicked)
        self.buttonDMSSetDB.clicked.connect(self.on_buttonDMSSetDBClicked)
        self.buttonDMSInstallPackages.clicked.connect(self.on_buttonDMSInstallPackagesClicked)
        self.button_dms_deploy_epdms.clicked.connect(self.on_button_dms_deploy_epdms_clicked)
        self.button_dms_deploy_epdms_init_db_table.clicked.connect(self.on_button_dms_deploy_epdms_init_db_table_clicked)



    def on_buttonInstallPythonClicked(self):
        self.communicateTabDMS.signal_str.emit('安装python')
        import subprocess
        # 安装包的路径
        # install_package_path = r"D:\cc\software\ep\epvs\python\python-3.10.2-amd64.exe"
        install_package_path = os.path.join(self.python_installer_path,self.comboBox_Python.currentText())
        try:
            subprocess.Popen(install_package_path)   # 使用 subprocess.Popen 启动安装包
            self.communicateTabDMS.signal_str.emit('安装包已启动')
        except Exception as e:
            # print(f"启动安装包时出错：{str(e)}")
            self.communicateTabDMS.signal_str.emit(f"启动安装包时出错：{str(e)}")

    def on_buttonSetPipClicked(self):
        pass
        import shutil
        source_folder = os.path.join(self.software_path,'pip')  # 源文件夹的路径
        target_folder = os.path.join(self.user_folder,'pip')  # 目标文件夹的路径
        if not os.path.exists(target_folder):
            shutil.copytree(source_folder, target_folder)
            self.communicateTabDMS.signal_str.emit('已完成复制pip文件夹！')
            QMessageBox.information(self,'提醒！','已完成复制！')
        else:
            self.communicateTabDMS.signal_str.emit('已存在pip文件夹，无法复制！')
            QMessageBox.information(self,'提醒！','已存在pip文件夹！')

    def on_buttonInstallVirtualToolsClicked(self):
        self.communicateTabDMS.signal_str.emit('安装虚拟环境！')
        disk_name = self.python_virtual_tools_path[0]

        import subprocess

        # 先看一下当前python解释器版本，如果不是Python3.10.2就不能安装包的
        # 创建一个子进程
        process_main_python_version = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands_main_python_version = [
            'deactivate',#先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'python --version',
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]
        result_list = []
        # 执行所有命令
        for command in commands_main_python_version:
            process_main_python_version.stdin.write(command + "\n")
            process_main_python_version.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process_main_python_version.stdout.readline()
            if process_main_python_version.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                result_list.append(output_line.strip())

        os_default_python_version = result_list[-3]
        self.communicateTabDMS.signal_str.emit(f'操作系统默认Python版本：{os_default_python_version}')

        # 关闭子进程的标准输入、输出和错误流
        process_main_python_version.stdin.close()
        process_main_python_version.stdout.close()
        process_main_python_version.stderr.close()
        # 等待子进程完成
        process_main_python_version.wait()

        if '3.10.2' not in os_default_python_version:
            QMessageBox.information(self,'警告！','操作系统默认python解释器版本不是3.10.2，请人工处理！')
            return


        # 创建一个子进程
        process = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )





        # 命令列表
        commands = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            f'{disk_name}:',
            f'cd {self.python_virtual_tools_path}',
            'pip install --no-index --find-links=./your_offline_packages/ -r requirements.txt',
            "pip list",
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]

        # 执行所有命令
        for command in commands:
            process.stdin.write(command + "\n")
            process.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process.stdout.readline()
            if process.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                self.communicateTabDMS.signal_str.emit(f'{output_line.strip()}')

        # 关闭子进程的标准输入、输出和错误流
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()

        # 等待子进程完成
        process.wait()
        self.communicateTabDMS.signal_str.emit('已完成安装！')
        QMessageBox.information(self,'提醒！','已完成安装！')

    def on_buttonInstallPythonCheckClicked(self):
        self.communicateTabDMS.signal_str.emit(f'Python环境检查：')
        import subprocess
        # 创建一个子进程
        process = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands = [
            "workon epdms",  # 用实际的命令替换"command1"
            "python --version",  # 用实际的命令替换"command2"
            "ipconfig"  # 用实际的命令替换"command3"
        ]
        # 执行第一个命令
        process.stdin.write(commands[0] + "\n")
        process.stdin.flush()
        ret1 = process.stdout.readline()  # Microsoft Windows [版本 10.0.22621.2134]
        ret2 = process.stdout.readline()  # (c) Microsoft Corporation。保留所有权利。
        ret3 = process.stdout.readline()  # (c)
        ret4 = process.stdout.readline()  # 例如(epvs) D:\cc\python\epwork\epvs>workon epcam_ui_test

        # 执行第2个命令
        process.stdin.write(commands[1] + "\n")
        process.stdin.flush()
        ret5 = process.stdout.readline()  # (epcam_ui_test) D:\cc\python\epwork\epvs>python --version
        ret6 = process.stdout.readline()  # 如Python 3.11.4
        # 关闭子进程的标准输入、输出和错误流
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        # 等待子进程完成
        process.wait()

        # 检查结果标记颜色
        # print('ret6:',ret6,type(ret6),len(ret6))
        if ret6 == 'Python 3.10.2\n':
            # print("passed", ret6)
            self.communicateTabDMS.signal_str.emit(f'passed：{ret6}')
            self.buttonInstallPythonCheck.setStyleSheet("background-color: green; color: white;")
        else:
            # print('failed', ret6)
            self.communicateTabDMS.signal_str.emit(f'failed：{ret6}')
            self.buttonInstallPythonCheck.setStyleSheet("background-color: red; color: white;")

    def on_buttonCreateVirualenv_epdmsClicked(self):
        pass
        print('创建虚拟环境epdms')
        self.communicateTabDMS.signal_str.emit(f'创建虚拟环境epdms')
        disk_name = self.python_virtual_tools_path[0]

        import subprocess

        # 先看一下当前python解释器版本，如果不是Python3.10.2就不能创建虚拟环境
        # 创建一个子进程
        process_main_python_version = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands_main_python_version = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'python --version',
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]
        result_list = []
        # 执行所有命令
        for command in commands_main_python_version:
            process_main_python_version.stdin.write(command + "\n")
            process_main_python_version.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process_main_python_version.stdout.readline()
            if process_main_python_version.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                result_list.append(output_line.strip())

        os_default_python_version = result_list[-3]
        # print('操作系统默认Python版本：', os_default_python_version)
        self.communicateTabDMS.signal_str.emit(f'操作系统默认Python版本：{os_default_python_version}')

        # 关闭子进程的标准输入、输出和错误流
        process_main_python_version.stdin.close()
        process_main_python_version.stdout.close()
        process_main_python_version.stderr.close()
        # 等待子进程完成
        process_main_python_version.wait()

        if '3.10.2' not in os_default_python_version:
            QMessageBox.information(self, '警告！', '操作系统默认python解释器版本不是3.10.2，请人工处理！')
            return

        # 创建一个子进程
        process = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            f'{disk_name}:',
            f'cd {self.python_virtual_tools_path}',
            f'{self.lineEdit_dms_create_epdms.text()}',
            "pip list",
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]

        # 执行所有命令
        for command in commands:
            process.stdin.write(command + "\n")
            process.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process.stdout.readline()
            if process.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                self.communicateTabDMS.signal_str.emit(f'{output_line.strip()}')

        # 关闭子进程的标准输入、输出和错误流
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()

        # 等待子进程完成
        process.wait()
        self.communicateTabDMS.signal_str.emit(f'已完成创建epdms虚拟环境！')
        QMessageBox.information(self, '提醒！', '已完成创建epdms虚拟环境！')

    def on_signal_str(self,message):
        pass
        # 当信号被发射时，将信息写入文本编辑框
        self.textEdit.append(message)

    def on_buttonInstallPostgreSQLClicked(self):
        self.communicateTabDMS.signal_str.emit('安装PostgreSQL')
        import subprocess
        # 安装包的路径
        # install_package_path = r"D:\cc\software\ep\epvs\python\python-3.10.2-amd64.exe"
        install_package_path = os.path.join(self.PostgreSQL_installer_path,self.comboBox_PostgreSQL.currentText())
        try:
            self.communicateTabDMS.signal_str.emit('正在启动安装包')
            subprocess.Popen(install_package_path)   # 使用 subprocess.Popen 启动安装包
            self.communicateTabDMS.signal_str.emit('安装包已启动')
        except Exception as e:
            # print(f"启动安装包时出错：{str(e)}")
            self.communicateTabDMS.signal_str.emit(f"启动安装包时出错：{str(e)}")

    def on_buttonCreateDB_epdmsClicked(self):
        self.communicateTabDMS.signal_str.emit(f'创建数据库{self.lineEdit_dms_create_db_epdms.text()}')
        import psycopg2
        from psycopg2 import sql
        con = psycopg2.connect(dbname='postgres', user='postgres', host='127.0.0.1', password='cc')
        con.autocommit = True  # 连接必须处于自动提交模式
        cur = con.cursor()
        # sql.SQL and sql.Identifier are needed to avoid SQL injection attacks.
        cur.execute(sql.SQL('CREATE DATABASE {};').format(sql.Identifier(self.lineEdit_dms_create_db_epdms.text())))
        self.communicateTabDMS.signal_str.emit(f'创建数据库{self.lineEdit_dms_create_db_epdms.text()}已完成！')


    def on_buttonDMSSetDBClicked(self):
        pass
        self.communicateTabDMS.signal_str.emit(f'开始修改数据库配置！')
        # 需要修改"C:\Program Files\PostgreSQL\13\data\pg_hba.conf"文件
        # 先备份一份
        import shutil
        source_file = r"C:\Program Files\PostgreSQL\13\data\pg_hba.conf" # 要备份的文件名
        file_name, file_extension = os.path.splitext(source_file) # 获取文件的扩展名（后缀）
        backup_file = file_name + "_copy" + file_extension # 备份文件名
        shutil.copy(source_file, backup_file) # 使用shutil.copy()函数进行备份
        # 将settings_for_remote_txt追加到pg_hba.conf
        # 以附加模式打开文件，并将文本追加到文件末尾
        with open(source_file, 'a') as file:
            file.write("\n")
            file.write("# cc settings\n")
            file.write(f'host    all             all             {self.lineEdit_dms_set_db.text()}/32         scram-sha-256\n')
            file.write('host	all				all				0.0.0.0/0				trust\n')
        self.communicateTabDMS.signal_str.emit(f'完成修改数据库配置！')


    def on_buttonDMSInstallPackagesClicked(self):
        self.MyThread_DMSInstallPackages = MyThreadDMSInstallPackages(self) # 创建并启动线程
        self.MyThread_DMSInstallPackages.signal_str.connect(self.on_buttonDMSInstallPackagesCompleted)
        self.MyThread_DMSInstallPackages.start()

    def on_buttonDMSInstallPackagesCompleted(self,message):
        pass
        self.textEdit.append(message)

    def on_button_dms_deploy_epdms_clicked(self):
        self.MyThread_DMSDeployEPDMS = MyThreadDMSDeployEPDMS(self) # 创建并启动线程
        self.MyThread_DMSDeployEPDMS.signal_str.connect(self.on_buttonDMSInstallPackagesCompleted)
        self.MyThread_DMSDeployEPDMS.start()

    def on_button_dms_deploy_epdms_init_db_table_clicked(self):
        pass
        self.MyThread_DMSDeployEPDMSInitDBTable = MyThreadDMSDeployEPDMSInitDBTable(self)  # 创建并启动线程
        self.MyThread_DMSDeployEPDMSInitDBTable.signal_str.connect(self.on_button_dms_deploy_epdms_init_db_table_completed)
        self.MyThread_DMSDeployEPDMSInitDBTable.start()

    def on_button_dms_deploy_epdms_init_db_table_completed(self,message):
        pass
        self.textEdit.append(message)



class CommunicateTabDMS(QObject):
    signal_str = pyqtSignal(str)

class MyThreadDMSInstallPackages(QThread):
    # 定义一个信号，用于将结果传递给主线程
    signal_str = pyqtSignal(str)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc):
        super(MyThreadDMSInstallPackages, self).__init__()
        self.cc = cc

    def run(self):
        self.signal_str.emit('开始安装DMS用的Python包')
        disk_name = self.cc.dms_packages_path[0]
        import subprocess
        # 先看一下当前python解释器版本，如果不是Python3.10.2就不能安装包的
        # 创建一个子进程
        process_main_python_version = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands_main_python_version = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'python --version',
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]
        result_list = []
        # 执行所有命令
        for command in commands_main_python_version:
            process_main_python_version.stdin.write(command + "\n")
            process_main_python_version.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process_main_python_version.stdout.readline()
            if process_main_python_version.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                result_list.append(output_line.strip())

        os_default_python_version = result_list[-3]
        self.signal_str.emit(f'操作系统默认Python版本：{os_default_python_version}')

        # 关闭子进程的标准输入、输出和错误流
        process_main_python_version.stdin.close()
        process_main_python_version.stdout.close()
        process_main_python_version.stderr.close()
        # 等待子进程完成
        process_main_python_version.wait()

        if '3.10.2' not in os_default_python_version:
            QMessageBox.information(self, '警告！', '操作系统默认python解释器版本不是3.10.2，请人工处理！')
            return

        # 创建一个子进程
        process = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'workon epdms',  # 进入epdms虚拟环境
            f'{disk_name}:',
            f'cd {self.cc.dms_packages_path}',
            'pip install --no-index --find-links=./your_offline_packages/ -r requirements.txt',
            "pip list",
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]

        # 执行所有命令
        for command in commands:
            process.stdin.write(command + "\n")
            process.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process.stdout.readline()
            if process.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                self.signal_str.emit(f'{output_line.strip()}')

        # 关闭子进程的标准输入、输出和错误流
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()

        # 等待子进程完成
        process.wait()
        self.signal_str.emit('已完成安装！')

        self.signal_str.emit("完成安装DMS用的Python包！")# 发射信号，将结果传递给主线程


class MyThreadDMSDeployEPDMS(QThread):
    # 定义一个信号，用于将结果传递给主线程
    signal_str = pyqtSignal(str)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc):
        super(MyThreadDMSDeployEPDMS, self).__init__()
        self.cc = cc

    def run(self):
        self.signal_str.emit('开始解压epdms代码！')
        from ccMethod.ccMethod import CompressTool
        # 用法示例
        rar_file_path = os.path.join(self.cc.software_path, 'epdms.rar')  # 替换为你的RAR文件路径
        output_dir = self.cc.lineEdit_dms_deploy_epdms.text()  # 替换为你要解压到的目录
        CompressTool.uncompress_with_winrar(rar_file_path, output_dir)

        self.signal_str.emit("完成解压epdms代码！")# 发射信号，将结果传递给主线程


class MyThreadDMSDeployEPDMSInitDBTable(QThread):
    # 定义一个信号，用于将结果传递给主线程
    signal_str = pyqtSignal(str)

    # 下面这个init方法，继承了一个窗口的实例。一般在QThread中需要直接获取窗口控件时使用。
    def __init__(self, cc):
        super(MyThreadDMSDeployEPDMSInitDBTable, self).__init__()
        self.cc = cc

    def run(self):
        self.signal_str.emit('开始初始化epdms数据库表！')

        # 初始化数据库
        disk_name = self.cc.epdms_path[0]
        import subprocess
        # 先看一下当前python解释器版本，如果不是Python3.10.2就不能安装包的
        # 创建一个子进程
        process_main_python_version = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )

        # 命令列表
        commands_main_python_version = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'python --version',
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]
        result_list = []
        # 执行所有命令
        for command in commands_main_python_version:
            process_main_python_version.stdin.write(command + "\n")
            process_main_python_version.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process_main_python_version.stdout.readline()
            if process_main_python_version.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                result_list.append(output_line.strip())

        os_default_python_version = result_list[-3]
        self.signal_str.emit(f'操作系统默认Python版本：{os_default_python_version}')

        # 关闭子进程的标准输入、输出和错误流
        process_main_python_version.stdin.close()
        process_main_python_version.stdout.close()
        process_main_python_version.stderr.close()
        # 等待子进程完成
        process_main_python_version.wait()

        if '3.10.2' not in os_default_python_version:
            QMessageBox.information(self, '警告！', '操作系统默认python解释器版本不是3.10.2，请人工处理！')
            return

        # 创建一个子进程
        process = subprocess.Popen(
            "cmd",  # 在Windows上使用cmd
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,  # 使用文本模式以处理字符串
            shell=True  # 启用shell模式
        )


        # 命令列表
        commands = [
            'deactivate',  # 先退出epvs的虚拟环境，来到操作系统默认的环境，按理说是python3.10.2的环境
            'workon epdms',  # 进入epdms虚拟环境
            f'{disk_name}:',
            f'cd {self.cc.epdms_path}',
            'python manage.py migrate',
            '$env:DJANGO_SUPERUSER_USERNAME = "cc"; $env:DJANGO_SUPERUSER_PASSWORD = "cc"; $env:DJANGO_SUPERUSER_EMAIL = "your_email@example.com"; python manage.py createsuperuser --noinput\n', # 创建管理员
            "exit"  # 添加一个退出命令以关闭cmd进程
        ]

        # 执行所有命令
        for command in commands:
            process.stdin.write(command + "\n")
            process.stdin.flush()

        # 读取和打印输出
        while True:
            output_line = process.stdout.readline()
            if process.poll() is not None:  # 检查子进程是否完成
                break
            if output_line:
                print(output_line.strip())
                self.signal_str.emit(f'{output_line.strip()}')

        # 关闭子进程的标准输入、输出和错误流
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        # 等待子进程完成
        process.wait()

        self.signal_str.emit("完成初始化epdms数据表！")# 发射信号，将结果传递给主线程