import sys
import traceback

from ccMethod import LogMethod0  # 导入异常处理代码
# 注册异常处理函数并传递日志文件路径参数
log_file_path = '..\log\epvs.log'  # 自定义日志文件路径
# sys.excepthook = lambda exctype, value, tb: LogMethod0.log_exception_traceback(exctype, value, tb, log_file_path)#日志方式一种
import logging
from ccMethod import LogMethod
def log_exception(exctype, value, tb):
    # 将异常信息记录到日志
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))
# 注册异常处理函数
sys.excepthook = log_exception
# 调用日志配置
LogMethod.setup_logging(log_file_path)

# 导入PyQt5和其他必要的模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton












class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        button = QPushButton('Trigger Error', self)
        button.clicked.connect(self.trigger_error)

    def trigger_error(self):
        # 这里会触发一个异常，因为没有try-except块来捕获异常
        1 / 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
