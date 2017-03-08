#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Main window for the tool
"""

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QTabWidget, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel
from PyQt5.QtCore import Qt
from core import utils
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.initUI() 

    def initUI(self):
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('PySweep')
        self.initMenuBar()
        self.tabs = TabsWidget(self)
        self.setCentralWidget(self.tabs)
        self.show()

    def initMenuBar(self):
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl-Q')
        exitAction.setStatusTip('Exit Application')
        exitAction.triggered.connect(qApp.quit)

        newProjectAction = QAction('&New Project',self)
        newProjectAction.setShortcut('Ctrl-N')
        newProjectAction.setStatusTip('Creates a new project')
        newProjectAction.triggered.connect(self.createNewProject)
        
        openProjectAction = QAction('&Open Project',self)
        openProjectAction.setShortcut('Ctrl-O')
        openProjectAction.setStatusTip('Opens an existing project')
        openProjectAction.triggered.connect(self.openProject)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newProjectAction)
        fileMenu.addAction(openProjectAction)
        fileMenu.addAction(exitAction)
        

    def createNewProject(self):
        newProj = NewProject()
        if newProj.exec_() == QDialog.Accepted:
            self.statusBar().showMessage('Accepted!')
        else:
            self.statusBar().showMessage('Rejected!')

    def openProject(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File','.')

        print(fname) 


class TabsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabWidget = QTabWidget()
        self.mode1tab = Mode1TabWidget()
        self.mode2tab = QWidget()

        self.tabWidget.addTab(self.mode1tab, "Mode 1")
        self.tabWidget.addTab(self.mode2tab, "Mode 2")

        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)

        self.tabWidget.setTabEnabled(0,True)
        self.tabWidget.setTabEnabled(1,True)

class Mode1TabWidget(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        #self.layout = QHBoxLayout(self)
        self.layout = QGridLayout(self)
        self.layout.setColumnStretch(1, 2)
        self.layout.setColumnStretch(2, 2)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(1)
        self.layout.addWidget(self.tableWidget,1,1)

        self.buttonPanel = QVBoxLayout(self)
        self.buttonPanel.addWidget(self.addDataButtons())
        self.buttonPanel.addWidget(self.addExternalDataButtons())
        self.buttonPanel.addWidget(self.addComputationButtons())
        self.layout.addLayout(self.buttonPanel,1,2)

        self.tableWidget.setHorizontalHeaderLabels(['Errors'])

        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
    
    def addExternalDataButtons(self):
        buttonGroupBox = QGroupBox("Import/Export data", self)
        buttonLayout = QVBoxLayout(self)
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
        buttonLayout = QVBoxLayout(self)
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
        buttonLayout = QVBoxLayout(self)
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
        #Verify data and start computation
        print("Compute")   
        
    def importData(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open File','.')
        data = utils.import_data(fileName)
        self.tableWidget.setRowCount(len(data))
        for i in range(len(data)):
            item = QTableWidgetItem()
            item.setText(data[i])
            self.tableWidget.setItem(i,0,item)

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
        data = []
        for i in range(self.tableWidget.rowCount()):
            try:
                data.append(int(self.tableWidget.item(i,0).text()))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        if fileName:
            utils.export_data(data, fileName)

class NewProject(QDialog):
    def __init__(self):
        super(NewProject,self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('New Project')
        self.setGeometry(350, 350, 640, 480)
        layout = QVBoxLayout(self)

        self.buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                        Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)


