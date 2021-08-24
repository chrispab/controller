import datetime as dt

import yaml
#from DatabaseObject import db # singleton
import os
import socket # to get hostname 
#import MySQLdb
import pymysql.cursors
import sys
from DBCore import *
import logging
logger = logging.getLogger(__name__)

import location
from pathlib import Path


class Config(object):
    
    config = 0
    dbc = 0
    dbConn =0

    def __init__(self):
        logger.info("creating config object")
        # self.dbc = DBCore()
        #write init config from file to db
        self.config = self.readConfigFromFile()
        #self.writeConfigToFile(self.config)

        # self.writeConfigToLocalDB()

        # logger.info("__written temp lon sp to db config__");
        return

    def readConfigFromFile(self):
        # check if custom config has been saved
        cfgZonesFilename = "config_custom_" + location.zoneName + ".yaml"
        path = Path(cfgZonesFilename)
        if path.is_file():
            #read in the config settings
            logger.warning("----------------DETECTED CUSTOM CONFIG FILE---------------")
            #read in custom zones yaml data
            fileStr = os.path.abspath( cfgZonesFilename )
            f = open(fileStr)
            customZoneConfig = yaml.safe_load(f)
            logger.warning(".......................== Reading custom config Zone settings from yaml file ==")
            # logger.warning(yaml.dump(configZones))
            f.close()  
            # print(customZoneConfig)
            logger.warning(customZoneConfig)
            return customZoneConfig


        # else get default config info for this zone - not yet customised config
        cfgZonesFilename = "config_zones.yaml"
        #read in zones yaml data
        fileStr = os.path.abspath( cfgZonesFilename )
        f = open(fileStr)
        configZones = yaml.safe_load(f)
        logger.warning("== Reading config Zone settings from yaml file ==")
        # logger.warning(yaml.dump(configZones))
        f.close()        

        # now get common data and specific data for locations
        cfgLocationsFilename = "config_locations.yaml"
        fileStr = os.path.abspath( cfgLocationsFilename )
        f = open(fileStr)
        configLocations = yaml.safe_load(f)
        logger.warning("== Reading config Location settings from yaml file ==")
        # logger.warning(yaml.dump(configLocations))
        f.close()  
        
           
        
        #get old config style data
        cfgFilename = "config_" + socket.gethostname() + ".yaml"
        logger.info(cfgFilename)
        #fileStr = os.path.abspath( cfgFilename )
        #f = open('/home/pi/controlleroo/config.yaml')
        #f = open(fileStr)
        # use safe_load instead load
        ##config = yaml.safe_load(f)
        logger.warning("==Reading config settings from yaml file==")
        #logger.warning(yaml.dump(config))
        #f.close()

        ################################################################
        # now we have the 3 config structs configLocations and configZones
        # and the old  config
        #lets build a new replacement config struct
        # use location.code to id the section to load
        
        newCfg = {}
        #add common section items to new config obj
        for item in configLocations['common']:
            # print(item)
            # print(configLocations['common'][item])
            newCfg[item] = configLocations['common'][item] # put in new dict
            
        #add location items to new config obj use location.code
        locSection = 'location' + location.code
        for item in configLocations[locSection]:
            # print(item)
            # print(configLocations[locSection][item])
            newCfg[item] = configLocations[locSection][item] # put in new dict
                        
        #add zone items to new config obj use location.zone
        locSection = location.zoneName
        for item in configZones[locSection]:
            # print(item)
            # print(configZones[locSection][item])
            newCfg[item] = configZones[locSection][item] # put in new dict

        return newCfg
        
        
    # def writeConfigToLocalDB(self):
    #     logger.info("== WriteConfigToLocalDB ==")
    #     try:
    #         self.setConfigItemInLocalDB( 'tempSPLOn', self.config['tempSPLOn'])
    #         self.setConfigItemInLocalDB( 'tempSPLOff', self.config['tempSPLOff'])
    #         self.setConfigItemInLocalDB( 'processUptime', self.config['processUptime'])
    #         self.setConfigItemInLocalDB( 'systemMessage', self.config['systemMessage'])        
    #     #            self.updateCentralConfigTable()
    #     except:
    #         logger.error("????? bad writeConfigToLocalDB exception thrown ???")
    #         e = sys.exc_info()[0]
    #         logger.error( "????? Error: %s ?????" % e )
    #     return

    # def updateCentralConfigTable(self):

    #     if (self.getItemValueFromConfig('remoteDBEnabled') == False):
    #         logger.warning("-------------remoteDB DISABLED ------------------------")
    #         return
    #     try:
    #         # Open database connection
    #         logger.debug("=== update central config table ===")
    #         self.dbCentralConn = self.dbc.getDBConn(
    #                                 self.getItemValueFromConfig('central_db_hostname'),
    #                                 self.getItemValueFromConfig('central_db_username'),
    #                                 self.getItemValueFromConfig('central_db_password'),
    #                                 self.getItemValueFromConfig('central_db_dbname')
    #                                 )
                                    
    #         if self.dbCentralConn == 0:
    #             #logger.warning("^^^^^^^^^^^ update central config table Central db conn returned 0 -- exiting ^^^^^^^^^^")
    #             logger.warning("^^^^^^^^^^ update central config table Central db conn returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return 
                

    #         logger.info("getDBConn done OK")
                                    
    #         self.central_cursor = self.dbc.getDBCursor(self.dbCentralConn)
    #         if (self.central_cursor==0):
    #             logger.warning( "^^^^^^^^^^ getdbcursor for update central config tbl tsplonfailed returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return    
                    
    #         # Prepare and execute SQL query to update 'tempSPLOn' in the central db settings table.
    #         sql = "UPDATE  config SET %s = %f" % ('tempSPLOn', self.config['tempSPLOn'])
    #         res = self.dbc.execute(self.central_cursor, sql)
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute for update central config tbl tsplon failed returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return                    
    #         logger.info("update central config: %s", sql)

    
    #         # Prepare SQL query to update a single item in the database settings table.
    #         sql = "UPDATE  config SET %s = %f" % ('tempSPLOff', self.config['tempSPLOff'])
    #         # Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql) 
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl tsploff returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return
    #         logger.info("update central config: %s", sql)
      
    #         #dbInfo = self.getDBConnInfoFromConfig('local')
            
    #         systemUpTime = self.getConfigItemFromLocalDB( 'systemUpTime')            
    #         sql = "UPDATE  config SET %s = '%s'" % ('systemUpTime', systemUpTime)
    #         # Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)  
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl systemUpTime returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)
                        
    #         processUptime = self.getConfigItemFromLocalDB('processUptime')
    #         sql = "UPDATE  config SET %s = '%s'" % ('processUptime', processUptime)
    #         # Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)  
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl puptime returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)

    #         systemMessage = self.getConfigItemFromLocalDB('systemMessage')            
    #         sql = "UPDATE  config SET %s = '%s'" % ('systemMessage', systemMessage)
    #         ## Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl sysmess returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)
        

    #         controllerMessage = self.getConfigItemFromLocalDB('controllerMessage')            
    #         sql = "UPDATE  config SET %s = '%s'" % ('controllerMessage', controllerMessage)
    #         ## Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl sysmess returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)


    #         miscMessage = self.getConfigItemFromLocalDB('miscMessage')            
    #         sql = "UPDATE  config SET %s = '%s'" % ('miscMessage', miscMessage)
    #         ## Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl sysmess returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)
                        
    #         lightState = self.getConfigItemFromLocalDB('lightState')
    #         sql = "UPDATE  config SET %s = %i" % ('lightState', lightState)
    #         ## Execute the SQL command
    #         res = self.dbc.execute(self.central_cursor, sql)
    #         if (res==0):
    #             logger.warning( "^^^^^^^^^^ execute query update central config tbl lightstae returned 0 ^^^^^^^^^^^^^^^^")
    #             logger.warning( "..........................returning..........................")
    #             return             
    #         logger.info("update central config: %s", sql)
            
                
    #         # Commit changes in the database
    #         self.dbc.commitClose(self.dbCentralConn)
            
    #     except:
    #         logger.error("????? bad update_central_db exception thrown ???")
    #         e = sys.exc_info()[0]
    #         logger.error( "????? Error: %s ?????" % e )

    #     return

    def getItemValueFromConfig(self, item):
        value = self.config[item]
        return value
        
    def setItemValueToConfig(self, item, value):
        self.config[item] = value
        # return value
        return


    def writeConfigToFile(self):
        fileStr = os.path.abspath("config_custom_" + location.zoneName + ".yaml")
        f = open(fileStr, "w")
        logger.info("----------------------------==Writing config settings to new yaml file config_zoneN.yaml==")
        yaml.dump(self.config, f)
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
        
    # def getDBConnInfoFromConfig(self, dbName):
    #     logger.warning("Get DB Conn Info for : %s", dbName)
    #     if (dbName == 'local'):
    #         dbInfo['db_hostname'] = cfg.getItemValueFromConfig('db_hostname')
    #         dbInfo['db_username'] = cfg.getItemValueFromConfig('db_username')
    #         dbInfo['db_password'] = cfg.getItemValueFromConfig('db_password')
    #         dbInfo['db_dbname'] = cfg.getItemValueFromConfig('db_dbname')
    #     elif (dbName == 'central'):
    #         dbInfo['db_hostname'] = cfg.getItemValueFromConfig('central_db_hostname')
    #         dbInfo['db_username'] = cfg.getItemValueFromConfig('central_db_username')
    #         dbInfo['db_password'] = cfg.getItemValueFromConfig('central_db_password')
    #         dbInfo['db_dbname'] = cfg.getItemValueFromConfig('central_db_dbname')
            
    #     return dbInfo


    # def setConfigItemInLocalDB(self, name, value):
    #     #logger.warning("name : %s" % (name))
    #     #logger.warning("value : %s" % (value))
    #     try:
    #         # Open database connection
    #         #logger.warning("===setconfigitemInLocaldb===")
            
    #         self.dbConn = self.dbc.getDBConn(self.getItemValueFromConfig('db_hostname'), 
    #                         self.getItemValueFromConfig('db_username'),
    #                         self.getItemValueFromConfig('db_password'),
    #                         self.getItemValueFromConfig('db_dbname'))
            
    #         #get db cursor
    #         #logger.warning("???????????? pre get cursor")
    #         #logger.warning("???????????? dbconn = %s" % self.dbConn)

    #         self.cursor = self.dbc.getDBCursor(self.dbConn)
    #         #logger.warning("???????????? post get cursor")

    #         #print("type", type(value))
    #         if (type(value) is str):
    #             #value = value
    #             logger.info("$string detected$")
    #         else:
    #             value=str(value)
    #         sqlstr = "UPDATE  config SET %s = '%s'" % (name, value)            
    #         #logger.warning("???????????? %s " % sqlstr)
    
    #         self.dbc.execute(self.cursor, sqlstr)
            
    #         self.dbc.commitClose(self.dbConn)
    #     except:
    #         logger.error("????? bad setConfigItemInLocalDB exception thrown ???")
    #         e = sys.exc_info()[0]
    #         logger.error( "????? Error: %s ?????" % e )

    #     return



    # def getConfigItemFromDB(self, db, itemNname):
    #     try:
    #         # Open database connection
    #         logger.info("===getConfigItemFromDB===")
    #         self.dbConn = self.dbc.getDBConn(db['db_hostname'], 
    #                         db['db_username'], db['db_password'],
    #                         db['db_dbname'])
            
    #         #get db cursor
    #         self.cursor = self.dbc.getDBCursor(self.dbConn)
    
    #         # Execute the SQL command
    #         sql = "SELECT %s FROM config" % (itemName)
    #         self.dbc.execute(self.cursor, sql)
                        
    #         value=self.cursor.fetchone()
    #         self.dbc.commitClose(self.dbConn)
    #     except:
    #         logger.error("????? bad getConfigItemFromDB ???")
    #         e = sys.exc_info()[0]
    #         logger.error( "????? Error: %s ?????" % e )
            
    #     return value[0]
        
        
    def getConfigItemFromLocalDB(self, name):
        value=[1]
        value[0]=1
        try:
            # Open database connection
            logger.info("===getConfigItemFromLocalDB===")
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
            logger.error("????? bad update_central_db exception thrown ???")
            e = sys.exc_info()[0]
            logger.error( "????? Error: %s ?????" % e )
            #value[0]=1
            
        return value[0]
