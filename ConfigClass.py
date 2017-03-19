import datetime as dt

import yaml
#from DatabaseObject import db # singleton
import os
import socket # to get hostname 
import MySQLdb
import pymysql.cursors
import sys
from DBCore import *
import logging


class Config(object):
    
    config = 0
    dbc = 0
    dbConn =0

    def __init__(self):
        logging.info("creating config object")
        self.dbc = DBCore()
        #write init config from file to db
        self.config = self.readConfigFromFile()
        #self.writeConfigToFile(self.config)

        self.writeConfigToLocalDB()

        logging.info("__written temp lon sp to db config__");
        return

    def readConfigFromFile(self):
        cfgFilename = "config_" + socket.gethostname() + ".yaml"
        logging.info(cfgFilename)
        fileStr = os.path.abspath( cfgFilename )
        #f = open('/home/pi/controlleroo/config.yaml')
        f = open(fileStr)
        # use safe_load instead load
        config = yaml.safe_load(f)
        logging.info("==Reading config settings from yaml file==")
        logging.info(yaml.dump(config))
        f.close()

        return config
        
    def writeConfigToLocalDB(self):
        logging.info("== WriteConfigToLocalDB ==")
        try:
            self.setConfigItemInLocalDB( 'tempSPLOn', self.config['tempSPLOn'])
            self.setConfigItemInLocalDB( 'tempSPLOff', self.config['tempSPLOff'])
            self.setConfigItemInLocalDB( 'processUptime', self.config['processUptime'])
            self.setConfigItemInLocalDB( 'systemMessage', self.config['systemMessage'])        
#            self.updateCentralConfigTable()
        except:
            logging.error("????? bad setConfigItemInDB exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )
        return

    def updateCentralConfigTable(self):
        try:
            # Open database connection
            logging.warning("=== update central config table ===")
            self.dbCentralConn = self.dbc.getDBConn(
                                    self.getItemValueFromConfig('central_db_hostname'),
                                    self.getItemValueFromConfig('central_db_username'),
                                    self.getItemValueFromConfig('central_db_password'),
                                    self.getItemValueFromConfig('central_db_dbname')
                                    )
                                    
            if self.dbCentralConn == 0:
                #logging.warning("^^^^^^^^^^^ update central config table Central db conn returned 0 -- exiting ^^^^^^^^^^")
                logging.warning("^^^^^^^^^^ update central config table Central db conn returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return 
                

            logging.info("getDBConn done OK")
                                    
            self.central_cursor = self.dbc.getDBCursor(self.dbCentralConn)
            if (self.central_cursor==0):
                logging.warning( "^^^^^^^^^^ getdbcursor for update central config tbl tsplonfailed returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return    
                    
            # Prepare and execute SQL query to update 'tempSPLOn' in the central db settings table.
            sql = "UPDATE  config SET %s = %f" % ('tempSPLOn', self.config['tempSPLOn'])
            res = self.dbc.execute(self.central_cursor, sql)
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute for update central config tbl tsplon failed returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return                    
            logging.info("update central config: %s", sql)

    
            # Prepare SQL query to update a single item in the database settings table.
            sql = "UPDATE  config SET %s = %f" % ('tempSPLOff', self.config['tempSPLOff'])
            # Execute the SQL command
            res = self.dbc.execute(self.central_cursor, sql) 
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute query update central config tbl tsploff returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return
            logging.info("update central config: %s", sql)
      
            #dbInfo = self.getDBConnInfoFromConfig('local')
            
            systemUpTime = self.getConfigItemFromLocalDB( 'systemUpTime')            
            sql = "UPDATE  config SET %s = '%s'" % ('systemUpTime', systemUpTime)
            # Execute the SQL command
            res = self.dbc.execute(self.central_cursor, sql)  
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute query update central config tbl systemUpTime returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return             
            logging.info("update central config: %s", sql)
                        
            processUptime = self.getConfigItemFromLocalDB('processUptime')
            sql = "UPDATE  config SET %s = '%s'" % ('processUptime', processUptime)
            # Execute the SQL command
            res = self.dbc.execute(self.central_cursor, sql)  
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute query update central config tbl puptime returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return             
            logging.info("update central config: %s", sql)

            systemMessage = self.getConfigItemFromLocalDB('systemMessage')            
            sql = "UPDATE  config SET %s = '%s'" % ('systemMessage', systemMessage)
            ## Execute the SQL command
            res = self.dbc.execute(self.central_cursor, sql)
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute query update central config tbl sysmess returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return             
            logging.info("update central config: %s", sql)
        
            lightState = self.getConfigItemFromLocalDB('lightState')
            sql = "UPDATE  config SET %s = %i" % ('lightState', lightState)
            ## Execute the SQL command
            res = self.dbc.execute(self.central_cursor, sql)
            if (res==0):
                logging.warning( "^^^^^^^^^^ execute query update central config tbl lightstae returned 0 ^^^^^^^^^^^^^^^^")
                logging.warning( "..........................returning..........................")
                return             
            logging.info("update central config: %s", sql)
            
                
            # Commit changes in the database
            self.dbc.commitClose(self.dbCentralConn)
            
        except:
            logging.error("????? bad update_central_db exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )

        return

    def getItemValueFromConfig(self, item):
        value = self.config[item]
        return value
        

    def writeConfigToFile(self, config):
        fileStr = os.path.abspath("config_new.yaml")
        f = open(fileStr, "w")
        logging.info("==Writing config settings to new yaml file config_new.yaml==")
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
        
    def getDBConnInfoFromConfig(self, dbName):
        logging.warning("Get DB Conn Info for : %s", dbName)
        if (dbName == 'local'):
            dbInfo['db_hostname'] = cfg.getItemValueFromConfig('db_hostname')
            dbInfo['db_username'] = cfg.getItemValueFromConfig('db_username')
            dbInfo['db_password'] = cfg.getItemValueFromConfig('db_password')
            dbInfo['db_dbname'] = cfg.getItemValueFromConfig('db_dbname')
        elif (dbName == 'central'):
            dbInfo['db_hostname'] = cfg.getItemValueFromConfig('central_db_hostname')
            dbInfo['db_username'] = cfg.getItemValueFromConfig('central_db_username')
            dbInfo['db_password'] = cfg.getItemValueFromConfig('central_db_password')
            dbInfo['db_dbname'] = cfg.getItemValueFromConfig('central_db_dbname')
            
        return dbInfo


    def setConfigItemInLocalDB(self, name, value):
        try:
            # Open database connection
            logging.info("===setconfigitemIndb===")
            
            self.dbConn = self.dbc.getDBConn(self.getItemValueFromConfig('db_hostname'), 
                            self.getItemValueFromConfig('db_username'),
                            self.getItemValueFromConfig('db_password'),
                            self.getItemValueFromConfig('db_dbname'))
            
            #get db cursor
            self.cursor = self.dbc.getDBCursor(self.dbConn)
    
            #print("type", type(value))
            if (type(value) is str):
                #value = value
                logging.info("$string detected$")
            else:
                value=str(value)
            sqlstr = "UPDATE  config SET %s = '%s'" % (name, value)            
            #print("???????????? ", sqlstr)
    
            self.dbc.execute(self.cursor, sqlstr)
            
            self.dbc.commitClose(self.dbConn)
        except:
            logging.error("????? bad setConfigItemInDB exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )

        return



    def getConfigItemFromDB(self, db, itemNname):
        try:
            # Open database connection
            logging.info("===getConfigItemFromDB===")
            self.dbConn = self.dbc.getDBConn(db['db_hostname'], 
                            db['db_username'], db['db_password'],
                            db['db_dbname'])
            
            #get db cursor
            self.cursor = self.dbc.getDBCursor(self.dbConn)
    
            # Execute the SQL command
            sql = "SELECT %s FROM config" % (itemName)
            self.dbc.execute(self.cursor, sql)
                        
            value=self.cursor.fetchone()
            self.dbc.commitClose(self.dbConn)
        except:
            logging.error("????? bad getConfigItemFromDB ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )
            
        return value[0]
        
        
    def getConfigItemFromLocalDB(self, name):
        value=[1]
        value[0]=1
        try:
            # Open database connection
            logging.info("===getConfigItemFromLocalDB===")
            self.dbConn = self.dbc.getDBConn(self.getItemValueFromConfig('db_hostname'), 
            self.getItemValueFromConfig('db_username'),self.getItemValueFromConfig('db_password'),
            self.getItemValueFromConfig('db_dbname'))
            
            #get db cursor
            self.cursor = self.dbc.getDBCursor(self.dbConn)
    
            # Execute the SQL command
            sql = "SELECT %s FROM config" % (name)
            self.dbc.execute(self.cursor, sql)
                        
            value=self.cursor.fetchone()
            self.dbc.commitClose(self.dbConn)
        except:
            logging.error("????? bad update_central_db exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )
            #value[0]=1
            
        return value[0]
