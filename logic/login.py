import json
import os
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from logic.ProgressBarWindow import ProgressBarWindowLogin
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
        self.pushButtonSettings.setToolTip('设置')

        icon = QIcon('static/pic/login/help.png')  # 替换为你的 logo 图片路径
        self.pushButtonHelp.setIcon(icon)
        self.pushButtonHelp.setIconSize(self.pushButtonHelp.size())
        self.pushButtonHelp.setToolTip('帮助')


        self.loadConfig()

        # 槽连接
        self.pushButtonLogin.clicked.connect(self.loginhandle)
        self.pushButtonSettings.clicked.connect(self.settingsShow)
        self.pushButtonHelp.clicked.connect(self.helpShow)

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
                self.progress_window = ProgressBarWindowLogin()
                self.progress_window.show()
                gl.login_username = login_user
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
                self.progress_window = ProgressBarWindowLogin()
                self.progress_window.show()
                gl.login_username = login_user
            else:
                logger.info(login_result['info'])
                QMessageBox.warning(self,
                        "警告",
                        login_result['info'],
                        QMessageBox.Yes)
                self.lineEditUserName.setFocus()


    def settingsShow(self):
        from logic.settings import DialogSettings
        self.dialogSettings = DialogSettings()
        self.dialogSettings.show()

    def helpShow(self):
        from logic.help import WindowHelp
        self.windowHelp = WindowHelp()
        self.windowHelp.show()






