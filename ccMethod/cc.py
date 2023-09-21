import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton

def on_button_click():
    # 获取QLineEdit的文本内容
    text = line_edit.text()
    print("Entered Text:", text)

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("QLineEdit with Default Text")

layout = QVBoxLayout()

# 创建一个QLineEdit并设置默认文本
line_edit = QLineEdit()
line_edit.setText("Default Text")
layout.addWidget(line_edit)

# 创建一个按钮，当点击时打印QLineEdit的文本内容
button = QPushButton("Get Text")
button.clicked.connect(on_button_click)
layout.addWidget(button)

window.setLayout(layout)
window.show()

sys.exit(app.exec_())
