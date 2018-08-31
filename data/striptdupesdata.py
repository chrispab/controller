# To be able to read csv formated files, we will first have to import the
# csv module.
import csv

csvfilename = '/home/pi/projects/controller1/thdata.csv'
csv_path = "/home/pi/projects/controller1/thdata.csv"
oppath = "/home/pi/projects/controller1/thdatacleaned.csv"

import csv


def csv_reader(file_obj):

    reader = csv.reader(file_obj)
    csv_file = open(oppath, "wb")
    writer = csv.writer(csv_file, delimiter=',')

    dupe = False
    row = next(reader)  # get 1st row
    while row:
        print('reading row :', row)
        # for row in reader:
        # if dupe == True:
        try:
            nextRow = next(reader)
            print('next    row :', nextRow)
            dupe = False
            # while ( (row[1] == nextRow[1]) and (row[3] == nextRow[3]) and (row[4] == nextRow[4]) and (row[5] == nextRow[5]) ):
            if ((row[1] == nextRow[1]) and (row[3] == nextRow[3]) and (row[4] == nextRow[4]) and (row[5] == nextRow[5])):
                print('dupe1 row  : ', row)
                print('dupe2 row  : ', nextRow)
                dupe = True

            #nextRow = next(reader)
            if dupe == True:
                row = nextRow

            if dupe == False:
                print('writing row :', row)
                print ('-')
                writer.writerow(row)
                row = nextRow

        except:
            csv_file.close()
            print(oppath, "written to disk after iter exception")
            break
        # finally:
            #print(oppath, "written to disk")

    print(oppath, "written to disk")


def csv_writer(data, path):

    with open(path, "wb") as csv_file:

        writer = csv.writer(csv_file, delimiter=',')

        for line in data:

            writer.writerow(line)


# ----------------------------------------------------------------------

if __name__ == "__main__":

    with open(csv_path, "rb") as f_obj:

        csv_reader(f_obj)

        # with open(csvfilename, 'rb') as f:
    #reader = csv.reader(f)
    # for row in reader:
        #print row

        # with open('/home/pi/projects/controller1/thdata.csv', 'r') as f:
        #data = list(reader(f))

    ##listlen = len(data)
    #startsample = 1

    #labels = [i[0] for i in data[startsample::]]
    #tempvalues = [i[1] for i in data[startsample::]]
    #humivalues = [i[2] for i in data[startsample::]]
    #heatervalues = [i[3] for i in data[startsample::]]
    #ventvalues = [i[4] for i in data[startsample::]]
    #fanvalues = [i[5] for i in data[startsample::]]
