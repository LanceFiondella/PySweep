#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Author: Venkateswaran Shekar (gv.shekar@gmail.com)
Main window for the tool
"""

from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QTabWidget, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel
from PyQt5.QtCore import Qt
from core import utils
from gui import modeA, modeB, modeC
import sys



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.globalData = utils.GlobalData()
        self.initUI() 
        

    def initUI(self):
        self.statusBar().showMessage('Ready')
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('SwEET')
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
        #fileMenu.addAction(newProjectAction)
        fileMenu.addAction(openProjectAction)
        fileMenu.addAction(exitAction)
    
    def closeEvent(self, event):
        qApp.quit()
        

    def createNewProject(self):
        newProj = NewProject()
        if newProj.exec_() == QDialog.Accepted:
            self.statusBar().showMessage('Accepted!')
        else:
            self.statusBar().showMessage('Rejected!')

    def openProject(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File','.', filter='*.xlsx')
        #print(fname)
        self.globalData.import_input_excel(fname[0])
        self.tabs.modeAtab.populateTable()
        self.tabs.modeBtab.populateTable()
        #self.tabs.mode3tab.populateTable()
        self.tabs.modeCtab.populateTable()
        


class TabsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.tabWidget = QTabWidget()
        self.modeAtab = modeA.ModeATabWidget(parent.globalData)
        self.modeBtab = modeB.ModeBTabWidget(parent.globalData)
        #self.mode3tab = mode3.Mode3TabWidget(parent.globalData)
        self.modeCtab = modeC.ModeCTabWidget(parent.globalData)

        self.tabWidget.addTab(self.modeAtab, "Mode A")
        self.tabWidget.addTab(self.modeBtab, "Mode B")
        #self.tabWidget.addTab(self.mode3tab, "Mode 3")
        self.tabWidget.addTab(self.modeCtab, "Mode C")

        self.layout.addWidget(self.tabWidget)
        #self.setLayout(self.layout)

        self.tabWidget.setTabEnabled(0,True)
        self.tabWidget.setTabEnabled(1,True)

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


