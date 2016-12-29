import MySQLdb
import sys

##import settings #old settings py file
#import socket # to get hostname 

##note: hostName expected zone1 or zone2
#hostName = socket.gethostname()
#settingsFileName = 'settings_' + hostName
#print(settingsFileName)
##import as settings
#settings = __import__(settingsFileName)
#from ConfigObject import cfg # singleton global

class DBCore(object):
        
    dbConn = 0
    cursor = 0
        
    def __init__(self):

        
        print("Creating db Core object")
        #
        return


    def getDBConn(self, hostName, userName, password, databaseName, connect_timeout=15):
        # Open database connection
        sys.stdout.write("*** Attempt to connect to DB ***")
        try:
            self.dbConn = MySQLdb.connect(hostName, userName, password, databaseName)
        except MySQLdb.Error, e:
            print("*** error connecting to DB ***")
            print "*** DB Error %d: %s ***" % (e.args[0], e.args[1])
        sys.stdout.write("*** connected ***")

        
        return self.dbConn
        

    def getDBCursor (self, dbConn):
        ## prepare a cursor object using cursor() method
        try:
            self.cursor = self.dbConn.cursor()
        except:
            print("*** dberror getting cursor ***")

        return self.cursor
        
    def execute(self, cursor, sqlstr):
        try:
            cursor.execute(sqlstr)
        except MySQLdb.Error, e:
            print("*** dberror executing sql query ***")
            print "*** dberror Error %d: %s ***" % (e.args[0], e.args[1])
        sys.stdout.write("*** executing sql ***")
        return
        

    def commitClose(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            sys.stdout.write("*** committed ***")

            # disconnect from server
            sys.stdout.write("*** ready for closing ***")
        except MySQLdb.Error, e:
            try:
                dbConn.rollback()
            except:
                print("*** db rollback failed dberror ***")
            #raise e
            print("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            print("*** final close commitClose **")
        return

    def commit(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            sys.stdout.write("*** committed ***")

            # disconnect from server
            sys.stdout.write("*** ready for closing ***")
        except MySQLdb.Error, e:
            try:
                dbConn.rollback()
            except:
                print("*** db rollback failed dberror ***")
            #raise e
            print("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            print("*** final close commitClose **")
        return
                
    def close(self, dbConn):
        # Commit your changes in the database

        if  dbConn.open:
            dbConn.close()
            print("** fclose dbConn **")
        return
        
