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