#import MySQLdb
#import pymysql
import pymysql.cursors
import sqlite3 as lite
import sys
import logging

class DBCore(object):
        
    dbConn = None
    cursor = 0
        
    def __init__(self):
        logging.info("Creating db Core object")
        return

#    def getDBConn(self, hostName, userName, password, databaseName, conn_timeout=1):
    def getDBConn(self, hostName, userName, password, databaseName):
        # Open database connection
        logging.debug("* 1 getDBconn*")
        
        # check if connecting to local sqlite3 db and get its con obj otherwise get a mysql conn object
        if (hostName == '127.0.0.1'):
            
            #con = None
            
            try:
                #con = lite.connect(databaseName)
                logging.warning("******* ATTEMPTING SQLITE CONN  *******")

                self.dbConn = lite.connect(databaseName)
                
                #cur = self.dbConn.cursor()    
                #cur.execute('SELECT SQLITE_VERSION()')
                
                #data = cur.fetchone()
                
                #print "SQLite version: %s" % data      
                logging.warning("***** SQLITE3  OPEN getDBconn connected *: %s, %s SQLITE3 *****" % (hostName, databaseName))
          
                
                
            except lite.Error, e:
                
                print "Error %s:" % e.args[0]
                #sys.exit(1)
                
            finally:
                
                if self.dbConn :
                    self.dbConn .close()
                        
        else:
            
            try:
                logging.debug("* 2 getDBconn*")
                self.dbConn = pymysql.connect(host = hostName,
                                                user = userName,
                                                passwd = password,
                                                db = databaseName,
                                                connect_timeout = 1,
                                                cursorclass = pymysql.cursors.SSCursor,
                                                read_timeout = 1)
    #                            db = databaseName, connect_timeout = conn_timeout, cursorclass=pymysql.cursors.SSCursor)
    
                logging.debug("* OPEN getDBconn connected *: %s, %s" % (hostName, databaseName))
                logging.info("* connected *")
                logging.debug("* 3 getDBconn*")
            except Exception as e:
                logging.debug("* 4 getDBconn*")
                logging.error("* error getting DB connection * ")
                logging.error("* DB Error %d: %s * " % (e.args[0], e.args[1]))
                #print "1!"
                self.dbConn = 0
                
        logging.debug("* 5 getDBconn*")
        return self.dbConn
        

    def getDBCursor (self, dbConn):
        logging.info("* getDBCursor *")
        logging.warning("???????????? GETDBCURSOR dbconn = %s" % dbConn)

        try:
            self.cursor = dbConn.cursor()
            logging.info("* got db cursor *")
        except Exception as e:
            logging.error("*** dberror getting cursor test ***")
            logging.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            self.cursor = 0
        return self.cursor
        
        
    def execute(self, cursor, sqlstr):
        
        try:
            #print("sql: %s" % sqlstr)
            cursor.execute(sqlstr)
            result = 1
        except Exception as e:
            logging.warning("*** dberror executing sql query ***")
            logging.warning("*** dberror Error %d: %s ***" % (e.args[0], e.args[1]))
            result = 0
        logging.info("* executing sql *")
        return result
        
    def executemany(self, cursor, sqlstr, rs):
        try:
            logging.info("* executing many sql *")
            #print("sql: %s" % sqlstr)
            #print("sql: %s" % rs)
            cursor.executemany( sqlstr, rs)
            result = 1
        except Exception as e:
            logging.error("*** dberror executing sql query ***")
            logging.error("*** dberror Error %d: %s ***" % (e.args[0], e.args[1]))
            result = 0
        logging.info("* executing sql *")
        return result
        

    def commitClose(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            logging.info("* committed *")
            # disconnect from server
            logging.info("* ready to close *")
        except Exception as e:
            try:
                dbConn.rollback()
            except:
                logging.error("*** db rollback failed dberror ***")
                logging.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            logging.error("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            logging.info("* commitClose *")
        return

    def commit(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            logging.info("* committed *")

            # disconnect from server
            logging.info("* ready to close *")
        except Exception as e:
            try:
                dbConn.rollback()
            except:
                logging.error("*** db rollback failed dberror ***")
                logging.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            logging.error("*** DB WRITE PROBLEM so rolled back***")
        finally:
            self.close(dbConn)
            logging.info("* commit - final close*")
        return
                
    def close(self, dbConn):
        # Close the database conn
        try:            
            if  dbConn.open:
                dbConn.close()
                logging.info("* close *")
        except Exception as e:
            logging.error("*** dberror closing conn ***")
            logging.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
        
        logging.debug("* CLOSED db conn %s: " % dbConn)
        return
        
