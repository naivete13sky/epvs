import sys
import logging
from ccMethod.ccMethod import LogMethod
from PyQt5 import QtWidgets
from logic.login import Login


def log_exception(exctype, value, tb):
    # 将异常信息记录到日志
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))


# 注册异常处理函数
sys.excepthook = log_exception
# 调用日志配置
LogMethod.setup_logging(r'log\epvs.log')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Ui_Login = Login()
    Ui_Login.show()  # 调用登录窗口
    sys.exit(app.exec_())
