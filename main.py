


from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from logic.login import Login




if __name__ == '__main__':


    import sys
    app = QtWidgets.QApplication(sys.argv)
    Ui_Login=Login()
    Ui_Login.show()#调用登录窗口
    sys.exit(app.exec_())

