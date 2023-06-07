#进度条窗口，用来显示加载EPCAM的进度条
import json
import time

from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QProgressBar, QVBoxLayout

from logic import gl
from logic.mainWindow import MainWindow


class ProgressBarWindowLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('正在加载EPCAM')
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.resize(300, 100)

        self.worker_thread = WorkerThreadLogin()
        self.worker_thread.progress_changed.connect(self.update_progress)
        self.worker_thread.finished.connect(self.complete_operation)
        self.worker_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def complete_operation(self):
        # 在进度条达到100%后执行操作的代码

        # logger.info('操作完成')
        self.close()



        self.mainWindow = MainWindow()
        self.mainWindow.show()

class WorkerThreadLogin(QThread):
    progress_changed = pyqtSignal(int)

    def run(self):
        total = 100
        # self.msleep(100)  # 模拟耗时操作
        self.progress_changed.emit(5)
        self.progress_changed.emit(10)

        # 读取配置文件
        with open(r'settings/epvs.json', 'r', encoding='utf-8') as cfg:
            self.settings_dict = json.load(cfg)
        self.flag_epcam_startup = self.settings_dict['general']['flag_epcam_startup']  # (json格式数据)字符串 转化 为字典
        if self.flag_epcam_startup == '0':
            #登录时不启动
            pass

        if self.flag_epcam_startup == '1':
            #登录时启动cam
            from config_ep.epcam import EPCAM
            self.epcam = EPCAM()
            self.progress_changed.emit(30)
            self.epcam.init()
            gl.FlagEPCAM = True

        self.progress_changed.emit(95)
        self.progress_changed.emit(100)



class ProgressBarWindowLoadEPCAM(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('正在加载EPCAM')
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setWindowModality(Qt.WindowModal)
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.resize(300, 100)

        self.worker_thread = WorkerThreadLoadEPCAM()
        self.worker_thread.progress_changed.connect(self.update_progress)
        self.worker_thread.finished.connect(self.complete_operation)
        self.worker_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def complete_operation(self):
        # 在进度条达到100%后执行操作的代码

        # logger.info('操作完成')
        self.close()



class WorkerThreadLoadEPCAM(QThread):
    progress_changed = pyqtSignal(int)

    def run(self):
        total = 100
        # self.msleep(100)  # 模拟耗时操作
        # self.progress_changed.emit(5)

        from config_ep.epcam import EPCAM
        self.epcam = EPCAM()
        self.progress_changed.emit(30)
        self.epcam.init()
        gl.FlagEPCAM = True

        self.progress_changed.emit(95)
        self.progress_changed.emit(100)





class ProgressDialogThreadLoadEPCAM(QThread):
    progressChanged = pyqtSignal(int)

    def run(self):
        # for i in range(101):
        #     self.progressChanged.emit(i)
        #     self.msleep(10)  # 模拟耗时操作
        self.progressChanged.emit(10)
        time.sleep(0.1)
        self.progressChanged.emit(20)
        # time.sleep(0.1)
        from config_ep.epcam import EPCAM
        epcam = EPCAM()
        epcam.init()
        print("完成加载EPCAM!")
        gl.FlagEPCAM = True
        self.progressChanged.emit(90)
        self.progressChanged.emit(100)