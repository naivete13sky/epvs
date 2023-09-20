import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel

class HelloWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("弹出窗口")
        self.setGeometry(200, 200, 300, 100)
        self.label = QLabel('你好', self)
        self.label.setGeometry(100, 40, 100, 20)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("主窗口")
        self.setGeometry(100, 100, 400, 200)

        self.buttonInstallPython = QPushButton("点击弹出窗口", self)

        # 将按钮点击事件与显示弹出窗口的方法关联
        self.buttonInstallPython.clicked.connect(self.show_hello_window)

    def show_hello_window(self):
        self.hello_window = HelloWindow()
        self.hello_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
