import os
import sys
from urllib.parse import urlparse
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QToolBar, QLineEdit, QAction, QFileDialog, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Browser")
        self.setGeometry(100, 100, 800, 600)

        self.webview = QWebEngineView()
        # 获取QWebEngineSettings对象

        # settings = self.webview.page().settings()
        # settings.setAttribute(QWebEngineSettings.WebBrowserSettings.ReferrerPolicy,
        #                       QWebEngineSettings.WebBrowserSettings.NoReferrer)


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