import os
import subprocess

import logic.gl as gl
from PyQt5.QtCore import QSize, QUrl, Qt, QRect, QProcess, QDir
from PyQt5.QtGui import QDesktopServices, QClipboard, QKeySequence, QTextDocument, QAbstractTextDocumentLayout, QIcon, \
    QPainter, QContextMenuEvent, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListView, QFileSystemModel, QApplication, qApp, QMessageBox, QShortcut, \
    QStyledItemDelegate, QStyle, QMenu, QAction, QStyleOptionMenuItem, QDialog, QVBoxLayout, QLineEdit, \
    QDialogButtonBox, QFileDialog, QInputDialog, QLabel, QMainWindow, QWidget, QPushButton
import shutil
from pathlib import Path
import send2trash
from ccMethod.ccMethod import CompressTool

class ListViewFile(QListView):
    def __init__(self,path):
        super().__init__()
        self.path = path
        # 加载文件夹内容
        folder_model = QFileSystemModel()
        folder_model.setRootPath(path)
        self.setModel(folder_model)
        self.setRootIndex(folder_model.index(path))
        self.setIconSize(QSize(64, 64))
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setGridSize(QSize(120, 120))  # 设置图标的固定宽度和高度
        self.setSpacing(20)  # 设置图标之间的间距

        # 创建上下文菜单
        self.context_menu = QMenu(self)
        # 当鼠标悬停在菜单项上时，项目的文本会消失。这个问题可能是由于菜单项的样式造成的，所以要设置下
        self.context_menu.setStyleSheet("QMenu::item:selected { color: black; }")


        # 创建菜单项
        self.open_action = QAction("打开", self)
        self.copy_action = QAction("复制", self)
        self.paste_action = QAction("粘贴", self)
        self.cut_action = QAction("剪切", self)
        self.delete_action = QAction("删除", self)
        self.rename_action = QAction("重命名", self)
        self.newFolder_action = QAction("新建文件夹", self)


        # 添加菜单项到上下文菜单
        self.context_menu.addAction(self.open_action)
        self.context_menu.addAction(self.copy_action)
        self.context_menu.addAction(self.paste_action)
        self.context_menu.addAction(self.cut_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addAction(self.rename_action)
        self.context_menu.addAction(self.newFolder_action)


        # 设置上下文菜单策略
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.open_action.triggered.connect(self.open_selected)
        self.copy_action.triggered.connect(self.copy_selected)
        self.paste_action.triggered.connect(self.paste_selected)
        self.cut_action.triggered.connect(self.cut_selected)
        self.delete_action.triggered.connect(self.delete_selected)
        self.rename_action.triggered.connect(self.rename_selected)
        self.newFolder_action.triggered.connect(self.newFolder)


        # 添加快捷键
        self.create_shortcuts()

    def contextMenuEvent(self, event: QContextMenuEvent):
        pass
        #本方法是在右击后才发生的

    def customizeContextMenu(self):
        # 在这里执行自定义操作，例如更改菜单项、添加额外的菜单项等
        print("Customizing context menu...")
        # 清空菜单项
        self.context_menu.clear()



        # 创建菜单项
        self.open_action = QAction("打开", self)
        self.copy_action = QAction("复制", self)
        self.paste_action = QAction("粘贴", self)
        self.cut_action = QAction("剪切", self)
        self.delete_action = QAction("删除", self)
        self.rename_action = QAction("重命名", self)
        self.newFolder_action = QAction("新建文件夹", self)


        # 添加菜单项到上下文菜单
        self.context_menu.addAction(self.open_action)
        self.context_menu.addAction(self.copy_action)
        self.context_menu.addAction(self.paste_action)
        self.context_menu.addAction(self.cut_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addAction(self.rename_action)
        self.context_menu.addAction(self.newFolder_action)

        self.open_action.triggered.connect(self.open_selected)
        self.copy_action.triggered.connect(self.copy_selected)
        self.paste_action.triggered.connect(self.paste_selected)
        self.cut_action.triggered.connect(self.cut_selected)
        self.delete_action.triggered.connect(self.delete_selected)
        self.rename_action.triggered.connect(self.rename_selected)
        self.newFolder_action.triggered.connect(self.newFolder)


        # 根据选中的项目动态设置右击快捷菜单
        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            #self.absolutePath是当前选中的文件或文件夹的路径，而self.path是父目录
            self.absolutePath = os.path.join(self.path, text)

            if os.path.isfile(self.absolutePath):
                if self.absolutePath.split('.')[-1] in ['rar','zip','7z']:
                    self.sub_menu_rar = QMenu("WinRAR", self)
                    self.file_name, self.file_extension = os.path.splitext(os.path.basename(self.absolutePath))
                    #下面这个是要解压到压缩文件的名称的文件夹
                    self.rar_action_uncompress_to_rarFileName_folder = QAction("解压到{}".format(self.file_name, self))
                    #下面这个是要解压到当前文件夹
                    self.rar_action_uncompress_to_current_folder = QAction("解压到当前文件夹", self)
                    self.sub_menu_rar.addAction(self.rar_action_uncompress_to_rarFileName_folder)
                    self.sub_menu_rar.addAction(self.rar_action_uncompress_to_current_folder)
                    # 设置子菜单的样式
                    # self.sub_menu_rar.setStyleSheet("background-color: red;")
                    # 设置被鼠标悬停项目的颜色为红色
                    self.sub_menu_rar.setStyleSheet("QMenu::item:selected { color: red; }")
                    self.context_menu.addMenu(self.sub_menu_rar)
                    self.rar_action_open = QAction("RAR打开", self)
                    self.context_menu.addAction(self.rar_action_open)

                    self.rar_action_uncompress_to_rarFileName_folder.triggered.connect(self.rar_uncompress_to_rarFileName_folder_selected)
                    self.rar_action_uncompress_to_current_folder.triggered.connect(self.rar_uncompress_to_current_folder_selected)
                    self.rar_action_open.triggered.connect(self.rar_open_selected)


            if os.path.isdir(self.absolutePath):
                self.sub_menu_rar = QMenu("WinRAR", self)
                self.folder_name = os.path.basename(self.absolutePath)
                # 下面这个是要把选中的文件夹压缩成rar文件，此压缩文件名称是选中的文件夹的名称
                self.rar_action_compress_to_folderName = QAction("压缩到{}".format(self.folder_name), self)
                self.sub_menu_rar.addAction(self.rar_action_compress_to_folderName)

                # 设置子菜单的样式
                # 设置被鼠标悬停项目的颜色为红色
                self.sub_menu_rar.setStyleSheet("QMenu::item:selected { color: red; }")
                self.context_menu.addMenu(self.sub_menu_rar)


                #连接槽
                self.rar_action_compress_to_folderName.triggered.connect(self.rar_compress_to_folderName_selected)



        if not selected_indexes:
            return
        # 示例：移除粘贴菜单项
        # self.removeAction(self.findChild(QAction, "pasteAction"))


    def show_context_menu(self, position):
        # 在显示上下文菜单之前执行自定义操作,每次右击时都会调用一下
        self.customizeContextMenu()

        # 设置菜单项样式
        self.context_menu.setStyleSheet("QMenu::item:selected { background-color: black; }")


        action = self.context_menu.exec_(self.mapToGlobal(position))
        if action is not None:
            # 在这里处理所选菜单项的操作
            print("Selected action:", action.text())


    def set_path(self,path):
        pass
        print("更新path",path)
        self.path = path


    # # 可以在按下鼠标时获取当前项目的信息，暂时用不到
    # def mousePressEvent(self, event):
    #     index = self.indexAt(event.pos())
    #     if index.isValid() and event.button() == Qt.LeftButton:
    #         self.filePath = index.data(Qt.DisplayRole)
    #         print("按下鼠标时:", self.filePath)
    #     super().mousePressEvent(event)



    def open_selected(self):
        print("open:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pass
                url = QUrl.fromLocalFile(self.absolutePath)
                QDesktopServices.openUrl(url)

        if not selected_indexes:
            return


    def copy_selected(self):
        print("copy:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.absolutePath)

        if not selected_indexes:
            return


    def cut_selected(self):
        print("cut:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                gl.cutFlag = True
                # 将文件路径设置到剪贴板
                clipboard = qApp.clipboard()
                clipboard.setText(self.absolutePath, QClipboard.Clipboard)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('Files have been cut.')
                msg_box.exec_()

                print('gl.cutFlag', gl.cutFlag)

        if not selected_indexes:
            return


    def paste_selected(self):
        print('gl.cutFlag', gl.cutFlag)
        clipboard = QApplication.clipboard()
        self.absolutePath = clipboard.text(QClipboard.Clipboard)
        if self.absolutePath:
            # Perform paste operation with the file_path
            print('Pasting file:', self.absolutePath)


            if os.path.isfile(self.absolutePath):
                #如果是文件
                print('file,self.path for paste',self.path)

                if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                    #已存在同名文件
                    print("Destination file already exists.")
                    overwrite_type = QMessageBox.question(None, "确认", "目标文件已存在，要覆盖吗？",
                                                  QMessageBox.Yes | QMessageBox.No)
                    if overwrite_type != QMessageBox.Yes:
                        print("不覆盖")
                        return


                try:
                    if gl.cutFlag == True:

                        #剪切后粘贴
                        try:
                            # 使用shutil.move移动文件，如果目标文件存在，则覆盖
                            # shutil.move(self.absolutePath, self.path,copy_function=shutil.copy)
                            os.replace(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        except Exception as e:
                            print(f'Error while pasting file: {e}')

                    else:
                        # 复制后粘贴
                        shutil.copy(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        print("File copied successfully!")
                except IOError as e:
                    print(f"Unable to copy file. {e}")

            if os.path.isdir(self.absolutePath):
                #如果是文件夹
                print('folder,self.path for paste',self.path)

                if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                    #已存在同名文件
                    print("Destination folder already exists.")
                    overwrite_type = QMessageBox.question(None, "确认", "目标文件夹已存在，要覆盖吗？",
                                                  QMessageBox.Yes | QMessageBox.No)
                    if overwrite_type != QMessageBox.Yes:
                        print("不覆盖")#不覆盖时直接返回
                        return


                try:
                    if gl.cutFlag == True:

                        #剪切后粘贴
                        try:
                            # 删除已存在的目标文件夹
                            if os.path.exists(os.path.join(self.path, os.path.basename(self.absolutePath))):
                                shutil.rmtree(os.path.join(self.path, os.path.basename(self.absolutePath)))
                            # 使用shutil.move移动文件，如果目标文件存在，则覆盖
                            shutil.move(self.absolutePath, os.path.join(self.path, os.path.basename(self.absolutePath)),copy_function=shutil.copy)

                        except Exception as e:
                            print(f'粘贴文件夹时发生错误: {e}')

                    else:
                        # 删除已存在的目标文件夹
                        if os.path.exists(os.path.join(self.path,os.path.basename(self.absolutePath))):
                            shutil.rmtree(os.path.join(self.path,os.path.basename(self.absolutePath)))
                        # 复制后粘贴
                        shutil.copytree(self.absolutePath, os.path.join(self.path,os.path.basename(self.absolutePath)))
                        print("已成功复制文件夹!")
                except IOError as e:
                    print(f"未能复制文件夹. {e}")


        gl.cutFlag = False#重置


    def delete_selected(self):
        print("delete:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pathStandard = Path(self.absolutePath).resolve().as_posix()
                pathStandard = pathStandard.replace('/','\\')

                print('pathStandard:',pathStandard)
                # 将文件移动到回收站
                send2trash.send2trash(pathStandard)

                # # 下面方法是永久删除
                # if os.path.isfile(self.absolutePath):
                #     os.remove(self.absolutePath)
                # if os.path.isdir(self.absolutePath):
                #     shutil.rmtree(self.absolutePath)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('已删除！')
                msg_box.exec_()



        if not selected_indexes:
            return

    def rename_selected(self):
        index = self.currentIndex()
        old_name = index.data()
        # print("old_name:", old_name)
        self.absolutePath = os.path.join(self.path, old_name)
        dialog = RenameDialog(old_name)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.rename_edit.text()
            if new_name:
                # print("new_name:",new_name)
                new_name_full_path = os.path.join(self.path,new_name)
                os.rename(self.absolutePath,new_name_full_path)
                # print('文件重命名成功！')


    def newFolder(self):
        folder_path = self.path
        if folder_path:
            # 下面这行会异常提示，尺寸问题
            new_folder_name, ok = QInputDialog.getText(self, "新建文件夹", "输入文件夹名称：")
            if ok and new_folder_name:
                new_folder_path = f"{folder_path}/{new_folder_name}"
                try:
                    os.mkdir(new_folder_path)
                    QMessageBox.information(self, "成功", "文件夹创建成功！")
                except OSError:
                    QMessageBox.warning(self, "错误", "文件夹创建失败！")








    def rar_open_selected(self):
        print("rar解压文件:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pass

                winrar_path = r"C:\Program Files\WinRAR\WinRAR.exe"
                # 构建执行的命令
                command = [winrar_path, self.absolutePath]

                # 执行命令并等待命令完成
                subprocess.Popen(command, shell=True).wait()



                # 显示消息框
                # msg_box = QMessageBox(self)
                # msg_box.setText('解压已完成！')
                # msg_box.exec_()



        if not selected_indexes:
            return

    def rar_uncompress_to_rarFileName_folder_selected(self):
        print("rar解压文件到与压缩包名称相同的文件夹:",self.file_name)

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                process = QProcess()
                command = 'C:/Program Files/WinRAR/WinRAR.exe'
                destPath = os.path.join(self.path,self.file_name)
                print('destPath:', destPath)
                if not os.path.exists(destPath):
                    os.mkdir(destPath)

                arguments = ['x', '-r', self.absolutePath, destPath]  # 替换为实际的压缩文件路径和目标文件夹路径
                # 执行解压缩命令
                process.startDetached(command, arguments)

                # 显示消息框
                # msg_box = QMessageBox(self)
                # msg_box.setText('解压已完成！')
                # msg_box.exec_()



        if not selected_indexes:
            return

    def rar_uncompress_to_current_folder_selected(self):
        print("rar解压文件到当前文件夹:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                process = QProcess()
                command = 'C:/Program Files/WinRAR/WinRAR.exe'
                arguments = ['x', '-r', self.absolutePath, self.path]  # 替换为实际的压缩文件路径和目标文件夹路径
                # 执行解压缩命令
                process.startDetached(command, arguments)



                # 显示消息框
                # msg_box = QMessageBox(self)
                # msg_box.setText('解压已完成！')
                # msg_box.exec_()



        if not selected_indexes:
            return

    def copy_file(source_path, destination_path):
        if os.path.exists(destination_path):
            print("Destination file already exists.")
            overwrite = input("Do you want to overwrite the file? (y/n): ")
            if overwrite.lower() != 'y':
                print("File not copied.")
                return

        try:
            shutil.copy(source_path, destination_path)
            print("File copied successfully!")
        except IOError as e:
            print(f"Unable to copy file. {e}")


    def rar_compress_to_folderName_selected(self):
        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            if self.absolutePath:
                from ccMethod.ccMethod import CompressTool
                print('self.absolutePath:',self.absolutePath)
                CompressTool.compress_with_winrar(self.absolutePath)

        if not selected_indexes:
            return



    def create_shortcuts(self):
        # # 创建快捷键
        # shortcut_open = QShortcut(QKeySequence(Qt.Key_Enter), self)  # 复制
        # # 绑定快捷键到槽函数
        # shortcut_open.activated.connect(self.open_selected)
        # 创建快捷键
        shortcut_copy = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self)  # 复制
        # 绑定快捷键到槽函数
        shortcut_copy.activated.connect(self.copy_selected)
        # 创建快捷键
        shortcut_paste = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_V), self)  # 复制
        # 绑定快捷键到槽函数
        shortcut_paste.activated.connect(self.paste_selected)
        # 创建快捷键
        shortcut_cut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_cut.activated.connect(self.cut_selected)
        # 创建快捷键
        shortcut_delete = QShortcut(QKeySequence(Qt.Key_Delete), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_delete.activated.connect(self.delete_selected)

    # 在PyQt5中，如果您在QListView中按下回车键，通常不会自动触发任何操作。QShortcut类主要用于全局快捷键而不是特定于某个小部件的快捷键。
    # 如果您想要在按下回车键时触发操作，您可以使用QListView的keyPressEvent事件来捕获回车键并执行所需的操作。
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 在这里执行按下回车键后的操作
            print("Enter key pressed!")
            self.open_selected()
        else:
            print("cc")
            super().keyPressEvent(event)



    def mouseDoubleClickEvent0(self, event):
        '''重写此方法可以实现根据点击的区域做不同操作,还不太好用'''
        index = self.indexAt(event.pos())
        item_rect = self.visualRect(index)

        if index.isValid():
            click_position = ""

            # 判断点击的位置是图标还是名称
            if event.pos().x() < item_rect.left() + item_rect.width() / 2:
                click_position = "icon"
            else:
                click_position = "name"

            if click_position == "icon":
                file_path = self.model().filePath(index)
                file_type = "folder" if self.model().isDir(index) else "file"

                if file_type == "folder":
                    print("folder")
                    # open_folder(file_path)
                elif file_type == "file":
                    print("file")
                    # rename_file(file_path)
            elif click_position == "name":
                print("name")
                file_path = self.model().filePath(index)
                # rename_file(file_path)

        super().mouseDoubleClickEvent(event)


    def mousePressEvent0(self, event):
        '''重写此方法可以实现根据点击的区域做不同操作，还不太好用'''
        index = self.indexAt(event.pos())
        item_rect = self.visualRect(index)

        if index.isValid():
            click_position = ""

            # 判断点击的位置是图标还是名称
            if event.pos().x() < item_rect.left() + item_rect.width() / 2:
                click_position = "icon"
            else:
                click_position = "name"

            if click_position == "icon":
                file_path = self.model().filePath(index)
                file_type = "folder" if self.model().isDir(index) else "file"

                if file_type == "folder":
                    print("folder")

                elif file_type == "file":
                    print("file")

            elif click_position == "name":
                print("name")
                file_path = self.model().filePath(index)
                print('file_path:',file_path)
                old_name = self.currentIndex().data()
                if old_name:
                    print('self.path:',self.path,"old_name:",old_name)
                    self.absolutePath = os.path.join(self.path, old_name)
                    dialog = RenameDialog(old_name)
                    if dialog.exec_() == QDialog.Accepted:
                        new_name = dialog.rename_edit.text()
                        if new_name:
                            # print("new_name:",new_name)
                            new_name_full_path = os.path.join(self.path, new_name)
                            os.rename(self.absolutePath, new_name_full_path)




        # super().mouseDoubleClickEvent(event)
        super(ListViewFile, self).mousePressEvent(event)



class ListViewFileForList(QListView):
    def __init__(self,list_path):
        super().__init__()
        self.list_path = list_path
        # 加载文件夹内容
        self.model = QStandardItemModel()

        # folder_model.setRootPath(path)
        self.setModel(self.model)
        # self.setRootIndex(folder_model.index(path))
        for each in self.list_path:
            self.model.appendRow(QStandardItem(each))


        # self.setIconSize(QSize(64, 64))
        # self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        # self.setGridSize(QSize(120, 120))  # 设置图标的固定宽度和高度
        # self.setSpacing(20)  # 设置图标之间的间距




        # 创建上下文菜单
        self.context_menu = QMenu(self)
        # 当鼠标悬停在菜单项上时，项目的文本会消失。这个问题可能是由于菜单项的样式造成的，所以要设置下
        self.context_menu.setStyleSheet("QMenu::item:selected { color: black; }")


        # 创建菜单项
        self.open_action = QAction("打开", self)
        self.copy_action = QAction("复制", self)
        self.cut_action = QAction("剪切", self)
        self.delete_action = QAction("删除", self)
        self.rename_action = QAction("重命名", self)



        # 添加菜单项到上下文菜单
        self.context_menu.addAction(self.open_action)
        self.context_menu.addAction(self.copy_action)
        self.context_menu.addAction(self.cut_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addAction(self.rename_action)



        # 设置上下文菜单策略
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.open_action.triggered.connect(self.open_selected)
        self.copy_action.triggered.connect(self.copy_selected)
        self.cut_action.triggered.connect(self.cut_selected)
        self.delete_action.triggered.connect(self.delete_selected)
        self.rename_action.triggered.connect(self.rename_selected)



        # 添加快捷键
        self.create_shortcuts()

    def contextMenuEvent(self, event: QContextMenuEvent):
        pass
        #本方法是在右击后才发生的

    def customizeContextMenu(self):
        # 在这里执行自定义操作，例如更改菜单项、添加额外的菜单项等
        print("Customizing context menu...")
        # 清空菜单项
        self.context_menu.clear()



        # 创建菜单项
        self.open_action = QAction("打开", self)
        self.copy_action = QAction("复制", self)
        self.cut_action = QAction("剪切", self)
        self.delete_action = QAction("删除", self)
        self.rename_action = QAction("重命名", self)



        # 添加菜单项到上下文菜单
        self.context_menu.addAction(self.open_action)
        self.context_menu.addAction(self.copy_action)
        self.context_menu.addAction(self.cut_action)
        self.context_menu.addAction(self.delete_action)
        self.context_menu.addAction(self.rename_action)


        self.open_action.triggered.connect(self.open_selected)
        self.copy_action.triggered.connect(self.copy_selected)
        self.cut_action.triggered.connect(self.cut_selected)
        self.delete_action.triggered.connect(self.delete_selected)
        self.rename_action.triggered.connect(self.rename_selected)



        # 根据选中的项目动态设置右击快捷菜单








    def show_context_menu(self, position):
        # 在显示上下文菜单之前执行自定义操作,每次右击时都会调用一下
        self.customizeContextMenu()

        # 设置菜单项样式
        self.context_menu.setStyleSheet("QMenu::item:selected { background-color: black; }")


        action = self.context_menu.exec_(self.mapToGlobal(position))
        if action is not None:
            # 在这里处理所选菜单项的操作
            print("Selected action:", action.text())


    def set_path(self,path):
        pass
        print("更新path",path)
        self.path = path






    def open_selected(self):
        print("open:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = text
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pass
                url = QUrl.fromLocalFile(self.absolutePath)
                QDesktopServices.openUrl(url)

        if not selected_indexes:
            return


    def copy_selected(self):
        print("copy:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.absolutePath)

        if not selected_indexes:
            return


    def cut_selected(self):
        print("cut:")

        selected_indexes = self.selectedIndexes()
        # print(selected_indexes)
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                gl.cutFlag = True
                # 将文件路径设置到剪贴板
                clipboard = qApp.clipboard()
                clipboard.setText(self.absolutePath, QClipboard.Clipboard)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('Files have been cut.')
                msg_box.exec_()

                print('gl.cutFlag', gl.cutFlag)

        if not selected_indexes:
            return




    def delete_selected(self):
        print("delete:")

        selected_indexes = self.selectedIndexes()
        for index in selected_indexes:
            text = index.data(Qt.DisplayRole)
            self.absolutePath = os.path.join(self.path,text)
            print("选中项的路径:", self.absolutePath)
            if self.absolutePath:
                pathStandard = Path(self.absolutePath).resolve().as_posix()
                pathStandard = pathStandard.replace('/','\\')

                print('pathStandard:',pathStandard)
                # 将文件移动到回收站
                send2trash.send2trash(pathStandard)

                # # 下面方法是永久删除
                # if os.path.isfile(self.absolutePath):
                #     os.remove(self.absolutePath)
                # if os.path.isdir(self.absolutePath):
                #     shutil.rmtree(self.absolutePath)

                # 显示消息框
                msg_box = QMessageBox(self)
                msg_box.setText('已删除！')
                msg_box.exec_()



        if not selected_indexes:
            return

    def rename_selected(self):
        index = self.currentIndex()
        old_name = index.data()
        # print("old_name:", old_name)
        self.absolutePath = os.path.join(self.path, old_name)
        dialog = RenameDialog(old_name)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.rename_edit.text()
            if new_name:
                # print("new_name:",new_name)
                new_name_full_path = os.path.join(self.path,new_name)
                os.rename(self.absolutePath,new_name_full_path)
                # print('文件重命名成功！')













    def copy_file(source_path, destination_path):
        if os.path.exists(destination_path):
            print("Destination file already exists.")
            overwrite = input("Do you want to overwrite the file? (y/n): ")
            if overwrite.lower() != 'y':
                print("File not copied.")
                return

        try:
            shutil.copy(source_path, destination_path)
            print("File copied successfully!")
        except IOError as e:
            print(f"Unable to copy file. {e}")






    def create_shortcuts(self):
        # # 创建快捷键
        # shortcut_open = QShortcut(QKeySequence(Qt.Key_Enter), self)  # 复制
        # # 绑定快捷键到槽函数
        # shortcut_open.activated.connect(self.open_selected)
        # 创建快捷键
        shortcut_copy = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_C), self)  # 复制
        # 绑定快捷键到槽函数
        shortcut_copy.activated.connect(self.copy_selected)

        # 创建快捷键
        shortcut_cut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_X), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_cut.activated.connect(self.cut_selected)
        # 创建快捷键
        shortcut_delete = QShortcut(QKeySequence(Qt.Key_Delete), self)  # 剪切
        # 绑定快捷键到槽函数
        shortcut_delete.activated.connect(self.delete_selected)

    # 在PyQt5中，如果您在QListView中按下回车键，通常不会自动触发任何操作。QShortcut类主要用于全局快捷键而不是特定于某个小部件的快捷键。
    # 如果您想要在按下回车键时触发操作，您可以使用QListView的keyPressEvent事件来捕获回车键并执行所需的操作。
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 在这里执行按下回车键后的操作
            print("Enter key pressed!")
            self.open_selected()
        else:
            print("cc")
            super().keyPressEvent(event)







class FileNameDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # 获取文件名和图标
        file_model = index.data(Qt.DisplayRole)
        file_icon = index.data(Qt.DecorationRole)

        # 获取绘制区域和边距
        rect = option.rect
        margins = 4

        # 绘制背景
        painter.save()
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())

        # 绘制图标
        icon_rect = QRect(rect.x(), rect.y(), rect.width(), rect.height() - 20)  # 调整图标区域的高度,最后数字越大，图标越小
        file_icon.paint(painter, icon_rect, Qt.AlignCenter, QIcon.Normal, QIcon.Off)

        # 绘制文件名，自动换行且居中对齐
        text_rect = QRect(rect.x(), rect.y() + icon_rect.height(), rect.width(), rect.height() - icon_rect.height())
        doc = QTextDocument()
        doc.setDefaultStyleSheet("p { margin: 0; text-align: center; }")
        doc.setHtml('<p>{}</p>'.format(file_model))
        doc.setTextWidth(text_rect.width())
        layout = doc.documentLayout()
        painter.translate(text_rect.topLeft())
        layout.draw(painter, QAbstractTextDocumentLayout.PaintContext())
        painter.restore()


class RenameDialog(QDialog):
    def __init__(self, old_name):
        super().__init__()
        self.setWindowTitle('重命名')
        self.layout = QVBoxLayout()

        self.rename_edit = QLineEdit(self)
        self.rename_edit.setText(old_name)
        self.rename_edit.selectAll()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.rename_edit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

