import json
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
import logic.gl as gl


from logic.log import MyLog
logger = MyLog.log_init()

# # logger.debug("这是一个调试消息")
# # logger.info("这是一个信息消息")
# # logger.warning("这是一个警告消息")
# # logger.error("这是一个错误消息")
# # logger.critical("这是一个严重错误消息")


class Login(QMainWindow,Ui_LoginWindow):
    def __init__(self):
        super(Login,self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("static/pic/ep/logo.png"))

        icon = QIcon('static/pic/login/settings.png')  # 替换为你的 logo 图片路径
        self.pushButtonSettings.setIcon(icon)
        self.pushButtonSettings.setIconSize(self.pushButtonSettings.size())



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
        remember = settings.value('DEFAULT/remember', defaultValue='True')


        if bool(remember) == True:
            self.lineEditUserName.setText(settings.value('DEFAULT/user_name', defaultValue='cc'))
            self.lineEditPassword.setText(settings.value('DEFAULT/password', defaultValue='123'))
            self.checkBoxRememberUserName.setChecked(True)
            login_user_type = settings.value('DEFAULT/user_type', defaultValue='')

            # # 获取所有的键
            # keys = settings.allKeys()
            # # 打印每个键和对应的值
            # for key in keys:
            #     value = settings.value(key)
            #     print(f"Key: {key}, Value: {value}")

            # print('login_user_type:',login_user_type)
            if login_user_type == 'common':
                self.radioButtonLoginUserCommon.setChecked(True)
            if login_user_type == 'dms':
                self.radioButtonLoginUserDMS.setChecked(True)
        else:
            self.checkBoxRememberUserName.setChecked(False)


    def loginhandle(self):
        login_user = self.lineEditUserName.text()
        login_password = self.lineEditPassword.text()
        login_user_type = None
        if self.radioButtonLoginUserCommon.isChecked():
            login_user_type = 'common'
        if self.radioButtonLoginUserDMS.isChecked():
            login_user_type = 'dms'

        #记住登录信息
        config = configparser.ConfigParser()
        if self.checkBoxRememberUserName.isChecked():
            config['DEFAULT']={
                "user_name":login_user,
                'password':login_password,
                'remember':self.checkBoxRememberUserName.isChecked(),
                'user_type':login_user_type
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

        if login_user_type == 'common':
            if login_user == 'cc' and login_password == '123':
                pass
                logger.info("登录成功")
                self.close()  # 关闭当前登录窗口
                #加载EPCAM进度条
                self.progress_window = ProgressBarWindow()
                self.progress_window.show()
            else:
                logger.info("用户名或密码错误")
                QMessageBox.warning(self,
                        "警告",
                        "用户名或密码错误！",
                        QMessageBox.Yes)
                self.lineEditUserName.setFocus()


        if login_user_type == 'dms':
            # print("dms")
            from dms.dms import DMS
            login_result = DMS().login(login_user,login_password)
            if login_result['result']:
                logger.info("登录成功")
                self.close()  # 关闭当前登录窗口
                #加载EPCAM进度条
                self.progress_window = ProgressBarWindow()
                self.progress_window.show()
            else:
                logger.info(login_result['info'])
                QMessageBox.warning(self,
                        "警告",
                        login_result['info'],
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

        # logger.info('操作完成')
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





