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


class Mode4TabWidget(QWidget):
    """
    This class describes the placement of widgets in the Mode 1 tab
    """
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Phase Name','Defects Detected/\nKSLOC'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        layout.addWidget(self.tableWidget)

        layout.addWidget(self.tableWidget,1,1)

        self.buttonPanel = QVBoxLayout()
        self.buttonPanel.addWidget(self.addDataButtons())
        self.buttonPanel.addWidget(self.addExternalDataButtons())
        self.buttonPanel.addWidget(self.addComputationButtons())
        layout.addLayout(self.buttonPanel,1,2)

    def addExternalDataButtons(self):
        buttonGroupBox = QGroupBox("Import/Export data", self)
        buttonLayout = QVBoxLayout()
        buttons = []

        self.importDataButton = QPushButton('Import Data')
        self.importDataButton.setToolTip('Imports failure data')
        self.importDataButton.clicked.connect(self.importData)
        buttons.append(self.importDataButton)

        self.saveDataButton = QPushButton('Save Data')
        self.saveDataButton.setToolTip('Saves data in the table failure data')
        self.saveDataButton.clicked.connect(self.saveData)
        buttons.append(self.saveDataButton)

        for button in buttons:
            buttonLayout.addWidget(button)
            #buttonLayout.setAlignment(button, Qt.AlignTop)
        buttonLayout.addStretch(1)
        buttonGroupBox.setLayout(buttonLayout)
        return buttonGroupBox

    def addComputationButtons(self):
        buttonGroupBox = QGroupBox("Computation", self)
        buttonLayout = QVBoxLayout()
        buttons = []
        
        latentErrorLabel = QLabel('Enter Latent Error :')
        self.latentErrorBox = QLineEdit()


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


    def addDataButtons(self):
        
        buttonGroupBox = QGroupBox("Data Manipulation", self)
        buttonLayout = QVBoxLayout()
        buttons = []
        self.addRowButton = QPushButton('Add Row')
        self.addRowButton.setToolTip('Adds a row to the end of the table')
        self.addRowButton.clicked.connect(self.addRow)
        buttons.append(self.addRowButton)

        self.insertRowButton = QPushButton('Insert Row')
        self.insertRowButton.setToolTip('Inserts Row above the selected row')
        self.insertRowButton.clicked.connect(self.insertRow)
        buttons.append(self.insertRowButton)

        self.deleteRowsButton = QPushButton('Delete Row')
        self.deleteRowsButton.setToolTip('Deletes selected row')
        self.deleteRowsButton.clicked.connect(self.deleteRows)
        buttons.append(self.deleteRowsButton)

        self.clearRowsButton = QPushButton('Clear All')
        self.clearRowsButton.setToolTip('Clears all rows')
        self.clearRowsButton.clicked.connect(self.clearRows)
        buttons.append(self.clearRowsButton)

        for button in buttons:
            buttonLayout.addWidget(button)
            #buttonLayout.setAlignment(button, Qt.AlignTop)
        buttonLayout.addStretch(1)
        buttonGroupBox.setLayout(buttonLayout)
        return buttonGroupBox

    def importData(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open File','.')
        data = utils.import_data(fileName)
        self.tableWidget.setRowCount(len(data))
        for i in range(len(data)):
            tVec = QTableWidgetItem()
            kVec = QTableWidgetItem()
            tVec.setText(data[i][0])
            kVec.setText(data[i][1])
            self.tableWidget.setItem(i,0,tVec)
            self.tableWidget.setItem(i,1,kVec)

    def clearRows(self):
        d = QDialog()
        buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                        Qt.Horizontal, self)
        buttons.accepted.connect(d.accept)
        buttons.rejected.connect(d.reject)

        msgLabel = QLabel("Warning: Data from all rows will be cleared. This cannot be undone. Proceed?")
        d.layout = QVBoxLayout(d)
        d.layout.addWidget(msgLabel)
        d.layout.addWidget(buttons)
        d.setWindowTitle("Clear All Rows")

        if d.exec_() == QDialog.Accepted:
            self.tableWidget.clearContents()
        
        

    def deleteRows(self):
        self.tableWidget.removeRow(self.tableWidget.currentRow())

    def addRow(self):
        self.tableWidget.insertRow(self.tableWidget.rowCount())

    def insertRow(self):
        self.tableWidget.insertRow(self.tableWidget.currentRow())

    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Save Data', '.', initialFilter='*.csv')
        data = self.getTableData()
        if fileName:
            utils.export_data(data, fileName)

    def getTableData(self):
        names = []
        data = []
        for i in range(self.tableWidget.rowCount()):
            try:
                if self.tableWidget.item(i,0) != None:
                    names.append(self.tableWidget.item(i,0).text())
                    data.append(self.tableWidget.item(i,1).text())
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        data = {'data':[float(d) for d in data], 'names':names}
        return data

    def compute(self):
        data = {}
        data['dp'] = self.getTableData()
        data['ld'] = self.latentErrorBox.text()
        di = defect_injection.DefectInjection(data)
        self.resultDialog = Mode4ResultsDialog(di)
        print("Compute!")


class Mode4ResultsDialog(QDialog):
    def __init__(self, di, parent=None):
        super(Mode4ResultsDialog, self).__init__(parent)
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
        self.tabWidget.addTab(self.leakageByPhaseTab,"Percentage Leakage by Phase")
        self.tabWidget.addTab(self.finalComputationTab,"Final Computation")

        
        layout.addWidget(self.tabWidget)
        self.setWindowTitle("Defect Discovery and Injection Profiles")
        layout.setAlignment(Qt.AlignTop)
        self.setGeometry(400,400,1000, 800)
        self.show()

    def genFinalCompTable(self):
        layout = QVBoxLayout()

        #Generate final outputs
        labels = ["<b>Overall Defect Discovery Efficiency:</b> {:.2f}%".format(self.di.ODDE*100), 
                "<b>Initial Average Phase Defect Discovery Efficiency:</b> {:.2f}%".format(self.di.ADE*100),
                "<b>Average Phase Defect Discovery Efficiency:</b> {:.2f}%".format(self.di.APDE*100),
                "<b>Initial Average Phase Defect Leakage:</b> {:.2f}%".format(self.di.ADL*100),
                "<b>Average Phase Defect Leakage:</b> {:.2f}%".format(self.di.APDL*100),
                "<b>Latent Defects as % of Total Defects Injected:</b> {:.2f}%".format(self.di.LDPD*100),
                "<b>Total Defects Injected / KSLOC:</b> {:.2f}".format(self.di.TDI),
                "<b>Latent Defects / KSLOC:</b> {:.2f}".format(self.di.LD)
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
                    tableItemRow[col].setText('{:.2f}'.format(self.di.I2[row]))
                else:
                    tableItemRow[col].setText('{:.2f}'.format(data[row, col-1]))
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
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                tableWidget.setItem(curr_row + row, col, tableItemRow[col])

        tableWidget.setVerticalHeaderLabels(self.di.names + [' ', 'Calculated', 'User Input Defects', 'Relative Error'])
        layout.addWidget(tableWidget)
        return layout



    def genDataLabels(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("<h3><b>Total Detected:</b> {:.2f}</h3>".format(self.di.total_defects)))
        layout.addWidget(QLabel("<h3><b>Total Injected:</b> {:.2f}</h3>".format(self.di.TDI)))
        layout.addWidget(QLabel("<h3><b>Latent Error:</b> {:.2f}</h3>".format(self.di.latent_defects)))
        layout.addWidget(QLabel("<h3><b>Peak at Phase:</b> {:.2f}</h3>".format(self.di.profile_peak)))
        layout.setAlignment(Qt.AlignHCenter)
        layout.setSpacing(20)
        return layout

    def genRightPlot(self):
        #Figure definition
        fig2 = plt.figure()
        canvas2 = FigureCanvas(fig2)
        toolbar2 = NavigationToolbar(canvas2, self)
        ax2 = fig2.add_subplot(111)
        ax2.set_xticklabels([""] + self.di.names) #Shifting names 
        ax2.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.2, color='b', label="Injected")
        ax2.bar([i+1 for i in range(self.di.num_phases)], self.di.DDR, width=0.2, color='r', label="Detected")
        ax2.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.LEAK, width=0.2, color='g', label="Leakage")
        ax2.set_xlabel("Phases")
        ax2.set_ylabel("Errors")
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
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                tableWidget2.setItem(row, col, tableItemRow[col])

        layoutfig2 = QVBoxLayout()
        layoutfig2.addWidget(toolbar2)
        layoutfig2.addWidget(canvas2, 1)
        layoutfig2.addWidget(tableWidget2)
        layoutfig2.setAlignment(tableWidget2, Qt.AlignBottom)
        return layoutfig2

    def genLeftPlot(self):
        #figure def
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.set_xticklabels([""] + self.di.names) #Shifting names 
        ax1.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.4, color='b', label="Injected")
        ax1.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.D2, width=0.4, color='r', label="Detected")
        ax1.set_xlabel("Phases")
        ax1.set_ylabel("Errors")
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
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                tableWidget.setItem(row, col, tableItemRow[col])

        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        layoutfig.addWidget(tableWidget)
        layoutfig.setAlignment(tableWidget, Qt.AlignBottom)
        return layoutfig


    def genLeakageRatePlot(self):
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.set_xticklabels([""] + self.di.names) #Shifting names 
        ax1.bar([i+1 for i in range(self.di.num_phases)], self.di.LRATE*100, width=0.4, color='b', label="Leakage Rate by Phase")
        
        ax1.set_xlabel("Phases")
        ax1.set_ylabel("Percentage of Defects")
        ax1.set_title("Leakage Rate by phase")
        ax1.legend()
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
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                tableWidget1.setItem(row, col, tableItemRow[col])

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas, 1)
        layout.addWidget(tableWidget1)
        layout.setAlignment(tableWidget1, Qt.AlignBottom)
        return layout