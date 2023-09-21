import sys
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem

app = QApplication(sys.argv)

# 创建一个QListWidget
list_widget = QListWidget()

# 创建一些项目并设置它们的高度
for i in range(5):
    item = QListWidgetItem("Item {}".format(i))
    item.setSizeHint(item.sizeHint())  # 设置项目的高度为默认高度，即文本的高度
    list_widget.addItem(item)

# 设置自定义的高度
for i in range(5, 10):
    item = QListWidgetItem("Custom Height Item {}".format(i))
    custom_height = 20  # 设置自定义的高度
    item.setSizeHint(QSize(item.sizeHint().width(), custom_height))  # 设置项目的高度
    list_widget.addItem(item)

list_widget.show()
sys.exit(app.exec_())
