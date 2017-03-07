#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Main window for the tool
"""

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QTabWidget, QWidget, QTableWidget,\
    QTableWidgetItem
from PyQt5.QtCore import Qt

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
        openProjectAction.triggered.connect(self.openNewProject)

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

    def openNewProject(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File','.')

        print(fname) 


class TabsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.tabWidget = QTabWidget()
        self.mode1tab = Mode1TabWidget(self)
        self.mode2tab = QWidget()

        self.tabWidget.addTab(self.mode1tab, "Mode 1")
        self.tabWidget.addTab(self.mode2tab, "Mode 2")

        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)

        self.tabWidget.setTabEnabled(0,True)
        self.tabWidget.setTabEnabled(1,True)

class Mode1TabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(4)
        self.tableWidget.setColumnCount(2)
        self.layout.addWidget(self.tableWidget)
        #self.tableWidget.doubleClicked.connect(self.onDoubleClick)

    #    def onDoubleClick(self):





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


