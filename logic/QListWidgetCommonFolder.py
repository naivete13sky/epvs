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


