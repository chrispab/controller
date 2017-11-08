#import MySQLdb
import pymysql.cursors
import sys
from DBCore import *
import logging

import datetime

logger = logging.getLogger(__name__)

from ConfigObject import cfg # singleton global

class Database(object):

    def __init__(self):
        logger.info("Creating db object")
        self.dbc = DBCore()
        return

        
    def writeSampleToLocalDB(self, sample_dt, temperature, humidity, heaterstate, ventstate, fanstate):

        # Open database connection
        try:
            logger.warning("=== write Sample To Local DB ===")
            self.dbConn = self.dbc.getDBConn(cfg.getItemValueFromConfig('db_hostname'), 
                            cfg.getItemValueFromConfig('db_username'), 
                            cfg.getItemValueFromConfig('db_password'),
                            cfg.getItemValueFromConfig('db_dbname'))        
            # prepare a cursor object using cursor() method
            self.cursor = self.dbc.getDBCursor(self.dbConn)
    
            # Prepare SQL query to INSERT a record into the database.
            sql = "INSERT INTO thdata(sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) VALUES ('%s', '%s', '%s', '%s', '%s', '%s' )" % (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate)
            # Execute the SQL command
            self.dbc.execute(self.cursor, sql)
    
            # Commit your changes in the database
            self.dbc.commitClose(self.dbConn)
    
            #self.update_central_db()    # sync local recs update to central db
        
        except:
            logger.error("????? bad writeSampleToLocalDB exception thrown ???")
            e = sys.exc_info()[0]
            logger.error( "????? Error: %s ?????" % e )
            
        return


    def update_central_db(self):

        logger.warning("=== update_central_db - samples ===")
        # Open database connection
        logger.info("111 pre get cent db conn")
        centralDBHostName = cfg.getItemValueFromConfig('central_db_hostname')
        centralDBUserName = cfg.getItemValueFromConfig('central_db_username')
        centralDBPassword = cfg.getItemValueFromConfig('central_db_password')
        centralDBDBName = cfg.getItemValueFromConfig('central_db_dbname')
        logger.info("222 got db string params")
        
        
        try:
            #time central get last sample time routine
            time1 = datetime.datetime.now()
            #cfg.updateCentralConfigTable()
            self.dbConnCentral = self.dbc.getDBConn(centralDBHostName,
                                                    centralDBUserName,
                                                    centralDBPassword,
                                                    centralDBDBName)
            logger.info("333 got db connection")
            if (self.dbConnCentral==0):                
                logger.warning("^^^^^^^^^^ dbconncentral error returned 0 ^^^^^^^^^^^^^^^^")
                logger.warning("..........................returning..........................")
                return
            
            self.cursorCentral = self.dbc.getDBCursor(self.dbConnCentral)
            if (self.cursorCentral==0):
                self.dbc.close(self.dbConnCentral)
                logger.warning( "^^^^^^^^^^ getdbcursor for central db failed returned 0 ^^^^^^^^^^^^^^^^")
                logger.warning("..........................returning..........................")
                return            
            
            logger.info("222 post get cent db conn")
            
            # Prepare and execute SQL query to get timestamp of last record in the central database.
            #ensure returned value includes the fracyional millisecs part .000 etc
            # using date format here ensures if fractional is .000 this is retrieved correctly
            # previously time with .000 was truncated
            sql = "SELECT DATE_FORMAT(sample_dt, '%Y-%m-%d %H:%i:%S.%f') FROM thdata ORDER BY id DESC LIMIT 1"
            
            
            res = self.dbc.execute(self.cursorCentral, sql)
            if (res==0):
                self.dbc.close(self.dbConnCentral)
                logger.warning("^^^^^^^^^^ execute query error returned 0 ^^^^^^^^^^^^^^^^")
                logger.warning("..........................returning..........................")
                return
            
            logger.warning("get last sample time from central sql: %s" % (sql) )
            
            #do what with empty set - e.g at start when central table is empty eg last sample time = 0
            #get the actual record containing the dattime 
            # logger.warning("--- rowcount 1 : %s ---" % self.cursorCentral.rowcount)
            
            # just get the one record which should be the datre time 
            result = self.cursorCentral.fetchone()
            if (result == None): # returns None if no data avail 
                last_sample_time = "2017-01-01 00:00:00.000"
                logger.warning("-- No last sample in central db so set time of last to long ago: %s" % last_sample_time)                            
            else: #  rowcount != 0
                # logger.warning("--- rowcount 2 : %s ---" % self.cursorCentral.rowcount)                
                
                #row = self.cursorCentral.fetchone()    # get row of data
                row = result
                logger.warning("--- row    : %s ---" % row)
                logger.warning("--- row[0] : %s ---" % row[0])
                #print(row[0])                
                
                #logger.warning("row[0] :%s " % (row[0]))
                #logger.warning("last sample time: %s - " % (row[0]) )
                
                
                #last_sample_time = strftime("%Y-%m-%d %H:%M:%S.%f", row[0])
                last_sample_time = row[0]
                
                if row[0] == None: #REDUNDANT CODE ????????
                    last_sample_time = "2017-01-01 00:00:00.000"
                    logger.warning("-- No datsamples to sync to central DB --")
        
            ##WHAT IF central DB is empty????#####
            time2 = datetime.datetime.now()
            duration = time2 - time1
            logger.warning("TTTTT - update get last sample time from central DB execution time: %s" % (duration))            
            
            #####
            # when prog gets here lastSampleTimeInCentralDB stored in last_sample_time
            #####
            
            # get rs from local db now get samples from local db with timestamp > last sample time on central db
            time1 = datetime.datetime.now()

            localDBHostName = cfg.getItemValueFromConfig('db_hostname')
            localDBUserName = cfg.getItemValueFromConfig('db_username')
            localDBPassword = cfg.getItemValueFromConfig('db_password')
            localDBDBName = cfg.getItemValueFromConfig('db_dbname')    
            
            self.dbConnLocal = self.dbc.getDBConn(localDBHostName,
                                                    localDBUserName,
                                                    localDBPassword,
                                                    localDBDBName)
                                                            
            # prepare a cursor object using cursor() method
            self.cursorLocal = self.dbc.getDBCursor(self.dbConnLocal)            
            # now get samples from local db with timestamp > last sample time on central db
            
            # get an error here if last_sample has no fractional part when retrieved from local db
            # e.g WHERE sample_dt > '2017-11-07 09:24:00' - this really should '2017-11-07 09:24:00.000'
            # appears to be truncated when retrieved from db as entry in db does have 3 dp '.000' using sqlite3
            sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt > '%s'" % last_sample_time
            logger.warning("sql to get last sample time: %s" % sql)            
            #
            self.dbc.execute(self.cursorLocal, sql)
            logger.warning("statement after get rs of samples from local db")
            rs_to_update_central_db = list(self.cursorLocal.fetchall())
             ######using sscursor must iterate over to get row count - cos cant use rowcount with ssCursor
            ##using sscursor to see if solves memory leak
            #with self.cursorLocal() as cursor:
                ## Read a single record
                
                ##cursor.execute(sql, ('webmaster@python.org',))
                #result = cursor.fetchone() # returns None if no data avail
                #print(result)
            ######################################################            
            
            logger.debug("--Records to update central db: %s" % (rs_to_update_central_db))
            logger.debug("data got from local server - in list ready to upload-")
    
    
    
            logger.debug("executing sql to update to remote db to sync with local db=")
            # if rs_to_update_central_db.count > 0: 
            
            time2 = datetime.datetime.now()
            duration = time2 - time1
            logger.warning("TTTTT - update get local samples to update to central DB : %s" % (duration)) 
            
           
           
                        
                        
            rsLen =   len(rs_to_update_central_db)          
            if  rsLen > 0:  # if there are records to add to central db
                
               # update central db
                sql = "INSERT INTO thdata (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) \
                     VALUES (%s, %s, %s, '%s', '%s', '%s' )"
                res = self.dbc.executemany(self.cursorCentral, sql, rs_to_update_central_db)
                if (res==0):
                    self.dbc.close(self.dbConnCentral)
                    self.dbc.close(self.dbConnLocal)
                    logger.warning( "^^^^^^^^^^ execute many to central db query returned 0 ^^^^^^^^^^^^^^^^")
                    logger.warning( "..........................returning..........................")  
                    return                
                self.dbc.commitClose(self.dbConnCentral)
                logger.warning("SSSSSS  samples synced to central DB: %s SSSSSS", rsLen )
            else:
                logger.warning("-- No samples to sync to central DB --")

            #if self.dbc: # does this do anything?
                #self.dbc.close(self.dbConnCentral)
            # Commit your changes in the database
            self.dbc.commitClose(self.dbConnLocal)
        except:
            logger.error("????????? bad update_central_db exception thrown ??????")
            logger.exception("update samples in central db")
            e = sys.exc_info()[0]
            logger.error( "????????? Error: %s ????????" % e )
            
        return
