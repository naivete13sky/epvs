import os
import sys

from ui.ussd import Ui_MainWindow
from PyQt5.QtWidgets import *
from epkernel import GUI

class Ussd(QMainWindow,Ui_MainWindow):
    from config_ep.epcam import EPCAM
    epcam = EPCAM()


    def __init__(self):
        super(Ussd,self).__init__()
        self.setupUi(self)


        # 设置表格大小
        self.tableWidgetGerber.setRowCount(0)
        self.tableWidgetGerber.setColumnCount(10)
        # 设置列标签
        column_labels = ["文件名", "类型", "省零", "整数", "小数", "单位", "工具单位","悦谱转图结果","第三方转图结果","第三方比图结果","说明"]
        self.tableWidgetGerber.setHorizontalHeaderLabels(column_labels)


        self.pushButtonSelectGerber.clicked.connect(self.selectGerber)
        self.pushButtonLoadEPCAM.clicked.connect(self.loadEPCAM)
        self.pushButtonIdentify.clicked.connect(self.identify)
        self.pushButtonTranslateEP.clicked.connect(self.translateEP)

    def selectGerber(self):
        # print(123)
        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "/")



        if folder_path:
            self.lineEditGerberFolderPath.setText(folder_path)
            jobName = folder_path.split("/")[-1]
            self.lineEditJobName.setText(jobName)
            self.lineEditStep.setText("orig")

            # print('返回指定目录下的所有文件和目录名：', os.listdir(folder_path))
            file_list = os.listdir(folder_path)
            file_count = len(file_list)
            # print(file_count)
            self.tableWidgetGerber.setRowCount(file_count)
            for each in range(file_count):
                self.tableWidgetGerber.setItem(each, 0, QTableWidgetItem(file_list[each]))


    def loadEPCAM(self):
        print("ready to load EPCAM")
        self.epcam.init()
        self.pushButtonLoadEPCAM.setText("已加载EPCAM")
        self.pushButtonLoadEPCAM.setStyleSheet("background-color: green")
        print("Finish load EPCAM")

    def identify(self):
        print("ready to identify")
        from epkernel import Input
        for row in range(self.tableWidgetGerber.rowCount()):
            # print(self.tableWidgetGerber.item(row, 0).text())
            result_each_file_identify = Input.file_identify(os.path.join(self.lineEditGerberFolderPath.text(),self.tableWidgetGerber.item(row, 0).text()))
            print(result_each_file_identify)
            # print(result_each_file_identify["format"])
            self.tableWidgetGerber.setItem(row, 1, QTableWidgetItem(result_each_file_identify["format"]))
            self.tableWidgetGerber.setItem(row, 2, QTableWidgetItem(result_each_file_identify["parameters"]['zeroes_omitted']))
            self.tableWidgetGerber.setItem(row, 3, QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_integer'])))
            self.tableWidgetGerber.setItem(row, 4,QTableWidgetItem(str(result_each_file_identify["parameters"]['Number_format_decimal'])))
            self.tableWidgetGerber.setItem(row, 5,QTableWidgetItem(result_each_file_identify["parameters"]['units']))
            self.tableWidgetGerber.setItem(row, 6,QTableWidgetItem(result_each_file_identify["parameters"]['tool_units']))

        # 设置固定宽度为多少像素
        self.tableWidgetGerber.setColumnWidth(0, 200)
        self.tableWidgetGerber.setColumnWidth(1, 80)
        self.tableWidgetGerber.setColumnWidth(2, 70)
        self.tableWidgetGerber.setColumnWidth(3, 50)
        self.tableWidgetGerber.setColumnWidth(4, 50)
        self.tableWidgetGerber.setColumnWidth(5, 50)
        self.tableWidgetGerber.setColumnWidth(6, 50)
        # 设置自适应宽度
        header = self.tableWidgetGerber.horizontalHeader()
        header.setSectionResizeMode(9, QHeaderView.Stretch)

    def viewLayer(self,id):
        pass
        print("layer id:",id)
        jobName = self.lineEditJobName.text()
        step = self.lineEditStep.text()
        layerName = self.tableWidgetGerber.item(int(id),0).text().lower()
        print("layerName:",layerName)
        GUI.show_layer(jobName, step, layerName)

    # 列表内添加按钮
    def buttonForRow(self, id):
        widget = QWidget()
        # 修改
        updateBtn = QPushButton('修改')
        updateBtn.setStyleSheet(''' text-align : center;
                                          background-color : NavajoWhite;
                                          height : 30px;
                                          border-style: outset;
                                          font : 13px  ''')

        updateBtn.clicked.connect(lambda: self.updateTable(id))

        # 查看
        viewBtn = QPushButton('查看')
        viewBtn.setStyleSheet(''' text-align : center;
                                  background-color : DarkSeaGreen;
                                  height : 30px;
                                  border-style: outset;
                                  font : 13px; ''')

        viewBtn.clicked.connect(lambda: self.viewLayer(id))

        # 删除
        deleteBtn = QPushButton('删除')
        deleteBtn.setStyleSheet(''' text-align : center;
                                    background-color : LightCoral;
                                    height : 30px;
                                    border-style: outset;
                                    font : 13px; ''')

        hLayout = QHBoxLayout()
        # hLayout.addWidget(updateBtn)
        hLayout.addWidget(viewBtn)
        # hLayout.addWidget(deleteBtn)
        hLayout.setContentsMargins(5, 2, 5, 2)
        widget.setLayout(hLayout)
        return widget


    def translateEP(self):
        from epkernel.Edition import Job,Matrix

        print("ready to traslateEp")
        from epkernel import Input,BASE


        jobName = self.lineEditJobName.text()
        step = self.lineEditStep.text()

        # 创建一个空料号
        Job.create_job(jobName)

        # 创建一个空step
        Matrix.create_step(jobName, step)


        # 开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        offsetFlag = False
        offset1 = 0
        offset2 = 0
        for row in range(self.tableWidgetGerber.rowCount()):
            each_file = self.tableWidgetGerber.item(row, 0).text()
            print(each_file)
            result_each_file_identify = Input.file_identify(os.path.join(self.lineEditGerberFolderPath.text(), each_file))
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']
            print("orig min_1,min_2:", min_1, ":", min_2)
            # 如果是孔的话，可能要调整参数的。
            try:
                if result_each_file_identify["format"] == "Excellon2":
                    print('need to set the para for drill excellon2'.center(190, '-'))
                    print('原来导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                    result_each_file_identify['parameters']['zeroes_omitted'] = self.tableWidgetGerber.item(row,2).text()
                    result_each_file_identify['parameters']['Number_format_integer'] = int(self.tableWidgetGerber.item(row,3).text())
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(self.tableWidgetGerber.item(row,4).text())
                    result_each_file_identify['parameters']['units'] = self.tableWidgetGerber.item(row, 5).text()
                    result_each_file_identify['parameters']['tool_units'] = self.tableWidgetGerber.item(row,6).text()
                    print('现在导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                if result_each_file_identify["format"] == "Gerber274x":
                    print("我是Gerber274x")
                    print('orig para'.center(190, '-'))
                    print(result_each_file_identify)
                    print("offsetFlag:", offsetFlag)
                    if (offsetFlag == False) and (
                            abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
                        # print("hihihi2:",each_file)
                        offset1 = min_1
                        offset2 = min_2
                        offsetFlag = True
                    result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1,
                                                                                 'second': offset2}
                    print('now para'.center(190, '-'))
                    print(result_each_file_identify)

            except Exception as e:
                print(e)
                print("有异常情况发生")
            translateResult = Input.file_translate(path=os.path.join(self.lineEditGerberFolderPath.text(), each_file), job=jobName, step='orig', layer=each_file,
                                 param=result_each_file_identify['parameters'])
            # print("translateResult:",translateResult)
            if translateResult == True:
                # self.tableWidgetGerber.setItem(row, 7,QTableWidgetItem("已转"))
                self.tableWidgetGerber.setCellWidget(row, 7, self.buttonForRow(str(row)))

        # GUI.show_layer(jobName, "orig", "top")
        # 保存料号
        BASE.save_job_as(jobName, r"C:\temp")





    def translateG(self):
        pass
