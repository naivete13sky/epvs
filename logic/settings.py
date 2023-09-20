import json
import subprocess

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QLineEdit, QMessageBox, QTableWidgetItem, QPushButton

from ui.settings import Ui_Dialog as DialogSettings



from logic.log import MyLog
logger = MyLog.log_init()


class DialogSettings(QDialog,DialogSettings):
    triggerDialogSettings = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    def __init__(self):


        logger.info("init")
        super(DialogSettings,self).__init__()
        self.setupUi(self)

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
        # 安装Python
        row_position = self.tableWidgetDMSDeployment.rowCount()
        self.tableWidgetDMSDeployment.insertRow(row_position)
        item1 = QTableWidgetItem("配置Python环境")
        item2 = QTableWidgetItem("配置")
        # item3 = QTableWidgetItem("检查")
        item4 = QTableWidgetItem("Python3.10.2，创建epvs虚拟环境")
        self.tableWidgetDMSDeployment.setItem(row_position, 0, item1)
        self.tableWidgetDMSDeployment.setItem(row_position, 1, item2)
        # self.tableWidgetDMSDeployment.setItem(row_position, 2, item3)
        self.tableWidgetDMSDeployment.setItem(row_position, 3, item4)

        # 配置DMS环境
        row_position = self.tableWidgetDMSDeployment.rowCount()
        self.tableWidgetDMSDeployment.insertRow(row_position)
        item1 = QTableWidgetItem("配置DMS环境")
        item2 = QTableWidgetItem("配置")
        # item3 = QTableWidgetItem("检查")
        item4 = QTableWidgetItem("装DMS用的python包")
        self.tableWidgetDMSDeployment.setItem(row_position, 0, item1)
        self.tableWidgetDMSDeployment.setItem(row_position, 1, item2)
        # self.tableWidgetDMSDeployment.setItem(row_position, 2, item3)
        self.tableWidgetDMSDeployment.setItem(row_position, 3, item4)

        # 部署DMS到Apache
        row_position = self.tableWidgetDMSDeployment.rowCount()
        self.tableWidgetDMSDeployment.insertRow(row_position)
        item1 = QTableWidgetItem("部署DMS到Apache")
        item2 = QTableWidgetItem("配置")
        # item3 = QTableWidgetItem("检查")
        item4 = QTableWidgetItem("备注")
        self.tableWidgetDMSDeployment.setItem(row_position, 0, item1)
        self.tableWidgetDMSDeployment.setItem(row_position, 1, item2)
        # self.tableWidgetDMSDeployment.setItem(row_position, 2, item3)
        self.tableWidgetDMSDeployment.setItem(row_position, 3, item4)

        # 部署Pytest框架
        row_position = self.tableWidgetDMSDeployment.rowCount()
        self.tableWidgetDMSDeployment.insertRow(row_position)
        item1 = QTableWidgetItem("部署Pytest框架")
        item2 = QTableWidgetItem("配置")
        # item3 = QTableWidgetItem("检查")
        item4 = QTableWidgetItem("备注")
        self.tableWidgetDMSDeployment.setItem(row_position, 0, item1)
        self.tableWidgetDMSDeployment.setItem(row_position, 1, item2)
        # self.tableWidgetDMSDeployment.setItem(row_position, 2, item3)
        self.tableWidgetDMSDeployment.setItem(row_position, 3, item4)

        # 配置检查按钮
        # 创建按钮并将其放入单元格中
        for row in range(self.tableWidgetDMSDeployment.rowCount()):
            # button = QPushButton(f"Button {row + 1}")
            button = QPushButton('点击检查')
            # button.clicked.connect(self.tableWidgetDMSDeployment_button_clicked)
            # 使用 lambda 函数连接按钮的点击事件，并传递按钮所在的行号作为参数
            button.clicked.connect(lambda checked, row=row: self.tableWidgetDMSDeployment_button_clicked(row))
            self.tableWidgetDMSDeployment.setCellWidget(row, 2, button)

        # 设置列宽
        self.tableWidgetDMSDeployment.setColumnWidth(0, 200)  # 第一个参数是列索引，第二个参数是列宽度
        self.tableWidgetDMSDeployment.setColumnWidth(3, 500)  # 第一个参数是列索引，第二个参数是列宽度

    def tableWidgetDMSDeployment_button_clicked(self,row):
        sender_button = self.sender()  # 获取发送信号的按钮
        if isinstance(sender_button, QPushButton):
            button_text = sender_button.text()
            # print(f"Button Clicked: {button_text}")
            # print(f"Button {row+1} Clicked")
            if row + 1 == 1:
                # print('python check')
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
                ret1 = process.stdout.readline()# Microsoft Windows [版本 10.0.22621.2134]
                ret2 = process.stdout.readline()# (c) Microsoft Corporation。保留所有权利。
                ret3 = process.stdout.readline()  # (c)
                ret4 = process.stdout.readline()  # 例如(epvs) D:\cc\python\epwork\epvs>workon epcam_ui_test

                # 执行第2个命令
                process.stdin.write(commands[1] + "\n")
                process.stdin.flush()
                ret5 = process.stdout.readline()# (epcam_ui_test) D:\cc\python\epwork\epvs>python --version
                ret6 = process.stdout.readline()# 如Python 3.11.4
                # 关闭子进程的标准输入、输出和错误流
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()
                # 等待子进程完成
                process.wait()

                # 检查结果标记颜色
                row_to_change = row  # 第row行的索引，Python索引从0开始
                button_to_change = self.tableWidgetDMSDeployment.cellWidget(row_to_change, 2)
                # print('ret6:',ret6,type(ret6),len(ret6))
                if ret6 == 'Python 3.10.2\n':
                    print("passed",ret6)
                    button_to_change.setStyleSheet("background-color: green;")
                    button_to_change.setText('通过')
                else:
                    print('failed',ret6)
                    button_to_change.setStyleSheet("background-color: red;")
                    button_to_change.setText('未通过')