import MySQLdb
import settings #old settings py file


class Database(object):

    def __init__(self):
        print("Creating db object")
        #


    def getConfigItem(self, name):
        # Open database connection
        print("trying to connect for setconfigitem in db")
        try:
            self.db = MySQLdb.connect(
                settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        print("connected")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

        sql = "SELECT %s FROM config ORDER BY id DESC LIMIT 1" % (name)
        
        # Execute the SQL command
        try:
            value = self.cursor.execute(sql)
        except:
            print("dberror executing sql query getting setting val from db")

        if self.db.open:
            self.db.close()
            print("++ final close ++")

        return


    def setConfigItem(self, name, value):
        # Open database connection
        print("trying to connect for setconfigitem in db")
        try:
            self.db = MySQLdb.connect(
                settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        print("connected")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

            # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % (name, value)
        # Execute the SQL command
        try:
            self.cursor.execute(sql)
        except:
            print("dberror executing sql query")
        print("executing sql")

        # Commit your changes in the database
        try:
            self.db.commit()
            print("committed")

            # disconnect from server
            print("ready for closing")
        except MySQLdb.Error, e:
            try:
                self.db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.db.open:
                self.db.close()
                print("++ final close ++")

        return value


    def writedb(self, sample_dt, temperature, humidity, heaterstate, ventstate, fanstate):
        # Open database connection
        print("about to try writing record to db")
        print("trying to connect")
        try:
            self.db = MySQLdb.connect(
                settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        print("connected")
        # prepare a cursor object using cursor() method
        try:
            self.cursor = self.db.cursor()
        except:
            print("dberror getting cursor")

            # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO thdata(sample_dt, \
            temperature, humidity, heaterstate, ventstate, fanstate) \
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s' )" % \
            (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate)
        # Execute the SQL command
        try:
            self.cursor.execute(sql)
        except:
            print("dberror executing sql query")
        print("executing sql")

        # Commit your changes in the database
        try:
            self.db.commit()
            print("committed")

            # disconnect from server
            print("ready for closing")
        except MySQLdb.Error, e:
            try:
                self.db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.db.open:
                self.db.close()
                print("++ final close ++")

        self.update_central_db()    # sync local recs update to central db

        return


    def updateCentralConfigTable(self):

        print("about to try update config table from local db to central db")
        print("trying to connect to central server")
        # Open database connection
        try:
            self.central_db = MySQLdb.connect(settings.central_db_hostname, settings.central_db_username,
                                              settings.central_db_password, settings.central_db_dbname, connect_timeout=15)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
            print("returning 1")
            return
        print("connected")

        # prepare a cursor object using cursor() method
        try:
            self.central_cursor = self.central_db.cursor()
        except:
            print("dberror getting cursor")
            
            
        # Prepare SQL query to update a single item in the database settings table.
        sql = "UPDATE  config SET %s = %f" % ('tempSPLOn', value)
        # Execute the SQL command
        try:
            self.central_cursor.execute(sql)
        except:
            print("dberror executing sql query")
        print("executing sql")

        # Commit your changes in the database
        try:
            self.central_db.commit()
            print("committed")

            # disconnect from server
            print("ready for closing")
        except MySQLdb.Error, e:
            try:
                self.central_db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.central_db.open:
                self.central_db.close()
                print("++ final close ++")

        return value


    def update_central_db(self):

        print("about to try batch update from local db to central db")
        print("trying to connect to central server")
        # Open database connection
        try:
            self.central_db = MySQLdb.connect(settings.central_db_hostname, settings.central_db_username,
                                              settings.central_db_password, settings.central_db_dbname, connect_timeout=15)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
            print("returning 1")
            return
        print("connected")

        # prepare a cursor object using cursor() method
        try:
            self.central_cursor = self.central_db.cursor()
        except:
            print("dberror getting cursor")

        # Prepare SQL query to get timestamp of last record in the central
        # database.
        sql = "SELECT sample_dt FROM thdata ORDER BY id DESC LIMIT 1"
        try:
            last_sample_time = self.central_cursor.execute(sql)
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            last_sample_time

        print("last sample time from central db: ", last_sample_time)
        row = self.central_cursor.fetchone()    # get result if any
        print("row :", row)

        if row > 0:
            print("last sample time = ", row[0])
            last_sample_time = row[0]
        if row == None:
            last_sample_time = "2016-11-01 00:00:00"

        # now get samples from local db with timestamp > last sample time on
        # central db
        sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt >= '%s'" % last_sample_time
        print (sql)
        # get rs from local db
        try:
            self.local_db = MySQLdb.connect(
                settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to local dberror")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])
        print("connected")

        # prepare a cursor object using cursor() method
        try:
            self.local_cursor = self.local_db.cursor()
        except:
            print("dberror getting cursor")

        try:
            rs_to_update_central_db = self.local_cursor.execute(sql)
            rs_to_update_central_db = list(self.local_cursor.fetchall())
            print(rs_to_update_central_db)
            # rs_to_update_central_db)
            print("data got from local server - in list ready to upload")
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            print "dberror Error %d: %s" % (e.args[0], e.args[1])

        print("executing sql to update to remote db to sync with local db")
        # if rs_to_update_central_db.count > 0:    #if there are records to add
        # to central db
        if self.local_cursor.rowcount > 0:  # if there are records to add to central db
           # update central db
            try:
                # Prepare SQL query to INSERT a record into the database.
                sql = "INSERT INTO thdata (sample_dt, temperature, humidity, heaterstate, ventstate, fanstate) \
                 VALUES (%s, %s, %s, '%s', '%s', '%s' )"
                self.central_cursor.executemany(sql, rs_to_update_central_db)
                self.central_db.commit()
                self.central_db.close()
            except MySQLdb.Error, e:
                print("error updating central db dberror")
                print "dberror Error %d: %s" % (e.args[0], e.args[1])
            print("connected")

            # Commit your changes in the database
        try:
            self.local_db.commit()
            print("committed")

            # disconnect from server
            print("ready for closing")
        except MySQLdb.Error, e:
            try:
                self.local_db.rollback()
            except:
                print("db rollback failed dberror")
            #raise e
            print("+++++++++++++DB WRITE PROBLEM +++++++++")
        finally:
            if self.local_db.open:
                self.local_db.close()
                print("++ final close ++")

        return
