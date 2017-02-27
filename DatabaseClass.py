import MySQLdb
import pymysql.cursors
import sys
from DBCore import *
import logging


from ConfigObject import cfg # singleton global

class Database(object):

    def __init__(self):
        logging.info("Creating db object")
        self.dbc = DBCore()
        return



        
        
    def writeSampleToLocalDB(self, sample_dt, temperature, humidity, heaterstate, ventstate, fanstate):
        # Open database connection
        try:
            logging.warning("===writeSampleToLocalDB===")
            self.dbConn = self.dbc.getDBConn(cfg.getItemValueFromConfig('db_hostname'), 
                            cfg.getItemValueFromConfig('db_username'), 
                            cfg.getItemValueFromConfig('db_password'),
                            cfg.getItemValueFromConfig('db_dbname'))        
            # prepare a cursor object using cursor() method
            self.cursor = self.dbc.getDBCursor(self.dbConn)
    
            # Prepare SQL query to INSERT a record into the database.
            sql = "INSERT INTO thdata(sample_dt, \
                temperature, humidity, heaterstate, ventstate, fanstate) \
                VALUES ('%s', '%s', '%s', '%s', '%s', '%s' )" % \
                (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate)
            # Execute the SQL command
            self.dbc.execute(self.cursor, sql)
    
            # Commit your changes in the database
            self.dbc.commitClose(self.dbConn)
    
            #self.update_central_db()    # sync local recs update to central db
        
        except:
            logging.error("????? bad writeSampleToLocalDB exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )
            
        return


    def update_central_db(self):

        try:
            logging.warning("=== update_central_db samples ===")
            # Open database connection
            #print "?1?"
            self.dbConnCentral = self.dbc.getDBConn(cfg.getItemValueFromConfig('central_db_hostname'), 
                                    cfg.getItemValueFromConfig('central_db_username'), 
                                    cfg.getItemValueFromConfig('central_db_password'), 
                                    cfg.getItemValueFromConfig('central_db_dbname'))          
            
            # prepare a cursor object using cursor() method
            
            self.cursorCentral = self.dbc.getDBCursor(self.dbConnCentral)
            #print "?2?"
            # Prepare and execute SQL query to get timestamp of last record in the central database.
            sql = "SELECT sample_dt FROM thdata ORDER BY id DESC LIMIT 1"
            self.dbc.execute(self.cursorCentral, sql)
            
            logging.debug("get last sample time from central sql: %s" % (sql) )
            
            #do what with empty set - e.g at start when central table is empty eg last sample time = 0
            
            if self.cursorCentral.rowcount == 0: #if central db is empty
                last_sample_time = "2017-01-01 00:00:00.000"
                logging.warning("-- No last sample in central db so set time of last to long ago: %s" % last_sample_time)                
            
            else: #  rowcount != 0
                logging.debug("--- rowcount  : %s ---" % self.cursorCentral.rowcount)                
                
                row = self.cursorCentral.fetchone()    # get row of data
                logging.debug("--- row !=0  : %s ---" % row)
                #print(row[0])                
                
                #logging.warning("row[0] :%s " % (row[0]))
                #logging.warning("last sample time: %s - " % (row[0]) )
                last_sample_time = row[0]
                if row[0] == None: #REDUNDANT CODE ????????
                    last_sample_time = "2017-01-01 00:00:00.000"
                    logging.warning("-- No datsamples to sync to central DB --")
        
##WHAT IF central DB is empty????#####
    
            
            # get rs from local db     
            self.dbConnLocal = self.dbc.getDBConn(cfg.getItemValueFromConfig('db_hostname'), cfg.getItemValueFromConfig('db_username'), 
                    cfg.getItemValueFromConfig('db_password'), cfg.getItemValueFromConfig('db_dbname'))        
    
            # prepare a cursor object using cursor() method
            self.cursorLocal = self.dbc.getDBCursor(self.dbConnLocal)
            
            # now get samples from local db with timestamp > last sample time on central db
            sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt > '%s'" % last_sample_time
            #sql = "SELECT * FROM thdata WHERE sample_dt >= '%s'" % last_sample_time

            logging.debug("sql: %s" % sql)
            
            rs_to_update_central_db = self.dbc.execute(self.cursorLocal, sql)
            rs_to_update_central_db = list(self.cursorLocal.fetchall())
            logging.debug("--Records to update central db: %s" % (rs_to_update_central_db))
            logging.debug("data got from local server - in list ready to upload-")
    
            logging.debug("executing sql to update to remote db to sync with local db=")
            # if rs_to_update_central_db.count > 0: 
            if self.cursorLocal.rowcount > 0:  # if there are records to add to central db
                
               # update central db
                sql = "INSERT INTO thdata (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) \
                     VALUES (%s, %s, %s, '%s', '%s', '%s' )"
                self.dbc.executemany(self.cursorCentral, sql, rs_to_update_central_db)
                self.dbc.commitClose(self.dbConnCentral)
                logging.warning("=== samples synced to central DB: %s ===", self.cursorLocal.rowcount )
            else:
                logging.warning("-- No samples to sync to central DB --")

    
            # Commit your changes in the database
            self.dbc.commitClose(self.dbConnLocal)
        except:
            logging.error("????? bad update_central_db exception thrown ???")
            e = sys.exc_info()[0]
            logging.error( "????? Error: %s ?????" % e )
            
        return
