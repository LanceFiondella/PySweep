"""Scratch pad to make sure I dont delete old code"""


class Mode1TabWidgetOld(QWidget):
    """
    This class describes the placement of widgets in the Mode 1 tab
    """
    def __init__(self):
        super(QWidget, self).__init__()
        
        self.tVec = []
        self.kVec = []

        #self.layout = QHBoxLayout(self)
        layout = QGridLayout(self)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Time Interval','Errors'])
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
        print("Compute")
        data = self.getTableData()
        if len(data) == 0:
            QMessageBox.about(self, 'Error','No data found in table. Please add a dataset')
        else:
            temp_tVec = [a for a,b in data]
            temp_kVec = [b for a,b in data]
            #If there has been a change in data, recompute MLEs. Else display previous results
            if len(self.tVec) == 0 or self.tVec != temp_tVec or self.kVec != temp_kVec: 
                self.tVec = temp_tVec
                self.kVec = temp_kVec
                #print(tVec, kVec)
                self.cw = ComputeWidget(self.tVec, self.kVec)
                self.cw.results.connect(self.saveAndDisplayResults)
            else:
                self.res = Mode1ResultsWidget(self.model)
                

    def saveAndDisplayResults(self, weibull):
        self.model = weibull
        self.res = Mode1ResultsWidget(self.model)


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
        data = []
        for i in range(self.tableWidget.rowCount()):
            try:
                if self.tableWidget.item(i,0) != None:
                    data.append((int(self.tableWidget.item(i,0).text()), int(self.tableWidget.item(i,1).text())))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        print(data)
        return data

class Mode4TabWidgetOld(QWidget):
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