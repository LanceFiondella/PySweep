from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView, QTabWidget
from PyQt5.QtCore import Qt
import PyQt5
from core import utils, models, defect_injection
import sys, math
import matplotlib
import numpy as np
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from gui.mode_template import ModeTabWidget
from core.models import WeibullNumpy as Weibull


class ModeCTabWidget(ModeTabWidget):
    def __init__(self, globalData):
        super().__init__(globalData)
        self.globalData = globalData
        self.modex = 'modeC'
        self.tableWidget.setHorizontalHeaderLabels(['Phase Name','Defects Detected/\nKSLOC'])
        self.tableWidget.cellChanged.connect(self.tableChanged)
        self.dataChanged = False

    def addComputationButtons(self):
        buttonGroupBox = QGroupBox("Computation", self)
        buttonLayout = QVBoxLayout()
        buttons = []
        
        latentErrorLabel = QLabel('Enter Latent Defect :')
        self.latentErrorBox = QLineEdit()
        self.latentErrorBox.setText('1.32')
        self.computeButton = QPushButton('Compute')
        self.computeButton.setToolTip('Starts the computation')
        self.computeButton.clicked.connect(self.compute)
        buttons.append(latentErrorLabel)
        buttons.append(self.latentErrorBox)
        buttons.append(self.computeButton)
        for button in buttons:
            buttonLayout.addWidget(button)
        
        buttonLayout.addStretch(1)
        buttonGroupBox.setLayout(buttonLayout)
        return buttonGroupBox
    
    def compute(self):
        data = self.globalData.input[self.modex]
        #data['dp'] = self.getTableData()
        #try:
        if 1:
            if self.dataChanged:
                data['ld'] = float(self.latentErrorBox.text())
                self.di = defect_injection.DefectInjection(data)
                self.resultDialog = ModeCResultsDialog(self.di)
            else:
                self.resultDialog = ModeCResultsDialog(self.di)
        #except:
        #    print("Unexpected error:", sys.exc_info()[0])
        #    QMessageBox.about(self, 'Error','Invalid or missing Lantent Error value')
        
        
        print("Compute!")

   
    def populateTable(self):
        #self.setGlobalData(data)
        col1Name = 'names'
        col2Name = 'values'
        data = self.globalData.input[self.modex]
        self.tableWidget.setRowCount(len(data[col1Name]))
        for i in range(len(data[col1Name])):
            tVec = QTableWidgetItem()
            kVec = QTableWidgetItem()
            tVec.setText(str(data[col1Name][i]))
            kVec.setText(str(data[col2Name][i]))
            self.tableWidget.setItem(i,0,tVec)
            self.tableWidget.setItem(i,1,kVec)

    def tableChanged(self, x, y):
        print("Table data changed! at : {}, {}".format(x, y))
        self.globalData.input[self.modex]['dp'] = self.getTableData()
        self.dataChanged = True

    def getTableData(self):
        data = {}
        names = []
        values = []
        for i in range(self.tableWidget.rowCount()):
            try:
                if self.tableWidget.item(i,0) != None and self.tableWidget.item(i,1) != None:
                    names.append(self.tableWidget.item(i,0).text())
                    values.append(float(self.tableWidget.item(i,1).text()))
                    #data.append((self.tableWidget.item(i,0).text(), float(self.tableWidget.item(i,1).text())))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass
        data['names'] = names
        data['values'] = values
        print(data)
        return data



class ModeCResultsDialog(QWidget):
    def __init__(self, di, parent=None):
        super(ModeCResultsDialog, self).__init__(parent)
        self.di = di
        layout = QVBoxLayout(self)
        dl_layout = self.genDataLabels()
        layout.addLayout(dl_layout)

        self.tabWidget = QTabWidget()
        self.defectsInPhaseTab = QWidget()
        self.defectsInPhaseTab.setLayout(self.genLeftPlot())
        self.phaseInjectionTab = QWidget()
        self.phaseInjectionTab.setLayout(self.genRightPlot())
        self.leakageByPhaseTab = QWidget()
        self.leakageByPhaseTab.setLayout(self.genLeakageRatePlot())
        self.finalComputationTab = QWidget()
        self.finalComputationTab.setLayout(self.genFinalCompTable())

        self.tabWidget.addTab(self.defectsInPhaseTab, "Defects/KSLOC Injected or Discovered in Phase")
        self.tabWidget.addTab(self.phaseInjectionTab,"Phase Injection/Detection/Leakage")
        self.tabWidget.addTab(self.genIntermediateTab(), "Intermediate Results")
        self.tabWidget.addTab(self.leakageByPhaseTab,"Percentage Leakage by Phase")
        self.tabWidget.addTab(self.genUpdatedIntermediateTab(), 'Updated Intermediate Calculations')
        self.tabWidget.addTab(self.finalComputationTab,"Final Computation")

        
        layout.addWidget(self.tabWidget)
        self.setWindowTitle('SwEET - Mode C Results')
        layout.setAlignment(Qt.AlignTop)
        self.setGeometry(400,400,1000, 800)
        self.show()

    def genUpdatedIntermediateTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        labels = [ "<b> Updated Estimate of latency: </b> {:.6f}".format(self.di.UEL),
                "<b>Number of Relative Defects : </b> {:.6f}".format(self.di.RE2)
                ]
        for label in labels:
            l = QLabel()
            l.setText(label)
            layout.addWidget(l)

        data = [self.di.UDF, self.di.UDR, self.di.UPLD, self.di.UENID]

        tableWidget = QTableWidget()
        tableWidget.setColumnCount(self.di.num_phases)
        #tableWidget.setRowCount(len(data))
        tableWidget.setHorizontalHeaderLabels(self.di.names)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            tableWidget.insertRow(row)
            for col in range(len(tableItemRow)):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget.setItem(row, col, tableItemRow[col])

        tableWidget.setVerticalHeaderLabels(['Updated Total Defects found', 'Updated rate of defects found', 
                                            'Updated proportion of latent defects per phase', 
                                            'Updated total estimated number of injected defects by phase']) 
        layout.addWidget(tableWidget)
        widget.setLayout(layout)
        return widget


    def genIntermediateTab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        labels = [ "<b> Average Efficiency: </b> {:.6f}".format(self.di.AE),
                "<b>Initial Estimate of latency : </b> {:.6f}".format(self.di.IEL)
                ]
        for label in labels:
            l = QLabel()
            l.setText(label)
            layout.addWidget(l)

        data = [self.di.DF, self.di.DR, self.di.PLD, self.di.ENID]

        tableWidget = QTableWidget()
        tableWidget.setColumnCount(self.di.num_phases)
        #tableWidget.setRowCount(len(data))
        tableWidget.setHorizontalHeaderLabels(self.di.names)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            tableWidget.insertRow(row)
            for col in range(len(tableItemRow)):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget.setItem(row, col, tableItemRow[col])

        tableWidget.setVerticalHeaderLabels(['Latent Defects', 'Defect Rate per Phase', 
                                            'Proportion of latent defects per phase', 
                                            'Estimated number of injected defects per phase']) 
        layout.addWidget(tableWidget)
        widget.setLayout(layout)
        return widget

    def genFinalCompTable(self):
        layout = QVBoxLayout()

        #Generate final outputs
        labels = ["<b>Overall Defect Discovery Efficiency:</b> {:.6f}%".format(self.di.ODDE*100), 
                "<b>Initial Average Phase Defect Discovery Efficiency:</b> {:.6f}%".format(self.di.ADE*100),
                "<b>Average Phase Defect Discovery Efficiency:</b> {:.6f}%".format(self.di.APDE*100),
                "<b>Initial Average Phase Defect Leakage:</b> {:.6f}%".format(self.di.ADL*100),
                "<b>Average Phase Defect Leakage:</b> {:.6f}%".format(self.di.APDL*100),
                "<b>Latent Defects as % of Total Defects Injected:</b> {:.6f}%".format(self.di.LDPD*100),
                "<b>Total Defects Injected / KSLOC:</b> {:.6f}".format(self.di.TDI),
                "<b>Latent Defects / KSLOC:</b> {:.6f}".format(self.di.LD)
                ]

        for label in labels:
            l = QLabel()
            l.setText(label)
            layout.addWidget(l)

        #Generate table
        tableWidget = QTableWidget()
        tableWidget.setColumnCount(1+self.di.num_phases)
        tableWidget.setHorizontalHeaderLabels(['Total Injected']+self.di.names)
        
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = self.di.di_matrix

        #Adding Injection Matrix
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases + 1)]
            tableWidget.insertRow(row)
            for col in range(len(tableItemRow)):
                if col == 0:
                    tableItemRow[col].setText('{:.6f}'.format(self.di.I2[row]))
                else:
                    tableItemRow[col].setText('{:.6f}'.format(data[row, col-1]))
                tableWidget.setItem(row, col, tableItemRow[col])

        #Adding other stats
        tableWidget.insertRow(len(data)) #Seperates data
        curr_row = len(data) + 1
        calc = np.append(self.di.TDI, self.di.D2)
        user_ip = np.append(self.di.total_defects, self.di.detection_profile)
        rel_error = calc-user_ip
        data = [calc, user_ip, rel_error]

        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases + 1)]
            tableWidget.insertRow(curr_row + row)
            for col in range(len(tableItemRow)):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget.setItem(curr_row + row, col, tableItemRow[col])

        tableWidget.setVerticalHeaderLabels(self.di.names + [' ', 'Calculated', 'User Input Defects', 'Relative Defect'])
        layout.addWidget(tableWidget)
        return layout

    def genDataLabels(self):
        layout = QHBoxLayout()
        labels = []
        
        labels.append(QLabel("<h3><b>Total Detected:</b> {:.2f}</h3>".format(self.di.total_defects)))
        labels.append(QLabel("<h3><b>Total Injected:</b> {:.2f}</h3>".format(self.di.TDI)))
        labels.append(QLabel("<h3><b>Latent Defect:</b> {:.2f}</h3>".format(self.di.latent_defects)))
        labels.append(QLabel("<h3><b>Peak at Phase:</b> {:.2f}</h3>".format(self.di.profile_peak)))
        for label in labels:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(label)
        layout.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(20)
        return layout

    def genRightPlot(self):
        #Figure definition
        fig2 = plt.figure()
        
        plt.grid(True)
        canvas2 = FigureCanvas(fig2)
        toolbar2 = NavigationToolbar(canvas2, self)
        ax2 = fig2.add_subplot(111)
        ax2.set_xticklabels([""] + self.di.names) #Shifting names 
        ax2.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.2, color='b', label="Injected")
        ax2.bar([i+1 for i in range(self.di.num_phases)], self.di.DDR, width=0.2, color='r', label="Detected")
        ax2.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.LEAK, width=0.2, color='g', label="Leakage")
        ax2.set_xlabel("Phases")
        ax2.set_ylabel("Defects")
        ax2.set_title("Phase Injection/Detection/Leakage")
        ax2.legend()
        
        canvas2.draw()

        #Table definition
        tableWidget2 = QTableWidget()
        tableWidget2.setRowCount(3)
        tableWidget2.setColumnCount(self.di.num_phases)
        tableWidget2.setHorizontalHeaderLabels(self.di.names)
        tableWidget2.setVerticalHeaderLabels(['Injected','Detected', 'Leakage'])
        tableWidget2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = [self.di.I2, self.di.DDR, self.di.LEAK]
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            for col in range(self.di.num_phases):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget2.setItem(row, col, tableItemRow[col])



        layoutfig2 = QVBoxLayout()
        layoutfig2.addWidget(toolbar2)
        layoutfig2.addWidget(canvas2, 1)
        layoutfig2.addWidget(tableWidget2)
        layoutfig2.setAlignment(tableWidget2, Qt.AlignBottom)
        plt.tight_layout()
        return layoutfig2

    def genLeftPlot(self):
        #figure def
        fig = plt.figure()
        #
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.set_xticklabels([""] + self.di.names) #Shifting names 
        ax1.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.4, color='b', label="Injected")
        ax1.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.D2, width=0.4, color='r', label="Detected")
        ax1.set_xlabel("Phases")
        ax1.set_ylabel("Defects")
        ax1.set_title("Defects/KSLOC Injected or discovered in phase")
        ax1.legend()
        canvas.draw()

        #table def
        tableWidget = QTableWidget()
        tableWidget.setRowCount(2)
        tableWidget.setColumnCount(self.di.num_phases)
        tableWidget.setHorizontalHeaderLabels(self.di.names)
        tableWidget.setVerticalHeaderLabels(['Injected','Detected'])
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = [self.di.I2, self.di.D2]
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            for col in range(self.di.num_phases):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget.setItem(row, col, tableItemRow[col])

        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        layoutfig.addWidget(tableWidget)
        layoutfig.setAlignment(tableWidget, Qt.AlignBottom)
        plt.tight_layout()
        return layoutfig

    def genLeakageRatePlot(self):
        fig = plt.figure()
        #
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.set_xticklabels([""] + self.di.names) #Shifting names 
        ax1.bar([i+1 for i in range(self.di.num_phases)], self.di.LRATE*100, width=0.4, color='b', label="Leakage Rate by Phase")
        
        ax1.set_xlabel("Phases")
        ax1.set_ylabel("Percentage of Defects")
        ax1.set_title("Leakage Rate by phase")
        #ax1.legend()
        canvas.draw()

        #table def
        print(self.di.EFC)
        print(self.di.EFV)
        data = [self.di.LRATE*100.0, self.di.EFC*100.0, self.di.EFV*100.0]
        tableWidget1 = QTableWidget()
        tableWidget1.setRowCount(len(data))
        tableWidget1.setColumnCount(self.di.num_phases)
        tableWidget1.setHorizontalHeaderLabels(self.di.names)
        tableWidget1.setVerticalHeaderLabels(['Percentage\nof Defects', "Efficiency", "Effectiveness"])
        tableWidget1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        for row in range(len(data)):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            for col in range(self.di.num_phases):
                tableItemRow[col].setText('{:.6f}'.format(data[row][col]))
                tableWidget1.setItem(row, col, tableItemRow[col])

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas, 1)
        layout.addWidget(tableWidget1)
        layout.setAlignment(tableWidget1, Qt.AlignBottom)
        plt.tight_layout()
        return layout