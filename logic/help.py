from PyQt5.QtCore import QSettings, QFile, QTextStream
from PyQt5.QtGui import QFont, QTextImageFormat, QPixmap, QTextBlockFormat, QTextFormat, QTextCursor, QTextDocument
from PyQt5.QtWidgets import QTextEdit, QAction, QFileDialog, QFontDialog, QColorDialog, QMainWindow, QInputDialog


class WindowHelp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个QTextEdit控件
        self.text_edit = QTextEdit()
        # self.text_document = QTextDocument()

        # self.line_spacing = 1.5
        # self.text_document.setDefaultStyleSheet("p { line-height: 1.5; }")  # 设置行距


        self.setCentralWidget(self.text_edit)

        # 创建一个菜单项和工具栏
        self.font_size_action = QAction('字体大小', self)
        self.font_size_action.triggered.connect(self.set_font_size)
        self.bold_action = QAction('加粗', self)
        # self.bold_action.triggered.connect(self.set_bold)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.italic_action = QAction('斜体', self)
        self.italic_action.triggered.connect(self.set_italic)
        self.underline_action = QAction('下划线', self)
        self.underline_action.triggered.connect(self.set_underline)
        self.color_action = QAction('颜色', self)
        self.color_action.triggered.connect(self.set_color)
        self.line_spacing_action = QAction('行距', self)
        self.line_spacing_action.triggered.connect(self.set_line_spacing)
        self.insert_image_action = QAction('插入图片', self)
        self.insert_image_action.triggered.connect(self.insert_image)

        self.save_action = QAction('保存', self)
        self.save_action.triggered.connect(self.save_text)

        self.load_action = QAction('加载', self)
        self.load_action.triggered.connect(self.load_text)


        menu = self.menuBar()
        file_menu = menu.addMenu('文件')
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)

        edit_menu = menu.addMenu('编辑')
        edit_menu.addAction(self.font_size_action)
        edit_menu.addAction(self.bold_action)
        edit_menu.addAction(self.italic_action)
        edit_menu.addAction(self.underline_action)
        edit_menu.addAction(self.color_action)
        edit_menu.addAction(self.line_spacing_action)
        edit_menu.addAction(self.insert_image_action)

        toolbar = self.addToolBar('文件')
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.load_action)
        toolbar = self.addToolBar('编辑')
        toolbar.addAction(self.font_size_action)
        toolbar.addAction(self.bold_action)
        toolbar.addAction(self.italic_action)
        toolbar.addAction(self.underline_action)
        toolbar.addAction(self.color_action)
        toolbar.addAction(self.line_spacing_action)
        toolbar.addAction(self.insert_image_action)

        self.setGeometry(400, 100,1000, 800)

        # 加载上一次保存的文本内容
        settings = QSettings('MyCompany', 'MyApp')
        self.text_edit.setHtml(settings.value('text', ''))
        # self.text_document.setHtml(settings.value('text', ''))
        # self.text_edit.setDocument(self.text_document)




    def save_text(self):
        filename, _ = QFileDialog.getSaveFileName(self, '保存文件', '.', 'Text files (*.txt)')
        if filename:
            file = QFile(filename)
            if file.open(QFile.WriteOnly | QFile.Text):
                stream = QTextStream(file)
                stream << self.text_edit.toHtml()
                file.close()

    def load_text(self):
        filename, _ = QFileDialog.getOpenFileName(self, '加载文件', '.', 'Text files (*.txt)')
        if filename:
            file = QFile(filename)
            if file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(file)
                self.text_edit.setHtml(stream.readAll())
                file.close()


    def set_font_size(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_edit.setFont(font)

    def set_bold(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontWeight(QFont.Bold)
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setBold(not font.bold())
            self.text_edit.setCurrentFont(font)

    def toggle_bold(self):
        font = self.text_edit.currentFont()
        if font.weight() == QFont.Bold:
            font.setWeight(QFont.Normal)
        else:
            font.setWeight(QFont.Bold)
        self.text_edit.setCurrentFont(font)


    def set_italic(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontItalic(not text_format.fontItalic())
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setItalic(not font.italic())
            self.text_edit.setCurrentFont(font)

    def set_underline(self):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            text_format = cursor.charFormat()
            text_format.setFontUnderline(not text_format.fontUnderline())
            cursor.mergeCharFormat(text_format)
        else:
            font = self.text_edit.currentFont()
            font.setUnderline(not font.underline())
            self.text_edit.setCurrentFont(font)

    def set_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                text_format = cursor.charFormat()
                text_format.setForeground(color)
                cursor.mergeCharFormat(text_format)
            else:
                self.text_edit.setTextColor(color)


    def set_line_spacing0(self):
        '''not ok'''
        dialog = QInputDialog()
        dialog.setLabelText("请输入行距倍数:")
        dialog.setDoubleRange(0.1, 10.0)  # 设置行距倍数的有效范围
        if dialog.exec_() == QInputDialog.Accepted:
            line_spacing_multiplier = dialog.doubleValue()

            cursor = self.text_edit.textCursor()
            cursor.select(QTextCursor.Document)
            selection = cursor.selection()
            cursor.clearSelection()

            self.text_document.setDefaultStyleSheet("p { line-height: %s; }" % (line_spacing_multiplier))  # 设置行距


            self.text_edit.setDocument(self.text_document)

    def set_line_spacing(self):
        # 弹出对话框获取用户输入的行距
        line_spacing, ok = QInputDialog.getDouble(self, '设置行距', '请输入行距值（倍数）:', 1.5, 0.1, 10, 1)

        if ok:
            # 设置文本编辑框的行距
            self.text_edit.setStyleSheet(f"p {{ line-height: {line_spacing}; }}")



    def insert_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, '选择图片', '.', 'Image files (*.jpg *.gif *.png)')
        if filename:
            image = QTextImageFormat()
            image.setName(filename)
            pixmap = QPixmap(filename)
            image.setWidth(pixmap.width())
            image.setHeight(pixmap.height())
            cursor = self.text_edit.textCursor()
            cursor.insertImage(image)


    def closeEvent(self, event):
        # 保存当前文本内容
        settings = QSettings('MyCompany', 'MyApp')
        settings.setValue('text', self.text_edit.toHtml())
        event.accept()