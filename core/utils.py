import csv

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

class GlobalData():
    def __init__(self):
        #Define input data
        #The inputs/output for each mode will have labels of the format modex where x is the mode number
        self.input = {}
        
        #Define output data
        self.output = {}
