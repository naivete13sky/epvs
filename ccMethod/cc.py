import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QSplitter, QGroupBox, QTextEdit

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QTabWidget Example")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个QTabWidget
        tabWidget = QTabWidget(self)
        self.setCentralWidget(tabWidget)

        # 创建一个子页面
        self.tabDMSDeployment = QWidget()
        tabWidget.addTab(self.tabDMSDeployment, "DMS Deployment")

        # 创建一个QSplitter来划分子页面
        splitter = QSplitter(self.tabDMSDeployment)
        self.tabDMSDeploymentLayout = QVBoxLayout(self.tabDMSDeployment)
        self.tabDMSDeploymentLayout.addWidget(splitter)

        # 创建左侧区域
        leftSplitter = QSplitter()
        leftSplitter.setOrientation(0)
        splitter.addWidget(leftSplitter)

        # 创建多个QGroupBox并垂直划分左侧区域
        groupBox1 = QGroupBox("Group 1")
        groupBox2 = QGroupBox("Group 2")
        groupBox3 = QGroupBox("Group 3")

        leftSplitter.addWidget(groupBox1)
        leftSplitter.addWidget(groupBox2)
        leftSplitter.addWidget(groupBox3)

        # 创建右侧区域并添加多行文本框
        rightWidget = QWidget()
        splitter.addWidget(rightWidget)

        textEdit = QTextEdit()
        rightLayout = QVBoxLayout(rightWidget)
        rightLayout.addWidget(textEdit)

def main():
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
