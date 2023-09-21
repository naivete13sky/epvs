import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QPushButton, QGridLayout

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TabWidget with GridLayout")

        # 创建QTabWidget
        tab_widget = QTabWidget(self)

        # 创建第一个子页面
        tab1 = QWidget()
        grid_layout = QGridLayout()
        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")
        grid_layout.addWidget(button1, 0, 0)
        grid_layout.addWidget(button2, 0, 1)
        tab1.setLayout(grid_layout)

        # 添加第一个子页面到TabWidget
        tab_widget.addTab(tab1, "Tab 1")

        # 创建第二个子页面（示例）
        tab2 = QWidget()
        # 在这里添加您的第二个子页面的内容和布局

        # 添加第二个子页面到TabWidget
        tab_widget.addTab(tab2, "Tab 2")

        # 将TabWidget设置为主窗口的中央部件
        self.setCentralWidget(tab_widget)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
