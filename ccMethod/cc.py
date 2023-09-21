from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QGroupBox, QPushButton, QSplitter, QWidget

app = QApplication([])

# 创建主窗口和主布局
window = QMainWindow()
central_widget = QWidget()
window.setCentralWidget(central_widget)
layout = QHBoxLayout(central_widget)

# 创建QSplitter
splitter = QSplitter()
splitter.setOrientation(0)
# 创建多个QGroupBox，每个QGroupBox都是水平布局
group_box1 = QGroupBox("Group Box 1")
group_box1_layout = QHBoxLayout()
button1 = QPushButton("Button 1")
group_box1_layout.addWidget(button1)
group_box1.setLayout(group_box1_layout)

group_box2 = QGroupBox("Group Box 2")
group_box2_layout = QHBoxLayout()
button2 = QPushButton("Button 2")
group_box2_layout.addWidget(button2)
group_box2.setLayout(group_box2_layout)

group_box3 = QGroupBox("Group Box 3")
group_box3_layout = QHBoxLayout()
button3 = QPushButton("Button 3")
group_box3_layout.addWidget(button3)
group_box3.setLayout(group_box3_layout)

# 将QGroupBox添加到QSplitter中
splitter.addWidget(group_box1)
splitter.addWidget(group_box2)
splitter.addWidget(group_box3)

# 将QSplitter添加到主布局
layout.addWidget(splitter)

window.show()
app.exec_()
