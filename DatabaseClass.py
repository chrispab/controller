import MySQLdb
import sys
from DBCore import *


from ConfigObject import cfg # singleton global

class Database(object):

    def __init__(self):
        print("Creating db object")
        self.dbc = DBCore()
        return

    def writeSampleToLocalDB(self, sample_dt, temperature, humidity, heaterstate, ventstate, fanstate):
        # Open database connection
        try:
            print("===writeSampleToLocalDB===")
            self.dbConn = self.dbc.getDBConn(cfg.getItemValueFromConfig('db_hostname'), 
                            cfg.getItemValueFromConfig('db_username'), 
                            cfg.getItemValueFromConfig('db_password'),
                            cfg.getItemValueFromConfig('db_dbname'))        
            #print(">>>>>>>>>>>>>>>>>>>>>> dbConn got okay >>>>>>>>>>>>>>>>>>>>>")
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
    
            self.update_central_db()    # sync local recs update to central db
        
        except:
            print("????? bad writeSampleToLocalDB exception thrown ???")
            e = sys.exc_info()[0]
            print( "????? Error: %s ?????" % e )
            
        return


    def update_central_db(self):

        try:
            print("===update_central_db===")
            # Open database connection
            self.dbConnCentral = self.dbc.getDBConn(cfg.getItemValueFromConfig('central_db_hostname'), 
                                    cfg.getItemValueFromConfig('central_db_username'), 
                                    cfg.getItemValueFromConfig('central_db_password'), 
                                    cfg.getItemValueFromConfig('central_db_dbname'))          
            
            # prepare a cursor object using cursor() method
            self.cursorCentral = self.dbc.getDBCursor(self.dbConnCentral)
    
            # Prepare and execute SQL query to get timestamp of last record in the central database.
            sql = "SELECT sample_dt FROM thdata ORDER BY id DESC LIMIT 1"
            last_sample_time = self.dbc.execute(self.cursorCentral, sql)
            
            sys.stdout.write("last sample time from central db: %s - " % (last_sample_time) )
            row = self.cursorCentral.fetchone()    # get result if any
            sys.stdout.write("row :%s - " % (row))
    
            if row > 0:
                sys.stdout.write("last sample time: %s - " % (row[0]) )
                last_sample_time = row[0]
            if row == None:
                last_sample_time = "2016-11-01 00:00:00"
    
            # now get samples from local db with timestamp > last sample time on central db
            sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt >= '%s'" % last_sample_time
    
            # get rs from local db     
            self.dbConnLocal = self.dbc.getDBConn(cfg.getItemValueFromConfig('db_hostname'), cfg.getItemValueFromConfig('db_username'), 
                    cfg.getItemValueFromConfig('db_password'), cfg.getItemValueFromConfig('db_dbname'))        
    
            # prepare a cursor object using cursor() method
            self.cursorLocal = self.dbc.getDBCursor(self.dbConnLocal)
    
            rs_to_update_central_db = self.dbc.execute(self.cursorLocal, sql)
            rs_to_update_central_db = list(self.cursorLocal.fetchall())
            print("--Records to update central db: %s" % (rs_to_update_central_db))
            sys.stdout.write("data got from local server - in list ready to upload-")
    
            sys.stdout.write("executing sql to update to remote db to sync with local db=")
            # if rs_to_update_central_db.count > 0: 
            if self.cursorLocal.rowcount > 0:  # if there are records to add to central db
               # update central db
                sql = "INSERT INTO thdata (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) \
                     VALUES (%s, %s, %s, '%s', '%s', '%s' )"
                self.dbc.executemany(self.cursorCentral, sql, rs_to_update_central_db)
                self.dbc.commitClose(self.dbConnCentral)
    
            # Commit your changes in the database
            self.dbc.commitClose(self.dbConnLocal)
        except:
            print("????? bad update_central_db exception thrown ???")
            e = sys.exc_info()[0]
            print( "????? Error: %s ?????" % e )
            
        return
