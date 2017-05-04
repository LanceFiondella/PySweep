from gui.mode_template import ModeTabWidget
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
import numpy as np
if np.finfo(np.longdouble).eps < np.finfo(np.float64).eps:
    from core.models import WeibullNumpy as Weibull
else:
    from core.models import WeibullNumpy as Weibull

class Mode2TabWidget(ModeTabWidget):
    def __init__(self, globalData):
        super().__init__(globalData)
        self.globalData = globalData
        self.modex = 'mode2'
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
            QMessageBox.about(self, 'Error','Phase Values do not total to length of input in Phase 1')
        elif 'mode2' in self.globalData.output.keys():
            self.saveAndDisplayResults(self.globalData.output['mode2'])
        else:
            totalKVec = self.globalData.input['mode1']['kVec']
            totalTVec = self.globalData.input['mode1']['tVec']
            self.cw = ComputeWidget(totalTVec, totalKVec, self.phaseValues)
            self.cw.results.connect(self.saveAndDisplayResults)
            

    def saveAndDisplayResults(self, models):
        print("saving results...  {}".format(len(models)))
        self.globalData.output[self.modex] = models
        self.resultWindow = Mode2ResultsWidget(models, self.phaseNames)
    
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


class Mode2ResultsWidget(QWidget):
    def __init__(self, models, phaseNames, parent=None):
        super().__init__()
        self.models = models
        self.phaseNames = phaseNames
        self.setLayout(self.resultPlot())
        self.show()
        

    def resultPlot(self):
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
        ax.bar([i+1-0.1 for i in range(len(self.models))], [m.kVec_cumu_sum[-1] for m in self.models], width=0.2, color='b', label="Actual")
        ax.bar([i+1+0.1 for i in range(len(self.models))], [m.MVF(m.tVec[-1], a, b, c) for i, m in enumerate(self.models)], width=0.2, color='r', label="Estimated")
        
        ax.set_xlabel("Phases")
        ax.set_ylabel("Errors")
        ax.set_title("Error Discovery Data and Fitted Histograms")
        ax.legend()
        canvas.draw()
        plt.tight_layout()
        plt.grid(True)

        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        return layoutfig
    
            
class ComputeWidget(QWidget):
    results = PyQt5.QtCore.pyqtSignal(list)
    def __init__(self, tVec, kVec, phaseValues, parent=None):
        super(ComputeWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, len(phaseValues))
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
        
        
        self.show()

    def onTaskFinished(self, result):
        # Stop the pulsation
        
        self.results.emit(result)
        self.close()
        
    def updateProgress(self, value):
        self.label.setText("Computing Phase : {}".format(value+1))
        self.progressBar.setValue(value+1)

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
        for i in range(len(self.phaseValues)):
            kVec = self.kVec[:self.phaseValues[i]]
            tVec = self.tVec[:self.phaseValues[i]]
            w = Weibull(kVec, tVec)
            self.models.append(w)
            self.updateProgress.emit(i)

        self.taskFinished.emit(self.models)  