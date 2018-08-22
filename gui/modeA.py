from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView, QTabWidget
from PyQt5.QtCore import Qt
import PyQt5
import sys, math
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.mode_template import ModeTabWidget
from core import utils
import numpy as np
#Check if float128 is available. If it is, use WeibullNumPy else use WeibullMP
from core.models import WeibullNumpy as Weibull

class ModeATabWidget(ModeTabWidget):
    def __init__(self, globalData):
        self.globalData = globalData
        super().__init__(globalData)
        self.tableWidget.setHorizontalHeaderLabels(['Time Interval','Defects'])
        self.tableWidget.cellChanged.connect(self.tableChanged)
        self.dataChanged = False
        self.modex = 'modeA'

    def compute(self):
        """
        This function is run when the compute button is clicked
        #Verify data and start computation
        """
        print("Compute")
        data = self.getTableData()
        if len(data) == 0:
            QMessageBox.about(self, 'Defect','No data found in table. Please add a dataset')
        else:
            temp_tVec = data['tVec']
            temp_kVec = data['kVec']
            #If there has been a change in data, recompute MLEs. Else display previous results
            #if len(self.tVec) == 0 or self.tVec != temp_tVec or self.kVec != temp_kVec: 
            if self.dataChanged:
                self.tVec = temp_tVec
                self.kVec = temp_kVec
                #print(tVec, kVec)
                self.cw = ComputeWidget(self.tVec, self.kVec)
                self.cw.results.connect(self.saveAndDisplayResults)
                self.dataChanged = False
            else:
                self.res = ModeAResultsWidget(self.model)
    
    def setGlobalData(self, data):
        tVec = [int(a) for a,b in data]
        kVec = [int(b) for a,b in data]
        self.globalData.input[self.modex] = {}
        self.globalData.input[self.modex]['tVec'] = tVec
        self.globalData.input[self.modex]['kVec'] = kVec


    def saveAndDisplayResults(self, weibull):
        self.model = weibull
        self.globalData.output['modeA'] = weibull
        self.res = ModeAResultsWidget(self.model)

    def populateTable(self):
        #self.setGlobalData(data)
        col1Name = 'tVec'
        col2Name = 'kVec'
        data = self.globalData.input[self.modex]
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
                    names.append(int(self.tableWidget.item(i,0).text()))
                    values.append(int(self.tableWidget.item(i,1).text()))
                    #data.append((self.tableWidget.item(i,0).text(), float(self.tableWidget.item(i,1).text())))
            except:
                print("Unexpected error:", sys.exc_info()[0])
                pass
        data['tVec'] = names
        data['kVec'] = values
        print(data)
        return data


class ModeAResultsWidget(QDialog):
    def __init__(self, weibull, parent=None):
        super(ModeAResultsWidget, self).__init__(parent)
        self.model = weibull
        layout = QVBoxLayout(self)

        self.errorsToDate = QLabel()
        self.errorsToDate.setText("<b>Defects discovered to date:</b> {:.6f}".format(self.model.total_failures))
        self.totalProjected = QLabel()
        self.totalProjected.setText("<b>Total Defects projected:</b> {:.6f}".format(self.model.a_est))
        self.percentOfErrors = QLabel()
        self.percentOfErrors.setText("<b>Percentage of projected Defects found to date:</b> {:.6f}".format(100.0*self.model.total_failures/self.model.a_est))
        self.estPeakLocation = QLabel()
        self.estPeakLocation.setText("<b>Estimated location of peak:</b> {:.6f} ".format(self.model.get_peak_loc()+1)) #Added 1 because of Python 0 indexing

        self.tabWidget = QTabWidget()
        self.cumuCurveTab = QWidget()
        self.cumuCurveTab.setLayout(self.genCumuCurve())
        self.inciCurveTab = QWidget()
        self.inciCurveTab.setLayout(self.genInciCurve())
        self.dataSheetTab = QWidget()
        self.dataSheetTab.setLayout(self.genDataSheet())
        self.estErrorsTab = QWidget()
        self.estErrorsTab.setLayout(self.genErrorEstLayout())
        
        self.tabWidget.addTab(self.cumuCurveTab, "Cumulative Curve")
        self.tabWidget.addTab(self.inciCurveTab,"Incidence Curve")
        self.tabWidget.addTab(self.dataSheetTab, "Time Based Model Output Data Sheet")
        self.tabWidget.addTab(self.estErrorsTab,"Estimated Defects")
        
    
        layout.addWidget(self.errorsToDate)
        layout.addWidget(self.totalProjected)
        layout.addWidget(self.percentOfErrors)
        layout.addWidget(self.estPeakLocation)
        
        #layout.addWidget(self.genErrorEstLayout())
        layout.addWidget(self.tabWidget)
        layout.addLayout(self.genButtonLayout())
        self.setWindowTitle('SwEET - Mode A Results')
        self.move(400,400)
        self.show()
    
    def genErrorEstLayout(self):
        #errorEstGroupBox = QGroupBox("Error Estimate Selection", self)
        
        intervalErrorGroupBox = QGroupBox("Estimated Defects based on Intervals Entered (n)", self)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        noie = QLabel("{} {}".format("<b>Number of intervals entered:</b>",self.model.n))
        noie.setAlignment(Qt.AlignCenter)
        tedtd = QLabel("{} {:.6f}".format("<b>Total Defects Discovered to Date:</b>", self.model.total_failures))
        tedtd.setAlignment(Qt.AlignCenter)
        tep = QLabel("<b>Total Defects Projected:</b> {0:.6f}".format(self.model.a_est))
        tep.setAlignment(Qt.AlignCenter)
        layout.addWidget(noie)
        layout.addWidget(tedtd)
        layout.addWidget(tep)
        
        resultHBox = QHBoxLayout()
        resultHBox.addWidget(self.genEstimatedErrorBox())
        resultHBox.addWidget(self.genPercentErrorBox())

        computeButton = QPushButton("Compute")
        computeButton.clicked.connect(self.compute)
        
        
        layout.addLayout(resultHBox)
        layout.addWidget(computeButton, 0, Qt.AlignRight)
        return layout
    
    def genPercentErrorBox(self):
        self.percent = 0
        self.intervalsNeeded = 0
        self.intervalsRemain = 0
        percentErrorGroupBox = QGroupBox("Estimated Defects based on Percentage (p)", self)
        layout = QVBoxLayout()
        label = QLabel("Enter Data (p) : ")
        self.dataTextBoxP = QLineEdit()
        self.dataTextBoxP.setText('0')
        self.pefe = QLabel("<b>Percentage (p) entered for estimate:</b> {}".format(self.percent))
        self.intap = QLabel("<b>Intervals needed to achieve p:</b> {0:.6f}".format(self.intervalsNeeded))
        self.irantap = QLabel("<b>Intervals remaining after n needed to achieve p:</b> {0:10.6f}".format(self.intervalsRemain))
        layout.addWidget(label)
        layout.addWidget(self.dataTextBoxP)
        layout.addWidget(self.pefe)
        layout.addWidget(self.intap)
        layout.addWidget(self.irantap)
        percentErrorGroupBox.setLayout(layout)
        return percentErrorGroupBox

    def genEstimatedErrorBox(self):
        self.intervals = 0
        percentErrorGroupBox = QGroupBox("Estimated Total Defects based on Intervals through m (n+m)", self)
        layout = QVBoxLayout()
        label = QLabel("Enter Data (m) : ")
        self.dataTextBoxM = QLineEdit()
        self.dataTextBoxM.setText('0')
        #noie = QLabel("<b>Number of Intervals Estimated (m):</b> {}".format(self.intervals))
        t = self.model.tn + self.intervals
        a = self.model.a_est
        b = self.model.b_est
        c = self.model.c_est
        self.errorsThroughM = self.model.MVF(t, a, b, c)
        self.errorsInM = self.errorsThroughM - self.model.total_failures
        numer = math.log(1 - (99.99 / 100))
        term = - numer / b
        self.intervals99 = math.pow(term, 1/c)
        poped = QLabel("<b>Intervals Needed to Achieve 99.99% of Total Defects:</b> {0:.6f}".format(self.intervals99))
        self.tedti = QLabel("<b>Total Defects Discovered through Interval (m):</b> {0:.6f}".format(self.errorsThroughM))
        self.eeimi = QLabel("<b>Estimated Defects in (m) intervals:</b> {0:.6f}".format(self.errorsInM))
        self.pote =  QLabel("<b>Percentage of Total Defects:</b> {0:.6f}".format(100.0* self.errorsThroughM / a))
        layout.addWidget(label)
        layout.addWidget(self.dataTextBoxM)
        layout.addWidget(poped)
        layout.addWidget(self.tedti)
        layout.addWidget(self.eeimi)
        layout.addWidget(self.pote)
        percentErrorGroupBox.setLayout(layout)
        return percentErrorGroupBox

    def compute(self):
        if self.isFloat(self.dataTextBoxM.text()) == False and self.isFloat(self.dataTextBoxP.text())==False:
            QMessageBox.about(self, 'Defect','Please enter a valid input')

        if self.isFloat(self.dataTextBoxM.text()):
            self.intervals = float(self.dataTextBoxM.text())
            t = self.model.tn + self.intervals
            a = self.model.a_est
            b = self.model.b_est
            c = self.model.c_est
            self.errorsThroughM = self.model.MVF(t, a, b, c)
            self.errorsInM = self.errorsThroughM - self.model.total_failures
            self.tedti.setText("<b>Total Defects Discovered through Interval (m):</b> {0:.6f}".format(self.errorsThroughM))
            self.eeimi.setText("<b>Estimated Defects in (m) intervals:</b> {0:.6f}".format(self.errorsInM))
            self.pote.setText("<b>Percentage of Total Defects:</b> {0:.6f}".format(100.0* self.errorsThroughM / a))
            
        
        if self.isFloat(self.dataTextBoxP.text()):
            self.percent = float(self.dataTextBoxP.text())
            numer = math.log(1 - (self.percent / 100))
            term = - numer / self.model.b_est
            self.intervalsNeeded = math.pow(term, 1/self.model.c_est)
            self.intervalsRemain = self.intervalsNeeded - self.model.n
            self.pefe.setText("<b>Percentage (p) entered for estimate:</b> {0:.6f}".format(self.percent))
            self.intap.setText("<b>Intervals needed to achieve p:</b> {0:.6f}".format(self.intervalsNeeded))
            self.irantap.setText("<b>Intervals remaining after n needed to achieve p:</b> {0:10.6f}".format(self.intervalsRemain))
        
    def isFloat(self, text):
        try:
            result = float(text)
            return True
        except:
            return False
        
    def genButtonLayout(self):
        buttonLayout = QHBoxLayout()
        
        cancelButton = QPushButton('Close')
        buttonLayout.addWidget(cancelButton, 0, Qt.AlignRight)
        cancelButton.clicked.connect(self.close)
        return buttonLayout
    
    def genCumuCurve(self):
        fig = plt.figure()
        
        
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.plot(self.model.tVec, self.model.kVec_cumu_sum, 'b', label="Actual")
        ax1.plot(self.model.tVec, self.model.MVF_cumu_vals, 'r', label="Estimated")
        ax1.set_xlabel("Intervals")
        ax1.set_ylabel("Defects")
        ax1.set_title("Cumulative Curve")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
        ax1.legend()
        canvas.draw()
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        plt.tight_layout()
        return layoutfig



    def genInciCurve(self):
        fig = plt.figure()
        
        #plt.tight_layout()
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.bar([i for i in self.model.tVec], self.model.kVec, width=0.4, color='b', label="Actual")
        #ax1.bar([i+0.2 for i in self.model.tVec], self.model.FI_vals, width=0.4, color='r', label="Estimated")
        ax1.plot(self.model.tVec,self.model.FI_vals, color='r', label='Estimated')      #Added [0] to the begining of FI_vals because vector starts from 1 not 0
        ax1.set_xlabel("Intervals")
        ax1.set_ylabel("Defects")
        ax1.set_title("Incidence Curve")
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
        ax1.legend()
        canvas.draw()
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        plt.tight_layout()
        return layoutfig



    def genDataSheet(self):
        layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(self.model.n)
        self.tableWidget.setColumnCount(10)
        self.tableLabels = ['Interval','Actual Defect', 'Estimated Defect', \
                                    'Defect Delta', 'Relative Data', 'Cumulative\n % of E', 'Actual\n Cumulation', \
                                     'Estimated\n Cumulation', 'Cumulation\n Delta', 'Relative Delta']
        self.tableWidget.setHorizontalHeaderLabels(self.tableLabels)
        self.populateTable()
        layout.addWidget(self.tableWidget)
        
        buttons = QDialogButtonBox(
                        Qt.Horizontal, self)
        buttons.accepted.connect(self.saveData)
        buttons.rejected.connect(self.reject)
        buttons.addButton(QDialogButtonBox.Save)
        layout.addWidget(buttons)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return layout

    def populateTable(self):
        data = [self.model.tVec, self.model.kVec, self.model.MVF_vals, self.model.error_delta, \
                    self.model.rel_delta, self.model.cumu_percent, self.model.kVec_cumu_sum, \
                    self.model.MVF_cumu_sum, self.model.cumu_delta, self.model.cumu_rel_delta]
        for row in range(len(self.model.tVec)):
            tableItemRow = [QTableWidgetItem() for i in range(10)]
            for col in range(10):
                #tableItemRow[col].setText('{:.4f}'.format(data[col][row]))
                tableItemRow[col].setText('{:.6f}'.format(data[col][row]))
                self.tableWidget.setItem(row, col, tableItemRow[col])

    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Save Data', '.', initialFilter='*.csv')
        data = self.getTableData()
        if fileName:
            utils.export_data(data, fileName)

    def getTableData(self):
        #Labels defined again to remove new line characters from the titles
        tableLabels = ['Interval','Actual Defect', 'Estimated Defect', \
                        'Defect Delta', 'Relative Delta', 'Cumulative % of Defect', 'Actual Cumulation', \
                            'Estimated Cumulation', 'Cumulation Delta', 'Relative Delta']
        data = [tableLabels]
        for i in range(self.tableWidget.rowCount()):
            row = []
            for col in range(10):
                row.append(self.tableWidget.item(i,col).text())
            data.append(row)
        #print(data)
        return data


class ComputeWidget(QWidget):
    results = PyQt5.QtCore.pyqtSignal(Weibull)
    def __init__(self, tVec, kVec, parent=None):
        super(ComputeWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,1)
        self.label = QLabel()
        self.label.setText("Computing results please wait...")
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        
        #Setup window
        self.setWindowTitle("Processing")
        self.move(400,400)


        self.myLongTask = TaskThread(tVec, kVec)
        self.myLongTask.taskFinished.connect(self.onFinished)
        self.progressBar.setRange(0,0)
        self.myLongTask.start()
        self.show()

    def onFinished(self, result):
        # Stop the pulsation
        self.results.emit(result)
        self.progressBar.setRange(0,1)
        self.close()


class TaskThread(PyQt5.QtCore.QThread):
    taskFinished = PyQt5.QtCore.pyqtSignal(Weibull)
    def __init__(self, tVec, kVec):
        super().__init__()
        self.tVec = tVec
        self.kVec = kVec

    def run(self):
        w = Weibull(self.kVec, self.tVec, -15)
        self.taskFinished.emit(w)  
