import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QRadioButton, QPushButton, QMessageBox

class CustomMessageBox(QDialog):
    def __init__(self, options):
        super().__init__()

        self.options = options
        self.selected_option = None

        self.initUI()

    def initUI(self):
        self.setWindowTitle('选择一个选项')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.radio_buttons = []

        for option in self.options:
            radio_button = QRadioButton(option, self)
            radio_button.clicked.connect(self.radio_button_clicked)
            layout.addWidget(radio_button)
            self.radio_buttons.append(radio_button)

        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def radio_button_clicked(self):
        sender = self.sender()
        if sender.isChecked():
            self.selected_option = sender.text()

def main():
    app = QApplication(sys.argv)

    options = ['a', 'b', 'c']
    dialog = CustomMessageBox(options)

    result = dialog.exec_()

    if result == QDialog.Accepted:
        if dialog.selected_option:
            QMessageBox.information(None, '选择结果', f'你选择了：{dialog.selected_option}')
        else:
            QMessageBox.warning(None, '选择结果', '未选择任何选项')

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
