import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 TableWidget")
        self.setGeometry(100, 100, 800, 600)

        # 创建一个QWidget作为中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建一个垂直布局
        layout = QVBoxLayout(central_widget)

        # 创建一个QTableWidget并添加到布局中
        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        # 设置表格的行数和列数
        self.tableWidget.setRowCount(0)  # 初始行数为0
        self.tableWidget.setColumnCount(3)  # 列数为3

        # 创建一个按钮用于添加行
        add_row_button = QPushButton("添加行")
        add_row_button.clicked.connect(self.add_row)
        layout.addWidget(add_row_button)

    def add_row(self):
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)

        item1 = QTableWidgetItem("列1数据")
        item2 = QTableWidgetItem("列2数据")
        item3 = QTableWidgetItem("列3数据")

        self.tableWidget.setItem(row_position, 0, item1)
        self.tableWidget.setItem(row_position, 1, item2)
        self.tableWidget.setItem(row_position, 2, item3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = MyWindow()
    my_window.show()
    sys.exit(app.exec_())
