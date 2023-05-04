import os
import shutil
import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from ui.ussd2 import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI

class Ussd2(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(Ussd2,self).__init__()
        self.setupUi(self)


