from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 禁用最大化按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)

        # 设置窗口的固定大小
        self.setFixedSize(800, 600)  # 你可以根据需要调整宽度和高度

        # 其他初始化代码
        # ...

if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
    window.show()
    app.exec_()
