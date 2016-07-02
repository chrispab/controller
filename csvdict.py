import csv

#----------------------------------------------------------------------

def csv_dict_reader(file_obj):

    """

    Read a CSV file using csv.DictReader

    """

    reader = csv.DictReader(file_obj, delimiter=',')

    for line in reader:

        print(line["temperature"]),

        print(line["humidity"])

#----------------------------------------------------------------------

if __name__ == "__main__":

    with open("/home/pi/projects/controller1/thdata.csv") as f_obj:

        csv_dict_reader(f_obj)
