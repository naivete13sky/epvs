from PyQt5 import QtWidgets
from logic.login import Login




if __name__ == '__main__':
    import sys
    # QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)#启动浏览器需要先启动这个

    app = QtWidgets.QApplication(sys.argv)
    # app.setAttribute(Qt.AA_ShareOpenGLContexts)#启动浏览器需要先启动这个
    Ui_Login=Login()
    Ui_Login.show()#调用登录窗口
    sys.exit(app.exec_())

