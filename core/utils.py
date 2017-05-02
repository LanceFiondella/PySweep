import csv
import openpyxl
from openpyxl import Workbook

def export_data(data, filename):
    with open(filename[0],'w') as f:
        for col,d in enumerate(data):
            f.write("{}\n".format(','.join(map(str, d))))

def import_data(filename):
    rows = []
    data = []
    with open(filename[0],'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            rows.append(row)
    data = [x for x in rows]
    return data

def import_excel(filename):
    wb = openpyxl.load_workbook(filename)
    for name in wb.get_sheet_names():
        if "Mode1" in name:
            print("Import mode1 data")
            worksheet = wb.get_sheet_by_name(name)
            for row in worksheet.rows:
                print(row[1].value)
        

class GlobalData():
    def __init__(self):
        #Define input data
        #The inputs/output for each mode will have labels of the format modex where x is the mode number
        self.input = {}
        
        #Define output data
        self.output = {}

        


    def import_input_csv(self, filename, mode):
        rows = []
        data = []
        with open(filename[0],'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                rows.append(row)
        data = [x for x in rows]
        self.input[mode] = data
        return data

    def export_input_csv(self, mode, filename):
        data = self.input[mode]
        with open(filename[0],'w') as f:
            for col,d in enumerate(data):
                f.write("{}\n".format(','.join(map(str, d))))

    def import_input_excel(self, filename):
            wb = openpyxl.load_workbook(filename)
            for name in wb.get_sheet_names():
                worksheet = wb.get_sheet_by_name(name)
                data = []
                if "mode1" in name.lower():
                    self.input['mode1'] = {}
                    self.input['mode1']['tVec'] = []
                    self.input['mode1']['kVec'] = []
                    for row in worksheet.rows:
                        try:
                            self.input['mode1']['tVec'].append(int(row[0].value))
                            self.input['mode1']['kVec'].append(int(row[1].value))
                        except:
                            pass
                elif "mode2" in name.lower():
                    self.input['mode2'] = {}
                    self.input['mode2']['names'] = []
                    self.input['mode2']['values'] = []
                    for row in worksheet.rows:
                        try:
                            self.input['mode2']['values'].append(int(row[1].value))
                            self.input['mode2']['names'].append(row[0].value)
                        except:
                            pass
                elif "mode3" in name.lower():
                    self.input['mode3'] = {}
                    self.input['mode3']['names'] = []
                    self.input['mode3']['values'] = []
                    for row in worksheet.rows:
                        try:
                            self.input['mode3']['values'].append(int(row[1].value))
                            self.input['mode3']['names'].append(row[0].value)
                        except:
                            pass
                elif "mode4" in name.lower():
                    self.input['mode4'] = {}
                    self.input['mode4']['names'] = []
                    self.input['mode4']['values'] = []
                    for row in worksheet.rows:
                        try:
                            self.input['mode4']['values'].append(float(row[1].value))
                            self.input['mode4']['names'].append(row[0].value)
                        except:
                            pass
                    


if __name__=="""__main__""":
    gd = GlobalData()
    gd.import_input_excel('../input.xlsx')