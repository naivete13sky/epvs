# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1149, 801)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidgetVS = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidgetVS.setGeometry(QtCore.QRect(10, 160, 901, 581))
        self.tableWidgetVS.setObjectName("tableWidgetVS")
        self.tableWidgetVS.setColumnCount(0)
        self.tableWidgetVS.setRowCount(0)
        self.textBrowserMain = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowserMain.setGeometry(QtCore.QRect(920, 160, 221, 581))
        self.textBrowserMain.setObjectName("textBrowserMain")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(50, 10, 861, 141))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayoutInput = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayoutInput.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutInput.setObjectName("horizontalLayoutInput")
        self.groupBoxJobA = QtWidgets.QGroupBox(self.layoutWidget)
        self.groupBoxJobA.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBoxJobA.setObjectName("groupBoxJobA")
        self.pushButtonInputA = QtWidgets.QPushButton(self.groupBoxJobA)
        self.pushButtonInputA.setGeometry(QtCore.QRect(40, 50, 81, 31))
        self.pushButtonInputA.setObjectName("pushButtonInputA")
        self.pushButtonImportA = QtWidgets.QPushButton(self.groupBoxJobA)
        self.pushButtonImportA.setGeometry(QtCore.QRect(180, 50, 81, 31))
        self.pushButtonImportA.setObjectName("pushButtonImportA")
        self.labelStatusJobA = QtWidgets.QLabel(self.groupBoxJobA)
        self.labelStatusJobA.setGeometry(QtCore.QRect(10, 110, 251, 16))
        self.labelStatusJobA.setObjectName("labelStatusJobA")
        self.horizontalLayoutInput.addWidget(self.groupBoxJobA)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutInput.addItem(spacerItem)
        self.verticalLayoutInput = QtWidgets.QVBoxLayout()
        self.verticalLayoutInput.setObjectName("verticalLayoutInput")
        self.pushButtonVS = QtWidgets.QPushButton(self.layoutWidget)
        self.pushButtonVS.setObjectName("pushButtonVS")
        self.verticalLayoutInput.addWidget(self.pushButtonVS)
        self.comboBoxVSMethod = QtWidgets.QComboBox(self.layoutWidget)
        self.comboBoxVSMethod.setObjectName("comboBoxVSMethod")
        self.comboBoxVSMethod.addItem("")
        self.comboBoxVSMethod.addItem("")
        self.verticalLayoutInput.addWidget(self.comboBoxVSMethod)
        self.horizontalLayoutInput.addLayout(self.verticalLayoutInput)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutInput.addItem(spacerItem1)
        self.groupBoxJobB = QtWidgets.QGroupBox(self.layoutWidget)
        self.groupBoxJobB.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBoxJobB.setObjectName("groupBoxJobB")
        self.pushButtonImportB = QtWidgets.QPushButton(self.groupBoxJobB)
        self.pushButtonImportB.setGeometry(QtCore.QRect(170, 50, 81, 31))
        self.pushButtonImportB.setObjectName("pushButtonImportB")
        self.pushButtonInputB = QtWidgets.QPushButton(self.groupBoxJobB)
        self.pushButtonInputB.setGeometry(QtCore.QRect(30, 50, 81, 31))
        self.pushButtonInputB.setObjectName("pushButtonInputB")
        self.labelStatusJobB = QtWidgets.QLabel(self.groupBoxJobB)
        self.labelStatusJobB.setGeometry(QtCore.QRect(10, 110, 251, 16))
        self.labelStatusJobB.setObjectName("labelStatusJobB")
        self.horizontalLayoutInput.addWidget(self.groupBoxJobB)
        self.horizontalLayoutInput.setStretch(0, 4)
        self.horizontalLayoutInput.setStretch(1, 1)
        self.horizontalLayoutInput.setStretch(2, 2)
        self.horizontalLayoutInput.setStretch(3, 1)
        self.horizontalLayoutInput.setStretch(4, 4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1149, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "悦谱转图比对系统 EPVS-V1.0"))
        self.groupBoxJobA.setTitle(_translate("MainWindow", "料号A"))
        self.pushButtonInputA.setText(_translate("MainWindow", "Input"))
        self.pushButtonImportA.setText(_translate("MainWindow", "Import"))
        self.labelStatusJobA.setText(_translate("MainWindow", "状态："))
        self.pushButtonVS.setText(_translate("MainWindow", "比图"))
        self.comboBoxVSMethod.setItemText(0, _translate("MainWindow", "方案1：G比图"))
        self.comboBoxVSMethod.setItemText(1, _translate("MainWindow", "方案2：悦谱比图"))
        self.groupBoxJobB.setTitle(_translate("MainWindow", "料号B"))
        self.pushButtonImportB.setText(_translate("MainWindow", "Import"))
        self.pushButtonInputB.setText(_translate("MainWindow", "Input"))
        self.labelStatusJobB.setText(_translate("MainWindow", "状态："))
