import os

from PyQt5 import QtCore

from ui.login import Ui_MainWindow as Ui_LoginWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
# from api.auth import loginres

from logic.ussd import Ussd
import configparser

class Login(QMainWindow,Ui_LoginWindow):
    def __init__(self):
        super(Login,self).__init__()
        self.setupUi(self)
        self.loadConfig()
        self.pushButtonLogin.clicked.connect(self.loginhandle)

    def loadConfig(self):
        currentFilePath = os.path.dirname(__file__)
        parentPath1 = os.path.dirname(currentFilePath)
        userIniPath = parentPath1 + r"\settings\user.ini"
        # print("load config")
        config = configparser.ConfigParser()
        configFilePath = userIniPath
        configFile = config.read(userIniPath)
        configDict = config.defaults()
        # print(configDict)
        if bool(configDict['remember']) == True:
            # print("remember = True")
            self.lineEditUserName.setText(configDict['user_name'])
            self.lineEditPassword.setText(configDict['password'])
            self.checkBoxRememberUserName.setChecked(True)
        else:
            self.checkBoxRememberUserName.setChecked(False)



    def loginhandle(self):
        pass
        # res = loginres(self.lineEdit.text(), self.lineEdit_2.text())
        # self.statusBar.showMessage(res['msg'])
        # if res['code']==1:
        #     self.ussd = Ussd()#调用主窗口，一定要用self.，否则会闪退
        #     self.ussd.show()
        #     self.close()

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

            #加载EPCAM进度条
            self.progress_window = ProgressBarWindow()
            self.progress_window.show()




            self.close()
        else:
            QMessageBox.warning(self,
                    "警告",
                    "用户名或密码错误！",
                    QMessageBox.Yes)
            self.lineEditUserName.setFocus()


    def update_progress(self):
        value = self.progress_window.progress_bar.value()



        value = (value + 1) % 101  # 增加进度条的值
        self.progress_window.set_progress(value)


    def update_text_start_EPCAM(self, message):
        self.message = message
        if self.message == "已完成加载EPCAM！":
            print(self.message)
            # self.pushButtonLoadEPCAM.setText("已加载EPCAM")
            # self.pushButtonLoadEPCAM.setStyleSheet("background-color: green")



class ProgressBarWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('正在加载EPCAM')
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
        self.ussd = Ussd()  # 调用主窗口，一定要用self.，否则会闪退
        self.ussd.show()





class WorkerThread(QThread):
    progress_changed = pyqtSignal(int)

    def run(self):
        total = 100
        # self.msleep(100)  # 模拟耗时操作
        self.progress_changed.emit(5)
        from config_ep.epcam import EPCAM
        self.epcam = EPCAM()
        self.progress_changed.emit(10)
        self.epcam.init()
        self.progress_changed.emit(95)

        self.progress_changed.emit(100)

        # self.progress_changed.emit(i)



        # for i in range(total + 1):
        #     self.progress_changed.emit(i)
        #     self.msleep(100)  # 模拟耗时操作



