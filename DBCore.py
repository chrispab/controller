import MySQLdb
import sys


class DBCore(object):
        
    dbConn = 0
    cursor = 0
        
    def __init__(self):
        print("Creating db Core object")
        #
        return


    def getDBConn(self, hostName, userName, password, databaseName, conn_timeout=15):
        # Open database connection
        sys.stdout.write("* get DB conn *")
        try:
            self.dbConn = MySQLdb.connect(host = hostName, 
                            user = userName, passwd = password, 
                            db = databaseName, connect_timeout = conn_timeout)
        except MySQLdb.Error, e:
            print("* error connecting to DB * ")
            print "* DB Error %d: %s * " % (e.args[0], e.args[1])
        sys.stdout.write("* connected *")        
        return self.dbConn
        

    def getDBCursor (self, dbConn):
        ## prepare a cursor object using cursor() method
        try:
            self.cursor = dbConn.cursor()
        except MySQLdb.Error, e:
            print("*** dberror getting cursor ***")
            print "*** DB Error %d: %s ***" % (e.args[0], e.args[1])
        return self.cursor
        
        
    def execute(self, cursor, sqlstr):
        result = 0
        try:
            result = cursor.execute(sqlstr)
        except MySQLdb.Error, e:
            print("*** dberror executing sql query ***")
            print "*** dberror Error %d: %s ***" % (e.args[0], e.args[1])
        sys.stdout.write("* executing sql *")
        return result
        
    def executemany(self, cursor, sqlstr, rs):
        try:
            result =cursor.executemany( sqlstr, rs)
        except MySQLdb.Error, e:
            print("*** dberror executing sql query ***")
            print "*** dberror Error %d: %s ***" % (e.args[0], e.args[1])
        sys.stdout.write("* executing sql *")
        return result
        

    def commitClose(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            sys.stdout.write("* committed *")

            # disconnect from server
            sys.stdout.write("* ready to close *")
        except MySQLdb.Error, e:
            try:
                dbConn.rollback()
            except:
                print("*** db rollback failed dberror ***")
                print "*** DB Error %d: %s ***" % (e.args[0], e.args[1])
            print("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            print("* final commitClose *")
        return

    def commit(self, dbConn):
        # Commit your changes in the database
        try:
            dbConn.commit()
            sys.stdout.write("* committed *")

            # disconnect from server
            sys.stdout.write("* ready to close *")
        except MySQLdb.Error, e:
            try:
                dbConn.rollback()
            except:
                print("*** db rollback failed dberror ***")
                print "*** DB Error %d: %s ***" % (e.args[0], e.args[1])
            print("*** DB WRITE PROBLEM ***")
        finally:
            self.close(dbConn)
            print("* final commit Close *")
        return
                
    def close(self, dbConn):
        # Commit your changes in the database

        if  dbConn.open:
            dbConn.close()
            sys.stdout.write("* fclose dbConn *")
        return
        
