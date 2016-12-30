import datetime as dt

import yaml
#from DatabaseObject import db # singleton
import os
import socket # to get hostname 
import MySQLdb
import sys
from DBCore import *


class Config(object):
    
    config = 0
    dbc = 0
    dbConn =0

    def __init__(self):
        print("creating config object")
        self.dbc = DBCore()
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
        sys.stdout.write("==writeconfigtodb ..")
        self.setConfigItemInDB( 'tempSPLOn', self.config['tempSPLOn'])
        self.setConfigItemInDB( 'tempSPLOff', self.config['tempSPLOff'])
        self.setConfigItemInDB( 'processUptime', self.config['processUptime'])
        self.setConfigItemInDB( 'systemMessage', self.config['systemMessage'])        
        
        self.updateCentralConfigTable() 
        return

    def getItemValueFromConfig(self, item):
        value = self.config[item]
        return value
        

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


    def setConfigItemInDB(self, name, value):
        # Open database connection
        sys.stdout.write("===setconfigitemIndb===")
        
        self.dbConn = self.dbc.getDBConn(self.getItemValueFromConfig('db_hostname'), 
        self.getItemValueFromConfig('db_username'),self.getItemValueFromConfig('db_password'),
        self.getItemValueFromConfig('db_dbname'))
        
        #get db cursor
        self.cursor = self.dbc.getDBCursor(self.dbConn)

        #print("type", type(value))
        if (type(value) is str):
            #value = value
            sys.stdout.write("$string detected$")
        else:
            value=str(value)
        sqlstr = "UPDATE  config SET %s = '%s'" % (name, value)            
        #print("???????????? ", sqlstr)

        self.dbc.execute(self.cursor, sqlstr)
        
        self.dbc.commitClose(self.dbConn)

        return value

    def updateCentralConfigTable(self): #pass config object

        # Open database connection
        sys.stdout.write("===updatecentralconfigtable ===")
        self.dbCentralConn = self.dbc.getDBConn(self.getItemValueFromConfig('central_db_hostname'), self.getItemValueFromConfig('central_db_username'),
                                        self.getItemValueFromConfig('central_db_password'), self.getItemValueFromConfig('central_db_dbname'))

        self.central_cursor = self.dbc.getDBCursor(self.dbCentralConn)
   
        # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % ('tempSPLOn', self.config['tempSPLOn'])
        # Execute the SQL command
        self.dbc.execute(self.central_cursor, sql)        

        # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % ('tempSPLOff', self.config['tempSPLOff'])
        # Execute the SQL command
        self.dbc.execute(self.central_cursor, sql)        
  
        processUptime = self.getItemValueFromConfig('processUptime')
        
        processUptime = self.getConfigItemFromLocalDB('processUptime')
        
        #print("^^^^^^^^^^^^^^^^^^^^^^^ ", processUptime)
        sql = "UPDATE  config SET %s = '%s'" % ('processUptime', processUptime)
        #print(" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ", sql)
        # Execute the SQL command
        self.dbc.execute(self.central_cursor, sql)        

        systemMessage = self.getConfigItemFromLocalDB('systemMessage')
        sql = "UPDATE  config SET %s = '%s'" % ('systemMessage', systemMessage)
        ## Execute the SQL command
        self.dbc.execute(self.central_cursor, sql)        

        # Commit your changes in the database
        self.dbc.commitClose(self.dbCentralConn)

        return


    def getConfigItemFromLocalDB(self, name):
        # Open database connection
        sys.stdout.write("===getConfigItemFromLocalDB===")
        self.dbConn = self.dbc.getDBConn(self.getItemValueFromConfig('db_hostname'), 
        self.getItemValueFromConfig('db_username'),self.getItemValueFromConfig('db_password'),
        self.getItemValueFromConfig('db_dbname'))
        
        #get db cursor
        self.cursor = self.dbc.getDBCursor(self.dbConn)

        sql = "SELECT %s FROM config" % (name)
        
        # Execute the SQL command
        self.dbc.execute(self.cursor, sql)
        
        #try:
            #value = self.cursor.execute(sql)
        #except:
            #print("dberror executing sql query getting setting val from db")
        
        value=self.cursor.fetchone()
        self.dbc.commitClose(self.dbConn)

        #if self.db.open:
            #self.db.close()
            #sys.stdout.write("++ final close ++")
            
        #print("!!!!!!!!!!!!!!!!!!!!!!!!!  ", value,sql)
        return value[0]


