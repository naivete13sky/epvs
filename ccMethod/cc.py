import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject

class Communicate(QObject):
    button_clicked = pyqtSignal()

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('PyQt5 Example')

        self.communicate = Communicate()

        # 创建一个按钮
        self.button = QPushButton('点击我写入信息', self)
        self.button.clicked.connect(self.emit_button_clicked_signal)

        # 创建一个文本编辑框
        self.text_edit = QTextEdit(self)

        # 创建一个垂直布局，并将按钮和文本编辑框添加到其中
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

        # 连接自定义信号与槽函数
        self.communicate.button_clicked.connect(self.on_button_click)

    def emit_button_clicked_signal(self):
        # 当按钮被点击时，发射自定义信号
        self.communicate.button_clicked.emit()

    def on_button_click(self):
        # 当按钮点击信号被发射时，将信息写入文本编辑框
        self.text_edit.append('按钮被点击了！')

def start_gui_app():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

def start_thread():
    # 创建一个后台线程来运行GUI应用程序
    thread = threading.Thread(target=start_gui_app)
    thread.start()

if __name__ == '__main__':
    # 启动后台线程
    start_thread()
