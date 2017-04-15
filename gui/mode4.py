from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView, QTabWidget
from PyQt5.QtCore import Qt
import PyQt5
from core import utils, models, defect_injection
import sys, math
import matplotlib
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

        self.tabWidget.addTab(self.defectsInPhaseTab, "Defects/KSLOC Injected or Discovered in Phase")
        self.tabWidget.addTab(self.phaseInjectionTab,"Phase Injection/Detection/Leakage")
        self.tabWidget.addTab(self.leakageByPhaseTab,"Percentage Leakage by Phase")

        
        layout.addWidget(self.tabWidget)


        
        self.setWindowTitle("Defect Discovery and Injection Profiles")
        layout.setAlignment(Qt.AlignTop)
        self.setGeometry(400,400,1000, 800)
        self.show()

    def genButtons(self):
        layout = QHBoxLayout()
        percentLeakageButton = QPushButton('Percentage Leakage by Phase')
        percentLeakageButton.clicked.connect(self.percentLeakageDialog())
        injectionMatricesButton = QPushButton('Injection/Leakage Matrices')
        injectionMatricesButton.clicked.connect(self.injectionMatricesDialog())
        qualityMatrixButton = QPushButton('Quality Metrics')
        qualityMatrixButton.clicked.connect(self.qualityMatrixDialog())
        closeButton = QPushButton('Close')
        closeButton.clicked.connect(self.close())

        layout.addWidget(percentLeakageButton)
        layout.addWidget(injectionMatricesButton)
        layout.addWidget(qualityMatrixButton)
        layout.addWidget(closeButton)
        
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
        self.fig2 = plt.figure()
        self.canvas2 = FigureCanvas(self.fig2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)
        ax2 = self.fig2.add_subplot(111)
        ax2.set_xticklabels([""] + self.di.names) #Shifting names 
        ax2.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.2, color='b', label="Injected")
        ax2.bar([i+1 for i in range(self.di.num_phases)], self.di.DDR, width=0.2, color='r', label="Detected")
        ax2.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.LEAK, width=0.2, color='g', label="Leakage")
        ax2.set_xlabel("Phases")
        ax2.set_ylabel("Errors")
        ax2.set_title("Phase Injection/Detection/Leakage")
        ax2.legend()
        self.canvas2.draw()

        #Table definition
        self.tableWidget2 = QTableWidget()
        self.tableWidget2.setRowCount(3)
        self.tableWidget2.setColumnCount(self.di.num_phases)
        self.tableWidget2.setHorizontalHeaderLabels(self.di.names)
        self.tableWidget2.setVerticalHeaderLabels(['Injected','Detected', 'Leakage'])
        self.tableWidget2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = [self.di.I2, self.di.DDR, self.di.LEAK]
        for row in range(3):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            for col in range(self.di.num_phases):
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                self.tableWidget2.setItem(row, col, tableItemRow[col])

        layoutfig2 = QVBoxLayout()
        layoutfig2.addWidget(self.toolbar2)
        layoutfig2.addWidget(self.canvas2, 1)
        layoutfig2.addWidget(self.tableWidget2)
        layoutfig2.setAlignment(self.tableWidget2, Qt.AlignBottom)
        return layoutfig2

    def genLeftPlot(self):
        #figure def
        self.fig1 = plt.figure()
        self.canvas1 = FigureCanvas(self.fig1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        ax1 = self.fig1.add_subplot(111)
        ax1.set_xticklabels([""] + self.di.names) #Shifting names 
        ax1.bar([i+1-0.2 for i in range(self.di.num_phases)], self.di.I2, width=0.4, color='b', label="Injected")
        ax1.bar([i+1+0.2 for i in range(self.di.num_phases)], self.di.D2, width=0.4, color='r', label="Detected")
        ax1.set_xlabel("Phases")
        ax1.set_ylabel("Errors")
        ax1.set_title("Defects/KSLOC Injected or discovered in phase")
        ax1.legend()
        self.canvas1.draw()

        #table def
        self.tableWidget1 = QTableWidget()
        self.tableWidget1.setRowCount(2)
        self.tableWidget1.setColumnCount(self.di.num_phases)
        self.tableWidget1.setHorizontalHeaderLabels(self.di.names)
        self.tableWidget1.setVerticalHeaderLabels(['Injected','Detected'])
        self.tableWidget1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = [self.di.I2, self.di.D2]
        for row in range(2):
            tableItemRow = [QTableWidgetItem() for i in range(self.di.num_phases)]
            for col in range(self.di.num_phases):
                tableItemRow[col].setText('{:.2f}'.format(data[row][col]))
                self.tableWidget1.setItem(row, col, tableItemRow[col])

        layoutfig1 = QVBoxLayout()
        layoutfig1.addWidget(self.toolbar1)
        layoutfig1.addWidget(self.canvas1, 1)
        layoutfig1.addWidget(self.tableWidget1)
        layoutfig1.setAlignment(self.tableWidget1, Qt.AlignBottom)
        return layoutfig1


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
        tableWidget1 = QTableWidget()
        tableWidget1.setRowCount(1)
        tableWidget1.setColumnCount(self.di.num_phases)
        tableWidget1.setHorizontalHeaderLabels(self.di.names)
        tableWidget1.setVerticalHeaderLabels(['Percentage\nof Defects'])
        tableWidget1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        data = [self.di.LRATE*100]
        for row in range(1):
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