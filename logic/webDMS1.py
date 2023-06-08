import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QCoreApplication, Qt


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个浏览器视图
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)

        # 设置窗口标题和大小
        self.setWindowTitle("简单浏览器")
        self.setGeometry(100, 100, 800, 600)

    def load_url(self, url):
        # 加载指定URL的网页
        self.webview.load(QUrl(url))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = BrowserWindow()
    window.load_url("http://10.97.80.119/admin/")  # 加载初始页面

    window.show()
    sys.exit(app.exec_())
