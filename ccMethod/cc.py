import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 创建一个 QLineEdit 控件
        line_edit = QLineEdit(self)
        line_edit.setGeometry(50, 50, 200, 30)  # 设置控件的位置和宽度
        line_edit.setPlaceholderText("请输入文本")  # 设置占位文本

        # 设置 QLineEdit 控件的高度
        line_edit.setFixedHeight(40)  # 设置高度为40像素

        self.setGeometry(100, 100, 400, 200)
        self.setWindowTitle("设置 QLineEdit 控件的高度")


def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
