from PyQt5.QtWidgets import QDialog, QVBoxLayout,\
    QDialogButtonBox, QFileDialog, QWidget, QTableWidget,\
    QTableWidgetItem, QGridLayout, QPushButton, QHBoxLayout, QHeaderView, QGroupBox,\
    QLabel, QProgressBar, QRadioButton, QLineEdit, QMessageBox, QAbstractItemView, QTabWidget
from PyQt5.QtCore import Qt
import PyQt5
from core import utils, models
import sys, math
import matplotlib
matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from gui.mode_template import ModeTabWidget

class Mode1TabWidget(ModeTabWidget):
    def __init__(self, globalData):
        self.globalData = globalData
        super().__init__(globalData)
        self.tableWidget.setHorizontalHeaderLabels(['Time Interval','Errors'])
        self.modex = 'mode1'

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
    
    def setGlobalData(self, data):
        tVec = [int(a) for a,b in data]
        kVec = [int(b) for a,b in data]
        self.globalData.input[self.modex] = {}
        self.globalData.input[self.modex]['tVec'] = tVec
        self.globalData.input[self.modex]['kVec'] = kVec


    def saveAndDisplayResults(self, weibull):
        self.model = weibull
        self.globalData.output['mode1'] = weibull
        self.res = Mode1ResultsWidget(self.model)

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


class Mode1ResultsWidget(QDialog):
    def __init__(self, weibull, parent=None):
        super(Mode1ResultsWidget, self).__init__(parent)
        self.model = weibull
        layout = QVBoxLayout(self)

        self.errorsToDate = QLabel()
        self.errorsToDate.setText("<b>Errors discovered to date:</b> {}".format(self.model.total_failures))
        self.totalProjected = QLabel()
        self.totalProjected.setText("<b>Total errors projected:</b> {}".format(self.model.a_est))
        self.percentOfErrors = QLabel()
        self.percentOfErrors.setText("<b>Percentage of projected errors found to date:</b> {}".format(100.0*self.model.total_failures/self.model.a_est))
        self.estPeakLocation = QLabel()
        self.estPeakLocation.setText("<b>Estimated location of peak:</b> {} ".format(self.model.get_peak_loc()+1)) #Added 1 because of Python 0 indexing

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
        self.tabWidget.addTab(self.estErrorsTab,"Estimated Errors")


        layout.addWidget(self.errorsToDate)
        layout.addWidget(self.totalProjected)
        layout.addWidget(self.percentOfErrors)
        layout.addWidget(self.estPeakLocation)
        
        #layout.addWidget(self.genErrorEstLayout())
        layout.addWidget(self.tabWidget)
        layout.addLayout(self.genButtonLayout())
        self.setWindowTitle("Estimated Errors")
        self.move(400,400)
        self.show()
    
    def genErrorEstLayout(self):
        #errorEstGroupBox = QGroupBox("Error Estimate Selection", self)
        layout = QVBoxLayout()
        self.estNextMRadioButton = QRadioButton("Estimate the number of Errors in Next (m) Intervals")
        self.estNextMRadioButton.setChecked(True)
        
        self.detNumIntRadioButton = QRadioButton("Determine the number of intervals required to achieve the following \% p based on the total number of errors projected")
        
        layout.addWidget(self.estNextMRadioButton)
        layout.addWidget(self.detNumIntRadioButton)

        hlayout = QHBoxLayout()
        label = QLabel("Enter Data (m or p) : ")
        self.dataTextBox = QLineEdit()
        computeButton = QPushButton("Compute")
        computeButton.clicked.connect(self.compute)
        hlayout.addWidget(label)
        hlayout.addWidget(self.dataTextBox)
        hlayout.addWidget(computeButton)

        layout.addLayout(hlayout)
        
        #errorEstGroupBox.setLayout(layout)
        return layout

    def compute(self):
        try:
            number = float(self.dataTextBox.text())
            if self.detNumIntRadioButton.isChecked():
                self.cpd = CalculatePDialog(self.model, number)
            elif self.estNextMRadioButton.isChecked():
                print("calculate M")
                self.cmd = CalculateMDialog(self.model, number)
        except Exception:
            
            QMessageBox.about(self, 'Error','Input can only be a number')
            pass
    
    def genButtonLayout(self):
        buttonLayout = QHBoxLayout()
        
        cancelButton = QPushButton('Close')
        buttonLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.close)
        return buttonLayout
    
    def genCumuCurve(self):
        fig = plt.figure()
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
        plt.tight_layout()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.plot(self.model.tVec, self.model.kVec_cumu_sum, 'b', label="Actual")
        ax1.plot(self.model.tVec, self.model.MVF_vals, 'r', label="Estimated")
        ax1.set_xlabel("Intervals")
        ax1.set_ylabel("Errors")
        ax1.set_title("Cumulative Curve")
        ax1.legend()
        canvas.draw()
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        return layoutfig



    def genInciCurve(self):
        fig = plt.figure()
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
        plt.tight_layout()
        plt.grid(True)
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        ax1 = fig.add_subplot(111)
        ax1.bar([i-0.2 for i in self.model.tVec], self.model.kVec, width=0.4, color='b', label="Actual")
        ax1.bar([i+0.2 for i in self.model.tVec], self.model.FI_vals, width=0.4, color='r', label="Estimated")
        ax1.set_xlabel("Intervals")
        ax1.set_ylabel("Errors")
        ax1.set_title("Incidence Curve")
        ax1.legend()
        canvas.draw()
        layoutfig = QVBoxLayout()
        layoutfig.addWidget(toolbar)
        layoutfig.addWidget(canvas, 1)
        return layoutfig



    def genDataSheet(self):
        layout = QVBoxLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(self.model.n)
        self.tableWidget.setColumnCount(10)
        self.tableLabels = ['Interval','Actual Error', 'Estimated Error', \
                                    'Error Delta', 'Relative Data', 'Cumulative\n % of E', 'Actual\n Cumulation', \
                                     'Estimated\n Cumulation', 'Cumulation\n Delta', 'Relative Delta']
        self.tableWidget.setHorizontalHeaderLabels(self.tableLabels)
        self.populateTable()
        layout.addWidget(self.tableWidget)
        
        buttons = QDialogButtonBox(
                        QDialogButtonBox.Close,
                        Qt.Horizontal, self)
        buttons.accepted.connect(self.saveData)
        buttons.rejected.connect(self.reject)
        buttons.addButton(QDialogButtonBox.Save)
        layout.addWidget(buttons)

        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return layout

    def populateTable(self):
        data = [self.model.tVec, self.model.kVec, self.model.MVF_vals, self.model.error_delta, \
                    self.model.rel_delta, self.model.kVec_cumu_sum, self.model.kVec_cumu_sum, \
                    self.model.MVF_cumu_sum, self.model.cumu_delta, self.model.cumu_rel_delta]
        for row in range(len(self.model.tVec)):
            tableItemRow = [QTableWidgetItem() for i in range(10)]
            for col in range(10):
                tableItemRow[col].setText('{:.4f}'.format(data[col][row]))
                self.tableWidget.setItem(row, col, tableItemRow[col])

    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Save Data', '.', initialFilter='*.csv')
        data = self.getTableData()
        if fileName:
            utils.export_data(data, fileName)

    def getTableData(self):
        #Labels defined again to remove new line characters from the titles
        tableLabels = ['Interval','Actual Error', 'Estimated Error', \
                        'Error Delta', 'Relative Data', 'Cumulative % of E', 'Actual Cumulation', \
                            'Estimated Cumulation', 'Cumulation Delta', 'Relative Delta']
        data = [tableLabels]
        for i in range(self.tableWidget.rowCount()):
            row = []
            for col in range(10):
                row.append(self.tableWidget.item(i,col).text())
            data.append(row)
        #print(data)
        return data


class CalculateMDialog(QDialog):
    def __init__(self, model, intervals, parent=None):
        super(CalculateMDialog, self).__init__(parent)
        self.model = model
        self.intervals = intervals
        self.calcIntervals99()
        buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok,
                        Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        
        layout = QVBoxLayout(self)

        layout.addWidget(self.genIntervalErrorBox())
        layout.addWidget(self.genEstimatedErrorBox())
        layout.addWidget(buttons)

        self.setWindowTitle("Calculate P")
        self.move(400,400)
        self.show()

    def calcIntervals99(self):
        numer = math.log(1 - (99.99 / 100))
        term = - numer / self.model.b_est
        self.intervals99 = math.pow(term, 1/self.model.c_est)
        

    def genIntervalErrorBox(self):
        intervalErrorGroupBox = QGroupBox("Estimated Errors based on Intervals Entered (n)", self)
        layout = QVBoxLayout()
        noie = QLabel("{} {}".format("<b>Number of intervals entered:</b>",self.model.n))
        noie.setAlignment(Qt.AlignCenter)
        tedtd = QLabel("{} {}".format("<b>Total Errors Discovered to Date:</b>", self.model.total_failures))
        tedtd.setAlignment(Qt.AlignCenter)
        tep = QLabel("<b>Total Errors Projected:</b> {0:.4f}".format(self.model.a_est))
        tep.setAlignment(Qt.AlignCenter)
        poped = QLabel("<b>Intervals Needed to Achieve 99.99% of Total Errors:</b> {0:.4f}".format(self.intervals99))
        poped.setAlignment(Qt.AlignCenter)
        layout.addWidget(noie)
        layout.addWidget(tedtd)
        layout.addWidget(tep)
        layout.addWidget(poped)

        intervalErrorGroupBox.setLayout(layout)
        return intervalErrorGroupBox

    def genEstimatedErrorBox(self):
        percentErrorGroupBox = QGroupBox("Estimated Total Errors based on Intervals through m (n+m)", self)
        layout = QVBoxLayout()
        noie = QLabel("<b>Number of Intervals Estimated (m):</b> {}".format(self.intervals))
        t = self.model.tn + self.intervals
        a = self.model.a_est
        b = self.model.b_est
        c = self.model.c_est
        errorsThroughM = self.model.MVF(t, a, b, c)
        errorsInM = errorsThroughM - self.model.total_failures
        tedti = QLabel("<b>Total Errors Discovered through Interval (m):</b> {0:.4f}".format(errorsThroughM))
        eeimi = QLabel("<b>Estimated Errors in (m) intervals:</b> {0:.4f}".format(errorsInM))
        pote =  QLabel("<b>Percentage of Total Errors:</b> {0:.4f}".format(100.0* errorsThroughM / a))
        layout.addWidget(noie)
        layout.addWidget(tedti)
        layout.addWidget(eeimi)
        layout.addWidget(pote)
        percentErrorGroupBox.setLayout(layout)
        return percentErrorGroupBox

class CalculatePDialog(QDialog):
    def __init__(self, model, percent, parent=None):
        super(CalculatePDialog, self).__init__(parent)
        self.model = model
        self.percent = percent
        self.calcIntervals()
        buttons = QDialogButtonBox(
                        QDialogButtonBox.Ok,
                        Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        
        layout = QVBoxLayout(self)

        layout.addWidget(self.genIntervalErrorBox())
        layout.addWidget(self.genPercentErrorBox())
        layout.addWidget(buttons)

        self.setWindowTitle("Calculate P")
        self.move(400,400)
        self.show()
    
    def genIntervalErrorBox(self):
        intervalErrorGroupBox = QGroupBox("Estimated Errors based on Intervals Entered (n)", self)
        layout = QVBoxLayout()
        noie = QLabel("{} {}".format("<b>Number of intervals entered:</b>",self.model.n))
        noie.setAlignment(Qt.AlignCenter)
        tedtd = QLabel("{} {}".format("<b>Total Errors Discovered to Date:</b>", self.model.total_failures))
        tedtd.setAlignment(Qt.AlignCenter)
        tep = QLabel("<b>Total Errors Projected:</b> {0:.4f}".format(self.model.a_est))
        tep.setAlignment(Qt.AlignCenter)
        poped = QLabel("<b>Percentage of Projected Errors Discovered :</b> {0:.4f}".format(100.0 * self.model.total_failures / self.model.a_est))
        poped.setAlignment(Qt.AlignCenter)
        layout.addWidget(noie)
        layout.addWidget(tedtd)
        layout.addWidget(tep)
        layout.addWidget(poped)

        intervalErrorGroupBox.setLayout(layout)
        return intervalErrorGroupBox
    
    def genPercentErrorBox(self):
        percentErrorGroupBox = QGroupBox("Estimated Errors based on Percentage (p)", self)
        layout = QVBoxLayout()
        pefe = QLabel("<b>Percentage (p) entered for estimate:</b> {}".format(self.percent))
        intap = QLabel("<b>Intervals needed to achieve p:</b> {0:.4f}".format(self.intervals))
        irantap = QLabel("<b>Intervals remaining after n needed to achieve p:</b> {0:10.4f}".format(self.intervalsRemain))
        layout.addWidget(pefe)
        layout.addWidget(intap)
        layout.addWidget(irantap)
        percentErrorGroupBox.setLayout(layout)
        return percentErrorGroupBox

    def calcIntervals(self):
        numer = math.log(1 - (self.percent / 100))
        term = - numer / self.model.b_est
        self.intervals = math.pow(term, 1/self.model.c_est)
        self.intervalsRemain = self.intervals - self.model.n

class ComputeWidget(QWidget):
    results = PyQt5.QtCore.pyqtSignal(models.Weibull)
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
    taskFinished = PyQt5.QtCore.pyqtSignal(models.Weibull)
    def __init__(self, tVec, kVec):
        super().__init__()
        self.tVec = tVec
        self.kVec = kVec

    def run(self):
        w = models.Weibull(self.kVec, self.tVec)
        self.taskFinished.emit(w)  
