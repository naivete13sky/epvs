import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton

app = QApplication(sys.argv)
window = QWidget()
layout = QGridLayout()

# 添加按钮到布局中
button1 = QPushButton("Button 1")
button2 = QPushButton("Button 2")
button3 = QPushButton("Button 3")
button4 = QPushButton("Button 4")
button5 = QPushButton("Button 5")

layout.addWidget(button1, 0, 0)
layout.addWidget(button2, 1, 0)
layout.addWidget(button3, 2, 0)
layout.addWidget(button4, 3, 0)
layout.addWidget(button5, 4, 0)

# 设置第2行的高度比例大一些
layout.setRowMinimumHeight(1, 100)

window.setLayout(layout)
window.show()
sys.exit(app.exec_())
