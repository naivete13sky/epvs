import os
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from ui.login import Ui_MainWindow as Ui_LoginWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
# from api.auth import loginres
from PyQt5.QtCore import QSettings


from logic.mainWindow import MainWindow
import configparser

class Login(QMainWindow,Ui_LoginWindow):
    def __init__(self):
        super(Login,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))
        self.loadConfig()
        self.pushButtonLogin.clicked.connect(self.loginhandle)
        self.pushButtonSettings.clicked.connect(self.settingsShow)

    def loadConfig(self):
        currentFilePath = os.path.dirname(__file__)
        parentPath1 = os.path.dirname(currentFilePath)
        userIniPath = parentPath1 + r"\settings\user.ini"
        config = configparser.ConfigParser()
        configFilePath = userIniPath
        configFile = config.read(userIniPath)
        configDict = config.defaults()

        settings = QSettings(userIniPath, QSettings.IniFormat)
        remember = settings.value('remember', defaultValue='True')
        # print("remember:",remember)

        if bool(remember) == True:
            self.lineEditUserName.setText(settings.value('user_name', defaultValue='cc'))
            self.lineEditPassword.setText(settings.value('password', defaultValue='123'))
            self.checkBoxRememberUserName.setChecked(True)
        else:
            self.checkBoxRememberUserName.setChecked(False)


    def loginhandle(self):
        login_user = self.lineEditUserName.text()
        login_password = self.lineEditPassword.text()

        #记住登录信息
        config = configparser.ConfigParser()
        if self.checkBoxRememberUserName.isChecked():
            config['DEFAULT']={
                "user_name":login_user,
                'password':login_password,
                'remember':self.checkBoxRememberUserName.isChecked()
            }
        else:
            config['DEFAULT'] = {
                "user_name": login_user,
                'password': '',
                'remember': self.checkBoxRememberUserName.isChecked()
            }
        currentFilePath = os.path.dirname(__file__)
        parentPath1 = os.path.dirname(currentFilePath)
        userIniPath = parentPath1 + r"\settings\user.ini"
        with open(userIniPath,'w') as configFile:
            config.write(configFile)

        if login_user == 'cc' and login_password == '123':
            pass
            self.close()  # 关闭当前登录窗口
            #加载EPCAM进度条
            self.progress_window = ProgressBarWindow()
            self.progress_window.show()
        else:
            QMessageBox.warning(self,
                    "警告",
                    "用户名或密码错误！",
                    QMessageBox.Yes)
            self.lineEditUserName.setFocus()


    def settingsShow(self):
        from logic.mainWindow import DialogSettings
        self.dialogSettings = DialogSettings()
        self.dialogSettings.show()


#进度条窗口，用来显示加载EPCAM的进度条
class ProgressBarWindow(QWidget):
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

        self.worker_thread = WorkerThread()
        self.worker_thread.progress_changed.connect(self.update_progress)
        self.worker_thread.finished.connect(self.complete_operation)
        self.worker_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def complete_operation(self):
        # 在进度条达到100%后执行操作的代码
        print("操作完成")
        self.close()



        self.mainWindow = MainWindow()
        self.mainWindow.show()





class WorkerThread(QThread):
    progress_changed = pyqtSignal(int)

    def run(self):
        total = 100
        # self.msleep(100)  # 模拟耗时操作
        self.progress_changed.emit(5)
        self.progress_changed.emit(10)
        from config_ep.epcam import EPCAM
        self.epcam = EPCAM()
        self.progress_changed.emit(30)
        self.epcam.init()
        self.progress_changed.emit(95)
        self.progress_changed.emit(100)





