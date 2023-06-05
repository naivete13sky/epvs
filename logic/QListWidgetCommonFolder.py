import json
import os
import subprocess

from PyQt5 import QtCore

import logic.gl as gl
from PyQt5.QtCore import QSize, QUrl, Qt, QRect, QProcess, QDir
from PyQt5.QtGui import QDesktopServices, QClipboard, QKeySequence, QTextDocument, QAbstractTextDocumentLayout, QIcon, \
    QPainter, QContextMenuEvent, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QFileSystemModel, QApplication, qApp, QMessageBox, QShortcut, \
    QStyledItemDelegate, QStyle, QMenu, QAction, QStyleOptionMenuItem, QDialog, QVBoxLayout, QLineEdit, \
    QDialogButtonBox, QFileDialog, QInputDialog, QLabel, QMainWindow, QWidget, QPushButton, QGridLayout, QCheckBox, \
    QHBoxLayout, QRadioButton, QListWidget
import shutil
from pathlib import Path
import send2trash
from ccMethod.ccMethod import CompressTool

class QListWidgetCommonFolder(QListWidget):
    triggerQListWidgetCommonFolderStr = QtCore.pyqtSignal(str)  # trigger传输的内容是字符串
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: lightgray;")
        # 添加常用文件夹项
        self.addItem("桌面")
        self.addItem("下载")
        self.addItem("文档")
        self.addItem("图片")
        self.addItem("音乐")
        self.addItem("视频")

        # 增加自定义常用文件夹，从配置文件读取
        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.common_folder_dict = self.settings_dict['general']['common_folder']  # (json格式数据)字符串 转化 为字典
        # print('self.common_folder_dict:',type(self.common_folder_dict),self.common_folder_dict)
        for k, v in self.common_folder_dict.items():
            # print(k,v)
            self.addItem(k)

        # 设置右击事件处理函数
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            lambda pos: self.folder_list_handle_right_click(self.itemAt(pos)))


    def folder_list_handle_right_click(self,item):
        # 获取当前鼠标位置
        pos = self.mapFromGlobal(self.cursor().pos())

        # 将列表控件坐标转换为全局坐标
        global_pos = self.viewport().mapToGlobal(pos)

        # 创建快捷菜单并添加动作
        menu = QMenu(self)
        # edit_action = QAction("Edit", self.folder_list)
        delete_action = QAction("Delete", self)
        # menu.addAction(edit_action)
        menu.addAction(delete_action)

        # 在全局坐标位置显示快捷菜单
        action = menu.exec_(global_pos)

        # 处理选择的动作
        if action == delete_action:
            print("Delete item:", item.text())