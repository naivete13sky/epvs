import os
import sys
from urllib.parse import urlparse

from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QLineEdit, QFileDialog, QApplication


class MyWebEnginePage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, parent=None):
        profile = QtWebEngineWidgets.QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Referer:")  # 设置Referer头字段的值
        print("cc")
        super(MyWebEnginePage, self).__init__(parent)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # 在这里实现自定义的导航请求逻辑
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            # 处理链接点击
            print("Link clicked:", url)
            return False  # 返回 False 表示不接受导航请求
        elif _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeFormSubmitted:
            # 处理表单提交
            print("Form submitted:", url)
            return False  # 返回 False 表示不接受导航请求

        # 默认情况下，接受所有其他类型的导航请求
        return super(MyWebEnginePage, self).acceptNavigationRequest(url, _type, isMainFrame)

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setGeometry(100, 100, 800, 600)

        # self.webview = QWebEngineView()
        self.webview = QWebEngineView()
        # 创建自定义的 WebEnginePage
        page = MyWebEnginePage()
        self.webview.setPage(page)

        self.setCentralWidget(self.webview)



        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.webview.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.webview.forward)
        toolbar.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.webview.reload)
        toolbar.addAction(reload_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.urlbar)

        self.webview.urlChanged.connect(self.update_urlbar)

        self.webprofile = QWebEngineProfile.defaultProfile()
        self.webprofile.downloadRequested.connect(self.download_requested)


    def load_url(self):
        url = self.urlbar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        self.webview.setUrl(QUrl(url))

    def load(self,url):
        self.webview.setUrl(QUrl(url))



    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())

    def download_requested(self, download):
        url = download.url().toString()
        file_name = os.path.basename(urlparse(url).path)
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.selectFile(file_name)
        if file_dialog.exec_() == QFileDialog.Accepted:
            save_path = file_dialog.selectedFiles()[0]
            download.setPath(save_path)
            download.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    web_view_dms = BrowserWindow()
    web_view_dms.load("http://10.97.80.119/admin/")  # 加载网页
    web_view_dms.show()
    sys.exit(app.exec_())