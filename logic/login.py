import os

from ui.login import Ui_MainWindow as Ui_LoginWindow
from PyQt5.QtWidgets import *
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
            self.ussd = Ussd()#调用主窗口，一定要用self.，否则会闪退
            self.ussd.show()
            self.close()
        else:
            QMessageBox.warning(self,
                    "警告",
                    "用户名或密码错误！",
                    QMessageBox.Yes)
            self.lineEditUserName.setFocus()
