from gui.mode_template import ModeTabWidget
from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView, QTabWidget
from PyQt5.QtCore import Qt
import PyQt5
import sys
import matplotlib
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
from core.models import WeibullNumpy as Weibull
#from gui.mode3 import Mode3ResultsWidget


class ModeBTabWidget(ModeTabWidget):
    def __init__(self, globalData):
        super().__init__(globalData)
        self.globalData = globalData
        self.modex = 'modeB'
        self.tableWidget.setHorizontalHeaderLabels(['Phase Name','Data Points'])
        self.tableWidget.cellChanged.connect(self.tableChanged)
        self.dataChanged = False
        
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
        elif max(self.phaseValues) > len(self.globalData.input['modeA']['tVec']):
            QMessageBox.about(self, 'Error','Phase Values do not total to length of input in Phase 1')
        elif 'modeB' in self.globalData.output.keys() and self.dataChanged == False:
            self.saveAndDisplayResults(self.globalData.output['modeB'])
        else:
            self.dataChanged = False
            totalKVec = self.globalData.input['modeA']['kVec']
            totalTVec = self.globalData.input['modeA']['tVec']
            self.cw = ComputeWidget(totalTVec, totalKVec, self.phaseValues)
            self.cw.results.connect(self.saveAndDisplayResults)
            

    def saveAndDisplayResults(self, models):
        print("saving results...  {}".format(len(models)))
        self.globalData.output[self.modex] = models
        
        self.computeMode3(models)
        self.resultWindow = ModeBResultsWidget(models, self.phaseNames, self.phaseValues, self.results)
        #self.resultWindow2 = Mode3ResultsWidget(self.results, self.phaseNames)
        #self.results = 
    
    def populateTable(self):
        #self.setGlobalData(data)
        col1Name = 'names'
        col2Name = 'values'
        data = self.globalData.input[self.modex]
        print(data)
        self.tableWidget.setRowCount(len(data[col1Name]))
        for i in range(len(data[col1Name])):
            tVec = QTableWidgetItem()
            kVec = QTableWidgetItem()
            tVec.setText(str(data[col1Name][i]))
            kVec.setText(str(data[col2Name][i]))
            self.tableWidget.setItem(i,0,tVec)
            self.tableWidget.setItem(i,1,kVec)

    def tableChanged(self, x, y):
        #print("Table data changed! at : {}, {}".format(x, y))
        self.globalData.input[self.modex] = self.getTableData()
        self.dataChanged = True

    def getTableData(self):
        data = {}
        names = []
        values = []
        for i in range(self.tableWidget.rowCount()):
            try:
                if self.tableWidget.item(i,0) != None and self.tableWidget.item(i,1) != None:
                    names.append(self.tableWidget.item(i,0).text())
                    values.append(int(self.tableWidget.item(i,1).text()))
                    #data.append((self.tableWidget.item(i,0).text(), float(self.tableWidget.item(i,1).text())))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass
        data['names'] = names
        data['values'] = values
        print(data)
        return data

    def addComputationButtons(self):
        buttonGroupBox = QGroupBox("Computation", self)
        buttonLayout = QVBoxLayout()
        buttonLayout.setAlignment(Qt.AlignHCenter)
        buttons = []

        row3 = QHBoxLayout()
        upperTolLabel = QLabel('Upper Tolerance (%) :')
        self.upperTol = QLineEdit()
        self.upperTol.setText('10')
        row3.addWidget(upperTolLabel)
        row3.addWidget(self.upperTol)

        row4 = QHBoxLayout()
        lowerTolLabel = QLabel('Lower Tolerance (%) :')
        self.lowerTol = QLineEdit()
        self.lowerTol.setText('10')
        row4.addWidget(lowerTolLabel)
        row4.addWidget(self.lowerTol)

        row5 = QHBoxLayout()
        sigToNoiseLabel = QLabel('Signal to Noise Ratio :')
        self.sigToNoise = QLineEdit()
        #row5.addWidget(sigToNoiseLabel)
        #row5.addWidget(self.sigToNoise)

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
    
    def computeMode3(self, models):
        self.models = models
        self.upper = []
        self.lower = []
        self.nom = []
        for i in range(len(self.phaseValues)):
            t = i + 1
            a = models[-1].a_est
            #a = float(self.estTotalInjErrors.text())
            b = models[-1].b_est
            c = models[-1].c_est
            Gt = models[-1].MVF(t, a, b, c) - models[-1].MVF(t-1, a, b, c)
            self.nom.append(Gt)
            

            if self.isfloat(self.sigToNoise.text()):
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
        #self.saveAndDisplayResults()

    def isfloat(self, value):
        try:
            value = float(value)
            return True
        except ValueError:
            return False


class ModeBResultsWidget(QWidget):
    def __init__(self, models, phaseNames, phaseValues, results,  parent=None):
        super().__init__()
        self.models = models
        self.phaseNames = phaseNames
        self.phaseValues = phaseValues
        self.results = results
        self.tabWidget = QTabWidget()

        self.tabWidget.addTab(self.modeBResultPlot(), "Mode 2 Results")
        self.tabWidget.addTab(self.mode3ResultPlot(), "Mode 3 Results")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabWidget)
        #self.setLayout(self.resultPlot())
        self.show()
        

    def modeBResultPlot(self):
        widget = QWidget()
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax = fig.add_subplot(111)
        ax.set_xticklabels([""] + self.phaseNames) #Shifting names 
        a = self.models[-1].a_est
        b = self.models[-1].b_est
        c = self.models[-1].c_est
        self.estTotalErrors = self.models[-1].a_est
        self.selPeakLocation = self.models[-1].get_peak_loc()
        self.numLatentErrors = self.models[-1].fi_t(a, b, c, len(self.models))
        self.eff = (1 - self.numLatentErrors/a) * 100
        #ax.bar([i+1-0.1 for i in range(len(self.models))], [m.kVec_cumu_sum[-1] for m in self.models], width=0.2, color='b', label="Actual")
        #ax.bar([i+1+0.1 for i in range(len(self.models))], [m.MVF(m.tVec[-1], a, b, c) for i, m in enumerate(self.models)], width=0.2, color='r', label="Estimated")
        ax.bar([i+1-0.1 for i in range(len(self.phaseNames))], np.cumsum(self.phaseValues), width=0.2, color='b', label="Actual")
        ax.bar([i+1+0.1 for i in range(len(self.phaseNames))], [self.models[-1].MVF(t+1, a, b, c) for t in range(len(self.phaseNames))] , width=0.2, color='r', label="Estimated")

        ax.set_xlabel("Phases")
        ax.set_ylabel("Cumulative Errors")
        ax.set_title("Error Discovery Data and Fitted Histograms")
        ax.legend()
        canvas.draw()
        plt.grid(True)
        
        self.setWindowTitle('SwEET - Mode B Results')
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        widget.setLayout(layoutfig)
        plt.tight_layout()
        return widget

    def mode3ResultPlot(self):
        widget = QWidget()
        fig = plt.figure()
        #plt.tight_layout()
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax = fig.add_subplot(111)
        ax.set_xticklabels([""] + self.phaseNames)
        ax.plot(self.results['lower'], color='g', label='Lower')   
        #ax.bar([i+1-0.2 for i in range(len(self.phaseNames))], self.results['lower'], width=0.2, color='g', label="Lower")
        ax.plot(self.results['nominal'], color='b', label='Nominal')   
        #ax.bar([i+1 for i in range(len(self.phaseNames))], self.results['nominal'], width=0.2, color='b', label="Nominal")
        ax.plot(self.results['upper'], color='r', label='Upper')   
        #ax.bar([i+1+0.2 for i in range(len(self.phaseNames))], self.results['upper'], width=0.2, color='r', label="Upper")
        
        ax.set_xlabel("Phases")
        ax.set_ylabel("Errors")
        ax.set_title("Error Discovery Data and Fitted Histograms")
        ax.legend()
        canvas.draw()
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        widget.setLayout(layoutfig)
        plt.tight_layout()
        return widget

    
            
class ComputeWidget(QWidget):
    results = PyQt5.QtCore.pyqtSignal(list)
    def __init__(self, tVec, kVec, phaseValues, parent=None):
        super(ComputeWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QProgressBar(self)
        #self.progressBar.setRange(0, len(phaseValues))
        self.progressBar.setRange(0,1)
        self.label = QLabel()
        
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        
        #Setup window
        self.setWindowTitle("Processing")
        self.move(400,400)
        #m = Weibull(kVec, tVec)
        self.myLongTask = TaskThread(tVec, kVec, phaseValues)
        self.myLongTask.taskFinished.connect(self.onTaskFinished)
        self.myLongTask.updateProgress.connect(self.updateProgress)
        self.myLongTask.start()
        self.progressBar.setRange(0,0)
        
        self.show()

    def onTaskFinished(self, result):
        # Stop the pulsation
        
        self.results.emit(result)
        self.close()
        
    def updateProgress(self, value):
        self.label.setText("Computing Phase : {}".format(value+1))
        #self.progressBar.setValue(value+1)

class TaskThread(PyQt5.QtCore.QThread):
    taskFinished = PyQt5.QtCore.pyqtSignal(list)
    updateProgress = PyQt5.QtCore.pyqtSignal(int)
    def __init__(self, tVec, kVec, phaseValues):
        super().__init__()
        self.tVec = tVec
        self.kVec = kVec
        self.phaseValues = phaseValues

    def run(self):
        self.models = []
        kPhase = self.phaseValues
        tPhase = [i+1 for i in range(len(kPhase))]
        w = Weibull(kPhase, tPhase, -5)
        self.models.append(w)
        self.updateProgress.emit(len(kPhase))
        #for i in range(len(self.phaseValues)):
        #    kVec = self.kVec[:self.phaseValues[i]]
        #    tVec = self.tVec[:self.phaseValues[i]]
        #    w = Weibull(kVec, tVec)
        #    self.models.append(w)
        #    self.updateProgress.emit(i)

        self.taskFinished.emit(self.models)  
