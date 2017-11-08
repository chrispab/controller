#import MySQLdb
#import pymysql
import pymysql.cursors
import sqlite3 as lite
import sys
import logging

logger = logging.getLogger(__name__)


class DBCore(object):
        
    dbConn = 0
    cursor = 0
        
    def __init__(self):
        logger.info("Creating db Core object")
        return

#    def getDBConn(self, hostName, userName, password, databaseName, conn_timeout=1):
    def getDBConn(self, hostName, userName, password, databaseName):
        # Open database connection
        logger.debug("* 1 getDBconn*")
        
        # check if connecting to local sqlite3 db and get its con obj otherwise get a mysql conn object
        if (hostName == '127.0.0.1'):
            try:
                #logger.warning("******* ATTEMPTING SQLITE CONN  *******")
                self.dbConn = lite.connect(databaseName)
                #logger.warning("***** SQLITE3  OPEN getDBconn connected *: %s, %s SQLITE3 *****" % (hostName, databaseName))
            #except lite.Error, e:
            except Exception as e:
                print "Error %s:" % e.args[0]
                #sys.exit(1)
                self.dbConn = 0
                
            #finally:
                
                #if self.dbConn :
                    #self.dbConn .close()
                        
        else:
            
            try:
                logger.debug("* 2 getDBconn*")
                self.dbConn = pymysql.connect(host = hostName,
                                                user = userName,
                                                passwd = password,
                                                db = databaseName,
                                                connect_timeout = 1,
                                                cursorclass = pymysql.cursors.SSCursor,
                                                read_timeout = 1)
    #                            db = databaseName, connect_timeout = conn_timeout, cursorclass=pymysql.cursors.SSCursor)
    
                logger.debug("* OPEN getDBconn connected *: %s, %s" % (hostName, databaseName))
                logger.info("* connected *")
                logger.debug("* 3 getDBconn*")
            except Exception as e:
                logger.debug("* 4 getDBconn*")
                logger.error("* error getting DB connection * ")
                logger.error("* DB Error %d: %s * " % (e.args[0], e.args[1]))
                #print "1!"
                self.dbConn = 0
                
        logger.debug("* 5 getDBconn*")
        return self.dbConn
        

    def getDBCursor (self, dbConn):
        logger.info("* getDBCursor *")
        #logger.warning("???????????? GETDBCURSOR dbconn = %s" % dbConn)

        try:
            self.cursor = dbConn.cursor()
            logger.info("* got db cursor *")
        except Exception as e:
            logger.error("*** dberror getting cursor test ***")
            #logger.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            self.cursor = 0
        return self.cursor
        
        
    def execute(self, cursor, sqlstr):
        
        try:
            #logger.warning("sql: %s" % sqlstr)
            cursor.execute(sqlstr)
            #logger.warning("* executed sql *")
            result = 1
        except Exception as e:
            logger.error("*** dberror executing sql query mmmmmm***")
            #logger.exception("*** db execute Error %d: %s ***" % (e.args[0], e.args[1]))
            logger.exception("*** db execute Error ***")
            result = 0
        return result
        
    def executemany(self, cursor, sqlstr, rs):
        try:
            logger.info("* executing many sql *")
            logger.debug("sqlstr: %s" % sqlstr)
            logger.debug("rs: %s" % rs)
            cursor.executemany( sqlstr, rs)
            result = 1
        except Exception as e:
            #logger.exception("*** dberror executing sql query zzz***")
            logger.error("*** dberror Error %d: %s ***" % (e.args[0], e.args[1]))
            result = 0
        logger.info("* executing sql *")
        return result
        

    def commitClose(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            logger.info("* committed *")
            # disconnect from server
            logger.info("* ready to close *")
        except Exception as e:
            try:
                dbConn.rollback()
            except:
                logger.error("*** db rollback failed dberror ***")
                logger.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            logger.error("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            logger.info("* commitClose *")
        return

    def commit(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            logger.info("* committed *")

            # disconnect from server
            logger.info("* ready to close *")
        except Exception as e:
            try:
                dbConn.rollback()
            except:
                logger.error("*** db rollback failed dberror ***")
                #logger.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
            logger.error("*** DB WRITE PROBLEM so rolled back***")
        finally:
            self.close(dbConn)
            logger.info("* commit - final close*")
        return
                
    def close(self, dbConn):
        # Close the database conn
        try:            
            if  dbConn:
                dbConn.close()
                logger.info("* close *")
        except Exception as e:
            logger.exception("*** dberror closing conn ***")
            #logger.error("*** DB Error %d: %s ***" % (e.args[0], e.args[1]))
        
        logger.debug("* CLOSED db conn %s: " % dbConn)
        return
        
