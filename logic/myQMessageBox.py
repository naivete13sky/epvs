import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QVBoxLayout, QPushButton,QLabel

class MyQMessageBox(QDialog):
    def __init__(self,title,label_text,lineEdit_text):
        super().__init__()
        self.setWindowTitle(title)
        self.label_text = QLabel()
        self.label_text.setText(label_text)
        self.line_edit = QLineEdit()
        self.line_edit.setText(lineEdit_text)
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.label_text)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.resize(200, self.sizeHint().height())





if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 创建自定义消息框
    message_box = MyQMessageBox("主料号ID","主料号ID：",'123')




    # 显示消息框
    message_box.exec_()

    sys.exit(app.exec_())
