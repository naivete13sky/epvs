import json

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QLineEdit, QMessageBox

from ui.settings import Ui_Dialog as DialogSettings



import logging
# 创建一个日志记录器
logger = logging.getLogger('epvs_logger')
logger.setLevel(logging.DEBUG)
# 创建一个文件处理器
file_handler = logging.FileHandler('log/epvs.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
# 创建一个格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# 检查是否已经存在相同的处理器
if not any(isinstance(handler, logging.FileHandler) and handler.baseFilename == file_handler.baseFilename for
           handler in logger.handlers):
    # 添加文件处理器到日志记录器
    logger.addHandler(file_handler)


class DialogSettings(QDialog,DialogSettings):
    triggerDialogSettings = QtCore.pyqtSignal(str) # trigger传输的内容是字符串

    def __init__(self):


        logger.info("init")
        super(DialogSettings,self).__init__()
        self.setupUi(self)



        # 初始化显示全局参数
        with open(r'settings/epvs.json', 'r',encoding='utf-8') as cfg:
            self.settingsDict = json.load(cfg)  # (json格式数据)字符串 转化 为字典
        self.treeWidgetSettings.setColumnCount(2)
        # 设置表头
        self.treeWidgetSettings.setHeaderLabels(['项目', '值'])
        self.treeWidgetSettings.setColumnWidth(0, 300)
        # self.treeWidgetSettings.setColumnWidth(1, 100)
        self.addTreeItems(self.treeWidgetSettings, self.settingsDict)
        self.treeWidgetSettings.expandAll()

        # 初始化显示通用设置
        root_item = self.treeWidgetSettings.invisibleRootItem()

        item_name = 'gSetupType'
        found_item = None
        found_item = self.find_item(root_item, item_name)
        if found_item is not None:
            logger.info("Found item:"+str(found_item.text(0)))
            self.comboBoxSettingsGSetupType.setCurrentText(found_item.text(1))
        else:
            logger.info("Item not found.")

        item_name = 'GENESIS_DIR'
        found_item = None
        found_item = self.find_item(root_item, item_name)
        if found_item is not None:
            logger.info("Found item:"+str(found_item.text(0)))
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