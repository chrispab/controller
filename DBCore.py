#import MySQLdb
import pymysql
import sys
import logging

class DBCore(object):
        
    dbConn = 0
    cursor = 0
        
    def __init__(self):
        logging.info("Creating db Core object")
        return


    def getDBConn(self, hostName, userName, password, databaseName, conn_timeout=1):
        # Open database connection
        logging.info("* getDBconn *")
        try:
            self.dbConn = pymysql.connect(host = hostName, 
                            user = userName, passwd = password, 
                            db = databaseName, connect_timeout = conn_timeout)
            logging.info("* connected *")
        except Exception as e:
            logging.error("* error getting DB connection * ")
            logging.error("* DB Error %d: %s * " % (e.args[0], e.args[1]))
            self.dbConn = 0
        
        return self.dbConn
        

    def getDBCursor (self, dbConn):
        logging.info("* getDBCursor *")
        try:
            self.cursor = dbConn.cursor()
            logging.info("* got db cursor *")
        except Exception as e:
            logging.error("*** dberror getting cursor ***")
            logging.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            self.cursor = 0
        return self.cursor
        
        
    def execute(self, cursor, sqlstr):
        result = 0
        try:
            #print("sql: %s" % sqlstr)
            result = cursor.execute(sqlstr)
        except Exception as e:
            logging.error("*** dberror executing sql query ***")
            logging.error("*** dberror Error %d: %s ***" % (e.args[0], e.args[1]))
        logging.info("* executing sql *")
        return result
        
    def executemany(self, cursor, sqlstr, rs):
        try:
            logging.info("* executing sql *")
            #print("sql: %s" % sqlstr)
            #print("sql: %s" % rs)
            result =cursor.executemany( sqlstr, rs)
        except Exception as e:
            logging.error("*** dberror executing sql query ***")
            logging.error("*** dberror Error %d: %s ***" % (e.args[0], e.args[1]))
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
        return
        
