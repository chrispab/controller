import datetime as dt

import yaml
#from DatabaseObject import db # singleton
import os
import socket # to get hostname 
import MySQLdb
import sys



class Config(object):


    def __init__(self):
        print("creating config object")
        #write init config from file to db
        self.config = self.readConfigFromFile()
        #self.writeConfigToFile(self.config)

        self.writeConfigToDB()

        print("__written temp lon sp to db config__");
        return

    def readConfigFromFile(self):
        cfgFilename = "config_" + socket.gethostname() + ".yaml"
        print(cfgFilename)
        fileStr = os.path.abspath( cfgFilename )
        #f = open('/home/pi/controlleroo/config.yaml')
        f = open(fileStr)
        # use safe_load instead load
        config = yaml.safe_load(f)
        print("==Reading config settings from yaml file==")
        print yaml.dump(config)
        f.close()
        #self.config = config
        
        #print("$$$$$$$$$$$$$$$$$$$$$$$$$$$: ",os.path.abspath( cfgFilename ))
        
        return config
        
    def writeConfigToDB(self):
        print("==Writing settings to db ..")
        self.setConfigItemInDB( 'tempSPLOn', self.config['tempSPLOn'])
        self.setConfigItemInDB( 'tempSPLOff', self.config['tempSPLOff'])
        self.updateCentralConfigTable(self.config) 
        return
        
    #def setConfigItemInDB(self, name, value):
        #self.setConfigItem(name, value)
        #return
        
    def getConfigItemFromDB(self, name, value):
        return value
        
    def getItemValue(self, item):
        value = self.config[item]
        return value
        
    def readConfigFromDB(self):
        config = 1
        return config



    def writeConfigToFile(self, config):
        fileStr = os.path.abspath("config_new.yaml")
        f = open(fileStr, "w")
        print("==Writing config settings to new yaml file config_new.yaml==")
        yaml.dump(config, f)
        f.close()
        return

    def getTOn(self):
        hrs = int(float(self.config['lightOnT'][0:2]))
        mins = int(float(self.config['lightOnT'][3:5]))
        return dt.time(hrs,mins)

    def getTOff(self):
        hrs = int(float(self.config['lightOffT'][0:2]))
        mins = int(float(self.config['lightOffT'][3:5]))
        return dt.time(hrs,mins)
        ##################################################################################
        ###############################################################################

    def getConfigItem(self, name):
        # Open database connection
        print("===trying to connect for setconfigitem in db===")
        try:
            self.db = MySQLdb.connect(
                self.getItemValue('db_hostname'), self.getItemValue('db_username'), self.getItemValue('db_password'), self.getItemValue('db_dbname'))
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        sys.stdout.write("===connected-")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

        sql = "SELECT %s FROM config ORDER BY id DESC LIMIT 1" % (name)
        
        # Execute the SQL command
        try:
            value = self.cursor.execute(sql)
        except:
            print("dberror executing sql query getting setting val from db")

        if self.db.open:
            self.db.close()
            print("++ final close ++")

        return


    def setConfigItemInDB(self, name, value):
        # Open database connection
        print("===trying to connect for setconfigitem in db===")
        try:
            self.db = MySQLdb.connect(
                self.getItemValue('db_hostname'), self.getItemValue('db_username'), self.getItemValue('db_password'), self.getItemValue('db_dbname'))
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        sys.stdout.write("===connected..")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

            # Prepare SQL query to update a single item in the database settings table.
        #sql = "UPDATE  config SET %s = %d" % (name, value)

        #sql = "UPDATE  config SET %s = %f" % (name, value)

        #sql = "UPDATE  config SET %s = %s"
        # % (name, value)
        print("type", type(value))
        if (type(value) is str):
            #value = value
            print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWW string WWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
        else:
            value=str(value)
        sqlstr = "UPDATE  config SET %s = '%s'" % (name, value)            
        #sqlstr = "UPDATE config SET " + name +" = " + value
        print("?????????????????   ", sqlstr)
        #sql = "UPDATE config SET (name) VALUES (value)"
        #cur.execute("INSERT INTO Writers(Name) VALUES('Jack London')")
        # Execute the SQL command
        
        #query = """ UPDATE  config SET %s = %s """
 
        #data = (name, value)
    
    
        try:
            self.cursor.execute(sqlstr)
            #self.cursor.execute(query, data)

        except MySQLdb.Error, e:
            print("dberror executing sql query")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        sys.stdout.write("executing sql..")

        # Commit your changes in the database
        try:
            self.db.commit()
            sys.stdout.write("committed-")

            # disconnect from server
            sys.stdout.write("ready for closing-")
        except MySQLdb.Error, e:
            try:
                self.db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.db.open:
                self.db.close()
                print("++ final close ++")

        return value


    def writedb(self, sample_dt, temperature, humidity, heaterstate, ventstate, fanstate):
        # Open database connection
        print("===about to try writing record to db..trying to connect===")
        try:
            self.db = MySQLdb.connect(
                self.getItemValue('db_hostname'), self.getItemValue('db_username'), self.getItemValue('db_password'), self.getItemValue('db_dbname'))
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        sys.stdout.write("===connected-")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

            # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO thdata(sample_dt, \
            temperature, humidity, heaterstate, ventstate, fanstate) \
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s' )" % \
            (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate)
        # Execute the SQL command
        try:
            self.cursor.execute(sql)
        except:
            print("dberror executing sql query")
        sys.stdout.write("===executing sql-")

        # Commit your changes in the database
        try:
            self.db.commit()
            sys.stdout.write("===committed-")

            # disconnect from server
            sys.stdout.write("ready for closing-")
        except MySQLdb.Error, e:
            try:
                self.db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.db.open:
                self.db.close()
                print("++ final close ++")

        self.update_central_db()    # sync local recs update to central db

        return


    def updateCentralConfigTable(self, config): #pass config object

        print("===try to update config table from local db to central. trying to connect to central server===")
        # Open database connection
        try:
            self.central_db = MySQLdb.connect(self.getItemValue('central_db_hostname'), self.getItemValue('central_db_username'),
                                              self.getItemValue('central_db_password'), self.getItemValue('central_db_dbname'), connect_timeout=15)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
            print("returning 1")
            return
        sys.stdout.write("===connected-")

        # prepare a cursor object using cursor() method
        try:
            self.central_cursor = self.central_db.cursor()
        except:
            print("dberror getting cursor")
            
        #######################################    
        # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % ('tempSPLOn', config['tempSPLOn'])
        # Execute the SQL command
        try:
            self.central_cursor.execute(sql)
        except:
            print("dberror executing sql query")
        sys.stdout.write("executing sql-")
        
        # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % ('tempSPLOff', config['tempSPLOff'])
        # Execute the SQL command
        try:
            self.central_cursor.execute(sql)
        except:
            print("dberror executing sql query")
        sys.stdout.write("executing sql-")
        ##############################################


        # Commit your changes in the database
        try:
            self.central_db.commit()
            sys.stdout.write("committed-")

            # disconnect from server
            sys.stdout.write("ready for closing-")
        except MySQLdb.Error, e:
            try:
                self.central_db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.central_db.open:
                self.central_db.close()
                print("++ final close ++")

        return


    def update_central_db(self):
        
        print("===try batch update from local db to central db--trying to connect to central server===")
        # Open database connection
        try:
            self.central_db = MySQLdb.connect(self.getItemValue('central_db_hostname'), self.getItemValue('central_db_username'),
                                              self.getItemValue('central_db_password'), self.getItemValue('central_db_dbname'), connect_timeout=15)

        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
            print("returning 1")
            return
        sys.stdout.write("===connected-")

        # prepare a cursor object using cursor() method
        try:
            self.central_cursor = self.central_db.cursor()
        except:
            print("dberror getting cursor")

        # Prepare SQL query to get timestamp of last record in the central
        # database.
        sql = "SELECT sample_dt FROM thdata ORDER BY id DESC LIMIT 1"
        try:
            last_sample_time = self.central_cursor.execute(sql)
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            #last_sample_time
##############################################################################################
##############################################################################################
        sys.stdout.write("last sample time from central db: %s - " % (last_sample_time) )
        row = self.central_cursor.fetchone()    # get result if any
        sys.stdout.write("row :%s - " % (row))

        if row > 0:
            sys.stdout.write("last sample time: %s - " % (row[0]) )
            last_sample_time = row[0]
        if row == None:
            last_sample_time = "2016-11-01 00:00:00"

        # now get samples from local db with timestamp > last sample time on
        # central db
        sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt >= '%s'" % last_sample_time
        #sys.stdout.write (sql)
        # get rs from local db
        try:
            self.local_db = MySQLdb.connect(
                self.getItemValue('db_hostname'), self.getItemValue('db_username'), self.getItemValue('db_password'), self.getItemValue('db_dbname'))
        except MySQLdb.Error, e:
            print("error connecting to local dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        sys.stdout.write("===connected-")

        # prepare a cursor object using cursor() method
        try:
            self.local_cursor = self.local_db.cursor()
        except:
            print("dberror getting cursor")

        try:
            rs_to_update_central_db = self.local_cursor.execute(sql)
            rs_to_update_central_db = list(self.local_cursor.fetchall())
            print(rs_to_update_central_db)
            # rs_to_update_central_db)
            sys.stdout.write("data got from local server - in list ready to upload-")
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])

        sys.stdout.write("executing sql to update to remote db to sync with local db=")
        # if rs_to_update_central_db.count > 0:    #if there are records to add
        # to central db
        if self.local_cursor.rowcount > 0:  # if there are records to add to central db
           # update central db
            try:
                # Prepare SQL query to INSERT a record into the database.
                sql = "INSERT INTO thdata (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) \
                 VALUES (%s, %s, %s, '%s', '%s', '%s' )"
                self.central_cursor.executemany(sql, rs_to_update_central_db)
                self.central_db.commit()
                self.central_db.close()
            except MySQLdb.Error, e:
                print("error updating central db dberror")
                print "dberror Error %d: %s" % (e.args[0], e.args[1])
            sys.stdout.write("===connected-")

            # Commit your changes in the database
        try:
            self.local_db.commit()
            sys.stdout.write("committed-")

            # disconnect from server
            sys.stdout.write("ready for closing-")
        except MySQLdb.Error, e:
            try:
                self.local_db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.local_db.open:
                self.local_db.close()
                print("++ final close ++")

        return

