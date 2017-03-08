import csv

def export_data(data, filename):
    with open(filename[0],'w') as f:
        for i,d in enumerate(data):
            f.write("{},{}\n".format(i+1,d))

def import_data(filename):
    rows = []
    data = []
    with open(filename[0],'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            rows.append(row)
    if len(rows) == 1:
        print("Split the first row as errors")
    else:
        data = [x[1] for x in rows]
    return data