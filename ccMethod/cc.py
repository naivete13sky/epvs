import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout, QPushButton, QTabBar


class MyTabWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('QTabWidget 示例')
        self.setGeometry(100, 100, 600, 400)

        # 创建一个 QTabWidget
        tab_widget = QTabWidget(self)
        tab_widget.setTabPosition(QTabWidget.West)
        # 创建第一个选项卡
        tab1 = QWidget()
        layout1 = QVBoxLayout(tab1)
        label1 = QLabel('这是第一个选项卡中的标签')
        button1 = QPushButton('按钮1')
        layout1.addWidget(label1)
        layout1.addWidget(button1)

        # 创建第二个选项卡
        tab2 = QWidget()
        layout2 = QVBoxLayout(tab2)
        label2 = QLabel('这是第二个选项卡中的标签')
        button2 = QPushButton('按钮2')
        layout2.addWidget(label2)
        layout2.addWidget(button2)

        # 将选项卡添加到 QTabWidget
        tab_widget.addTab(tab1, '选项卡 1')
        tab_widget.addTab(tab2, '选项卡 2')


        tab_bar = tab_widget.tabBar()

        # 旋转文本
        for i in range(tab_widget.count()):
            tab_text = tab_widget.tabText(i)
            tab_widget.setTabText(i, '')  # 清空原有文本
            rotated_label = QLabel(tab_text, tab_widget)
            rotated_label.setStyleSheet("transform: rotate(90deg);")
            tab_bar.setTabButton(i, QTabBar.LeftSide, rotated_label)


        # 将 QTabWidget 设置为主窗口的中央部件
        self.setCentralWidget(tab_widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyTabWidget()
    window.show()
    sys.exit(app.exec_())
