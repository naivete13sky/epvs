import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGroupBox, QPushButton

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TabWidget with QVBoxLayout and QGroupBox")

        # 创建QTabWidget
        tab_widget = QTabWidget(self)

        # 创建一个子页面
        tab1 = QWidget()

        # 在子页面中创建一个垂直布局
        layout = QVBoxLayout(tab1)

        # 创建QGroupBox并将其添加到垂直布局中
        group_box1 = QGroupBox("Group Box 1")
        button1 = QPushButton("Button 1")
        group_box1_layout = QVBoxLayout()
        group_box1_layout.addWidget(button1)
        group_box1.setLayout(group_box1_layout)
        layout.addWidget(group_box1)

        group_box2 = QGroupBox("Group Box 2")
        button2 = QPushButton("Button 2")
        group_box2_layout = QVBoxLayout()
        group_box2_layout.addWidget(button2)
        group_box2.setLayout(group_box2_layout)
        layout.addWidget(group_box2)

        # 添加子页面到TabWidget
        tab_widget.addTab(tab1, "Tab 1")

        # 将TabWidget设置为主窗口的中央部件
        self.setCentralWidget(tab_widget)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
