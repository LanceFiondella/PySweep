from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView
from PyQt5.QtCore import Qt
import PyQt5
from core import utils, models
import sys, math
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt



class ModeTabWidget(QWidget):
    """
    This class describes the placement of widgets in the Mode 1 tab
    """
    def __init__(self):
        super().__init__()
        
        self.tVec = []
        self.kVec = []

        #self.layout = QHBoxLayout(self)
        layout = QGridLayout(self)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Dummy','Dummy'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
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
        
        self.computeButton = QPushButton('Compute')
        self.computeButton.setToolTip('Starts the computation')
        self.computeButton.clicked.connect(self.compute)
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
        
    def compute(self):
        """
        This function is run when the compute button is clicked
        #Verify data and start computation
        """
        print("Compute!")
        data = self.getTableData()


    def saveAndDisplayResults(self, weibull):
        print("Save and display results")


    def importData(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open File','.')
        data = utils.import_data(fileName)
        self.populateTable(data)
        

    def setGlobalData(self, data):
        print("Please override this function to set the global data for the particular mode")
        self.globalData.input[self.modex] = data

    def populateTable(self, data):
        self.setGlobalData(data)
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
        data = []
        for i in range(self.tableWidget.rowCount()):
            try:
                if self.tableWidget.item(i,0) != None:
                    data.append((self.tableWidget.item(i,0).text(), self.tableWidget.item(i,1).text()))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        print(data)
        return data