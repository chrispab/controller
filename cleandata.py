#To be able to read csv formated files, we will first have to import the
#csv module.
import csv

csvfilename = '/home/pi/projects/controller1/thdata.csv'
csv_path = "/home/pi/projects/controller1/thdata.csv"
oppath = "/home/pi/projects/controller1/thdatacleaned.csv"

import csv

#----------------------------------------------------------------------

def csv_reader(file_obj):

    """

    Read a csv file

    """

    reader = csv.reader(file_obj)
    csv_file = open(oppath, "wb")
    writer = csv.writer(csv_file, delimiter=',')
    #with open(path, "wb") as csv_file:

    for row in reader:

#        print(",".join(row))
        if (float(row[1]) > 35.0) or (float(row[1]) < 10.0) or (float(row[2]) > 100.0) or (float(row[2]) < 20.0):
            print('skipping row ',row)
        else:
            #write row back to new file
            #with open(oppath, "wb") as csv_file:
            writer.writerow(row)
    print(oppath, "written to disk")
            


def csv_writer(data, path):

    """

    Write data to a CSV file path

    """

    with open(path, "wb") as csv_file:

        writer = csv.writer(csv_file, delimiter=',')

        for line in data:

            writer.writerow(line)


#----------------------------------------------------------------------

if __name__ == "__main__":


    with open(csv_path, "rb") as f_obj:

        csv_reader(f_obj)
        
        
        
        #with open(csvfilename, 'rb') as f:
    #reader = csv.reader(f)
    #for row in reader:
        #print row
        
        
        #with open('/home/pi/projects/controller1/thdata.csv', 'r') as f:
        #data = list(reader(f))
    
    ##listlen = len(data)
    #startsample = 1

    #labels = [i[0] for i in data[startsample::]]
    #tempvalues = [i[1] for i in data[startsample::]]
    #humivalues = [i[2] for i in data[startsample::]]
    #heatervalues = [i[3] for i in data[startsample::]]
    #ventvalues = [i[4] for i in data[startsample::]]
    #fanvalues = [i[5] for i in data[startsample::]]
