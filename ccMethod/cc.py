import sys
import time
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# 自定义线程类，用于执行耗时任务
class WorkerThread(QThread):
    # 定义一个信号，用于将结果传递给主线程
    result_signal = pyqtSignal(str)

    def run(self):
        # 模拟一个耗时任务
        time.sleep(2)
        # 发射信号，将结果传递给主线程
        self.result_signal.emit("耗时任务完成！")

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyQt5 Thread and Signal Example')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("等待任务完成...")
        layout.addWidget(self.label)

        self.button = QPushButton("开始任务")
        layout.addWidget(self.button)

        self.button.clicked.connect(self.startTask)

        self.setLayout(layout)

    def startTask(self):
        # 创建并启动线程
        self.worker_thread = WorkerThread()
        self.worker_thread.result_signal.connect(self.onTaskCompleted)
        self.worker_thread.start()
        self.button.setEnabled(False)

    def onTaskCompleted(self, result):
        # 在任务完成时被调用，更新UI
        self.label.setText(result)
        self.button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
