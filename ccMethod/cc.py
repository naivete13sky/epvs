import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 TableWidget with Button")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tableWidget = QTableWidget()
        layout.addWidget(self.tableWidget)

        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)

        # 创建按钮并将其放入单元格中
        for row in range(4):
            button = QPushButton(f"Button {row+1}")
            button.clicked.connect(self.button_clicked)
            self.tableWidget.setCellWidget(row, 0, button)

        # 设置第二列的数据
        for row in range(4):
            item = QTableWidgetItem(f"Data {row+1}")
            self.tableWidget.setItem(row, 1, item)

    def button_clicked(self):
        sender_button = self.sender()  # 获取发送信号的按钮
        if isinstance(sender_button, QPushButton):
            button_text = sender_button.text()
            print(f"Button Clicked: {button_text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_window = MyWindow()
    my_window.show()
    sys.exit(app.exec_())
