from gui.mode_template import ModeTabWidget
from core.models import Weibull

from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView
from PyQt5.QtCore import Qt
import PyQt5
import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from gui.mode2 import ComputeWidget
import math
import numpy as np

class Mode3TabWidget(ModeTabWidget):
    def __init__(self, globalData):
        super().__init__(globalData)
        self.modex = 'mode3'
        self.globalData = globalData
        self.tableWidget.setHorizontalHeaderLabels(['Phase Name','Data Points'])
        
    def setGlobalData(self, data):
        self.phaseNames = [a for a,b in data]
        self.phaseValues = [int(b) for a,b in data]
        self.globalData.input[self.modex] = {}
        self.globalData.input[self.modex]['names'] = self.phaseNames
        self.globalData.input[self.modex]['values'] = self.phaseValues

    def compute(self):
        data = self.getTableData()
        self.phaseNames = self.globalData.input[self.modex]['names']
        self.phaseValues = self.globalData.input[self.modex]['values']
        if len(data) == 0:
            QMessageBox.about(self, 'Error','No data found in table. Please add a dataset')
        elif max(self.phaseValues) > len(self.globalData.input['mode1']['tVec']):
            QMessageBox.about(self, 'Error','Phase Values do not total to length of input in Phases')
        elif 'mode2' in self.globalData.output.keys() and self.globalData.input['mode2']['values'] == self.globalData.input['mode3']['values']:
            #print("Mode 3 same as Mode 2, taking results from mode 2")
            self.computeMode3(self.globalData.output['mode2'])
        elif 'mode3' in self.globalData.output.keys():          
            self.computeMode3(self.globalData.output['mode3'])
        else:
            totalKVec = self.globalData.input['mode1']['kVec']
            totalTVec = self.globalData.input['mode1']['tVec']

            self.cw = ComputeWidget(totalTVec, totalKVec, self.phaseValues)

            self.cw.results.connect(self.computeMode3)
        
    def computeMode3(self, models):
        self.models = models
        self.upper = []
        self.lower = []
        self.nom = []
        for i in range(len(models)):
            t = i + 1
            a = models[i].a_est
            #a = float(self.estTotalInjErrors.text())
            b = models[i].b_est
            c = models[i].c_est
            Gt = models[i].MVF(t, a, b, c) - models[i].MVF(t-1, a, b, c)
            self.nom.append(Gt)
            

            if self.isfloat(self.sigToNoise.text()):
                print("Found signal to noise!")
                snr = float(self.sigToNoise.text())
                if snr >= 1:
                    Ut = ((snr + 1)/snr)*self.nom[-1]
                    Lt = ((snr - 1)/snr)*self.nom[-1]
                else:
                    utol = 100/snr
                    ltol = 100/snr
                    Ut = Gt * (1 + 0.01 * utol)
                    Lt = Gt * (1 - 0.01 * ltol)    
            elif self.isfloat(self.upperTol.text()) and self.isfloat(self.lowerTol.text()):
                utol = float(self.upperTol.text())
                ltol = float(self.lowerTol.text())
                Ut = Gt * (1 + 0.01 * utol)
                Lt = Gt * (1 - 0.01 * ltol)
            self.upper.append(Ut)
            self.lower.append(Lt)
        print(self.nom)
        self.results = {'upper':self.upper, 'lower':self.lower, 'nominal':self.nom}
        self.saveAndDisplayResults()

    def isfloat(self, value):
        try:
            value = float(value)
            return True
        except ValueError:
            return False

    def saveAndDisplayResults(self):
        self.globalData.output['mode3'] = self.models
        self.resultWindow = Mode3ResultsWidget(self.results, self.phaseNames)
    
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

    def addComputationButtons(self):
        buttonGroupBox = QGroupBox("Computation", self)
        buttonLayout = QVBoxLayout()
        buttonLayout.setAlignment(Qt.AlignHCenter)
        buttons = []
        
        """
        row1 = QHBoxLayout()
        estTotalInjErrorsLabel = QLabel('Estimated Total Injected Errors :')
        self.estTotalInjErrors = QLineEdit()
        row1.addWidget(estTotalInjErrorsLabel)
        row1.addWidget(self.estTotalInjErrors)

        row2 = QHBoxLayout()
        peakLocLabel = QLabel('Peak Location (T) :')
        self.peakLoc = QLineEdit()
        row2.addWidget(peakLocLabel)
        row2.addWidget(self.peakLoc)
        """
        row3 = QHBoxLayout()
        upperTolLabel = QLabel('Upper Tolerance (%) :')
        self.upperTol = QLineEdit()
        row3.addWidget(upperTolLabel)
        row3.addWidget(self.upperTol)

        row4 = QHBoxLayout()
        lowerTolLabel = QLabel('Lower Tolerance (%) :')
        self.lowerTol = QLineEdit()
        row4.addWidget(lowerTolLabel)
        row4.addWidget(self.lowerTol)

        row5 = QHBoxLayout()
        sigToNoiseLabel = QLabel('Signal to Noise Ratio :')
        self.sigToNoise = QLineEdit()
        row5.addWidget(sigToNoiseLabel)
        row5.addWidget(self.sigToNoise)

        #buttonLayout.addLayout(row1)
        #buttonLayout.addLayout(row2)
        buttonLayout.addLayout(row3)
        buttonLayout.addLayout(row4)
        buttonLayout.addLayout(row5)


        self.computeButton = QPushButton('Compute')
        self.computeButton.setToolTip('Starts the computation')
        self.computeButton.clicked.connect(self.compute)
        buttons.append(self.computeButton)
        

        for button in buttons:
            buttonLayout.addWidget(button)
        
        buttonLayout.addStretch(1)
        buttonGroupBox.setLayout(buttonLayout)
        return buttonGroupBox



class Mode3ResultsWidget(QWidget):
    def __init__(self, results, phaseNames, parent=None):
        super().__init__()
        self.results = results
        self.phaseNames = phaseNames
        self.setLayout(self.resultPlot())
        self.show()
    
    def resultPlot(self):
        fig = plt.figure()
        #plt.tight_layout()
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax = fig.add_subplot(111)
        ax.set_xticklabels([""] + self.phaseNames)
        print(self.results['lower'])
        print(self.results['upper'])
        ax.bar([i+1-0.2 for i in range(len(self.phaseNames))], self.results['lower'], width=0.2, color='g', label="Lower")
        ax.bar([i+1 for i in range(len(self.phaseNames))], self.results['nominal'], width=0.2, color='b', label="Nominal")
        ax.bar([i+1+0.2 for i in range(len(self.phaseNames))], self.results['upper'], width=0.2, color='r', label="Upper")
        
        ax.set_xlabel("Phases")
        ax.set_ylabel("Errors")
        ax.set_title("Error Discovery Data and Fitted Histograms")
        ax.legend()
        canvas.draw()

        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        return layoutfig