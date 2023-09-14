import sys
# from ccMethod.ccMethod import LogMethod
# # 注册异常处理函数并传递日志文件路径参数
# log_file_path = 'log\epvs.log'  # 自定义日志文件路径
# sys.excepthook = lambda exctype, value, tb: LogMethod.log_exception(exctype, value, tb, log_file_path)


import logging
from ccMethod.ccMethod import LogMethod
def log_exception(exctype, value, tb):
    # 将异常信息记录到日志
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))
# 注册异常处理函数
sys.excepthook = log_exception
# 调用日志配置
LogMethod.setup_logging('log\epvs.log')




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

