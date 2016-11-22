#!/usr/bin/env python
# control.py
# control for enviro controller

# ===================general imports=====================================
import csv
import datetime
import time
from datetime import timedelta
import MySQLdb
#import yaml

import hardware as hw
import settings
from support import round_time as round_time

OFF = settings.OFF  # state for relay OFF
ON = settings.ON  # state for on

path = settings.dataPath
extraPath = settings.extraPath


# ============================common code start==========================

class Relay(object):
    def __init__(self):
        print("creating relay - dummy so far")


class Vent(object):
    def __init__(self):
        print("creating vent")
        self.state = OFF
        self.speed_state = OFF
        self.speed_state_count = 0
        self.speed_state_trigger = 5    #trigger hi state on n counts hi
        self.prev_vent_millis = 0  # last time vent state updated
        self.vent_on_delta = settings.ventOnDelta  # vent on time
        self.vent_off_delta = settings.ventOffDelta  # vent off time
        self.vent_pulse_active = OFF  # settings.ventPulseActive
        self.vent_pulse_delta = 0  # ventPulseDelta
        self.vent_pulse_on_delta = settings.ventPulseOnDelta
        self.vent_override = OFF  # settings.ventOverride
      

    def control(self, current_temp, target_temp, d_state, current_millis):
        print('.Vent ctl')

        #if self.speed_state = ON  # high speed
            #self.speed_state_count++
        #if self.speed_state_count == self.speed_state_trigger:
            #self.speed_state = ON  # high speed
            #self.speed_state_count = 0
        #if self.speed_state = OFF  # lo speed
        
        #else:
            #self.speed_state = OFF  # lo speed        
        
        #if d_state == ON:
            #self.speed_state = ON  # high speed
        #else:
            #self.speed_state = OFF  # lo speed
        self.speed_state = OFF  # lo speed
        
        # cool
        if current_temp > target_temp + settings.vent_sp_offset:
            self.vent_override = ON
            self.state = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            print("..VENT ON - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")
        elif (self.vent_override == ON) and ((current_millis - self.prev_vent_millis) >= self.vent_pulse_on_delta):  # temp below target, change state to OFF after pulse delay
            self.state = OFF
            self.vent_override = OFF
            self.prev_vent_millis = current_millis
            print("..VENT OFF - temp ok, OVERRIDE - OFF")
        elif self.vent_override == ON:
            print('..Vent on - override in progress')

        # periodic vent control - only execute if vent ovveride not active
        if self.vent_override == OFF:  # process periodic vent activity
            if self.state == OFF:  ##if the vent is off, we must wait for the interval to expire before turning it on
                ## iftime is up, so change the state to ON
                if current_millis - self.prev_vent_millis >= self.vent_off_delta:
                    self.state = ON
                    print("..VENT ON cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    print('..Vent off - during cycle OFF period')
            else:
                # vent is on, we must wait for the duration to expire before turning it off
                if (current_millis - self.prev_vent_millis) >= self.vent_on_delta:  # time up, change state to OFF
                    self.state = OFF
                    print("..VENT OFF cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    print('..Vent on - during cycle ON period')
        return


class Fan(object):
    def __init__(self):
        print("Creating fan")
        self.state = OFF
        self.prev_fan_millis = 0  # last time vent state updated
        self.fan_on_delta = settings.fan_on_t  # vent on time
        self.fan_off_delta = settings.fan_off_t  # vent off time

    def control(self, current_millis):
        print('.fan ctl')
        # if fan off, we must wait for the interval to expire before turning it on
        print('current millis ', current_millis)
        print('..current fan state ', self.state)
        if self.state == OFF:
            # iftime is up, so change the state to ON
            if current_millis - self.prev_fan_millis >= self.fan_off_delta:
                self.state = ON
                print("..FAN ON")
                self.prev_fan_millis = current_millis
        # else if fanState is ON
        else:
            # time is up, so change the state to LOW
            if (current_millis - self.prev_fan_millis) >= self.fan_on_delta:
                self.state = OFF
                print("..FAN OFF")
                self.prev_fan_millis = current_millis
        #self.state = ON
        return


class Heater(object):
    def __init__(self):
        print("creating heater")
        self.state = OFF
        self.heater_off_delta = settings.heater_off_t  # min time heater is on or off for
        self.heater_on_delta = settings.heater_on_t  # min time heater is on or off for
        self.prev_heater_millis = 0  # last time heater switched on or off
        self.heater_sp_offset = settings.heater_sp_offset

    def control(self, current_temp, target_temp, current_millis, d_state):
        print('.Heat ctl')
        #if d_state == ON:
        current_hour = datetime.datetime.now().hour
        if current_hour in settings.heat_off_hours:  # l on and not hh:xx pm
            self.state = OFF
            print('..d on, in heat off hours - skipping lon heatctl')
        else:#d state on or off here
            print('..do lon or off heatctl')
            if current_temp >= target_temp + self.heater_sp_offset:  # if over temp immediately turn off
                self.state = OFF
                print("...temp over sp - HEATER OFF")
                self.prev_heater_millis = current_millis
            elif self.state == ON:  # t below tsp if time is up, so change the state to OFF
                if current_millis - self.prev_heater_millis >= self.heater_on_delta:
                    self.state = OFF
                    print("...in heat auto cycle - switch HEATER OFF")
                    self.prev_heater_millis = current_millis
                else:
                    print('...in heat auto cycle - Heater still on - during low temp heat pulse')
            elif current_millis - self.prev_heater_millis >= self.heater_off_delta:  # heater is off, turn on after delta
                self.state = ON
                print("...in heat auto cycle - switch HEATER ON")
                self.prev_heater_millis = current_millis
            else:
                print("...in heat auto cycle - during heat OFF period")
        #else:   
            #print("..in d-off, no heat ctl")

        print(' ')
        return

class Database(object):
    
    def __init__(self):
        print("Creating db")
        
    def writedb(self,sample_dt,temperature,humidity,heaterstate,ventstate,fanstate):
        # Open database connection
        print("about to try writing record to db")
        print("trying to connect")
        try:
            self.db = MySQLdb.connect(settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0],e.args[1])
        print("connected")
            # prepare a cursor object using cursor() method
        try:
            self.cursor=self.db.cursor()
        except:
            print("dberror getting cursor")
                
            # Prepare SQL query to INSERT a record into the database.
        sql = "INSERT INTO thdata(sample_dt, \
            temperature, humidity, heaterstate, ventstate, fanstate) \
            VALUES ('%s', '%s', '%s', '%s', '%s', '%s' )" % \
            (sample_dt,temperature,humidity,heaterstate,ventstate,fanstate)
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
        
    def update_central_db(self):
        

        print("about to try batch update from local db to central db")
        print("trying to connect to central server")
        # Open database connection        
        try:
            self.central_db = MySQLdb.connect( settings.central_db_hostname, settings.central_db_username, settings.central_db_password, settings.central_db_dbname, connect_timeout=15)
        except MySQLdb.Error, e:
            print("error connecting to dberror")
            print "dberror Error %d: %s" % (e.args[0],e.args[1])
            print("returning 1")
            return
        print("connected")
        
        # prepare a cursor object using cursor() method
        try:
            self.central_cursor=self.central_db.cursor()
        except:
            print("dberror getting cursor")
                
        # Prepare SQL query to get timestamp of last record in the central database.
        sql = "SELECT sample_dt FROM thdata ORDER BY id DESC LIMIT 1"
        try:
            last_sample_time = self.central_cursor.execute(sql)
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            last_sample_time
        
        print("last sample time from central db: ", last_sample_time)
        row = self.central_cursor.fetchone()    # get result if any
        print("row :", row)
        
        if row >0:
            print("last sample time = ",row[0])
            last_sample_time=row[0]
        if row == None:
            last_sample_time = "2016-11-01 00:00:00" 
        
        # now get samples from local db with timestamp > last sample time on central db
        sql = "SELECT sample_dt, temperature, humidity, heaterstate, ventstate,fanstate FROM thdata WHERE sample_dt >= '%s'" % last_sample_time
        print ( sql)
            # get rs from local db
        try:
            self.local_db = MySQLdb.connect(settings.db_hostname, settings.db_username, settings.db_password, settings.db_dbname)
        except MySQLdb.Error, e:
            print("error connecting to local dberror")
            print "dberror Error %d: %s" % (e.args[0],e.args[1])
        print("connected")
        
            # prepare a cursor object using cursor() method
        try:
            self.local_cursor=self.local_db.cursor()
        except:
            print("dberror getting cursor")            
        
        try:
            rs_to_update_central_db = self.local_cursor.execute(sql)
            rs_to_update_central_db = list(self.local_cursor.fetchall())
            print(rs_to_update_central_db)
            print("data got from local server - in list ready to upload")    #rs_to_update_central_db)
        except MySQLdb.Error, e:
            print("dberror getting last sample time from central db")
            print "dberror Error %d: %s" % (e.args[0],e.args[1])
        
        print("executing sql to update to remote db to sync with local db")        
        #if rs_to_update_central_db.count > 0:    #if there are records to add to central db
        if self.local_cursor.rowcount > 0:    #if there are records to add to central db
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
                print "dberror Error %d: %s" % (e.args[0],e.args[1])
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
        

class Logger(object):
    # roundT = roundTime
    def __init__(self):
        print("creating logger object")
        self.temperature = 0
        self.humidity = 0
        self.heater_state = OFF
        self.vent_state = OFF
        self.fan_state = OFF
        self.vent_speed_state = OFF
        self.current_millis = 0
        self.current_time = 0


        self.previous_temperature = 0
        self.previous_humidity = 0
        self.previous_heater_state = OFF
        self.previous_vent_state = OFF
        self.previous_fan_state = OFF
        self.previous_vent_speed_state = OFF
        self.previous_proc_temp = 0
        # self.previousHeater = 0
        self.previous_CSV_write_millis = 0
        self.min_CSV_write_interval = settings.min_CSV_write_interval
        self.datastore = Database()
        
        
    def write_edge_change(self, state, previous_state):
        if previous_state == OFF:  # must be going OFF to ON
            # write a low record immediately before hi record
            print("----- write edge func -- new prev low row appended to CSV -----")
            state[0] = OFF
            self._write_to_CSV()
            state[0] = ON  # restore to actual current val
            self._write_to_CSV()

        if previous_state == ON:  # must be going ON TO OFF
            # write a on record immediately before hi record
            print("----- new prev hi row appended to CSV -----")
            state[0] = ON
            self._write_to_CSV()
            state[0] = OFF  # restore to actual current val
            self._write_to_CSV()


    def update_CSV_If_changes(self, temperature, humidity, vent_state,
                              fan_state, heater_state, vent_speed_state, current_millis,
                              current_time, proc_temp):
        self.temperature = temperature
        self.humidity = humidity
        self.vent_state = vent_state
        self.fan_state = fan_state
        self.heater_state = heater_state
        self.vent_speed_state = vent_speed_state
        self.current_millis = current_millis
        self.current_time = current_time
        self.proc_temp = proc_temp
        
        self.state_changed = False
        # check each for state change and set new prewrite states
        if self.vent_state != self.previous_vent_state:  # any change in vent
            if self.previous_vent_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new prevvent low row appended to CSV -----")
                self.vent_state = OFF
                self.state_changed = True
            else: # if self.previous_vent_state == ON:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new prevvent hi row appended to CSV -----")
                self.vent_state = ON
                self.state_changed = True
                
        if self.vent_speed_state != self.previous_vent_speed_state:  # any change in vent speed
            if self.previous_vent_speed_state == OFF:  # was lo speed
                # write a low record immediately before hi record
                print("----- new prevvspeed low row appended to CSV -----")
                self.vent_speed_state = OFF
                self.state_changed = True
            else:  # was hi speed going low
                # write a on record immediately before hi record
                print("----- new prevvspeed hi row appended to CSV -----")
                self.vent_speed_state = ON
                self.state_changed = True

        if self.fan_state != self.previous_fan_state:  # any change in vent
            if self.previous_fan_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new prevfanstate low row appended to CSV -----")
                self.fan_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new  prevfanstate hi row appended to CSV -----")
                self.fan_state = ON
                self.state_changed = True

        if self.heater_state != self.previous_heater_state:  # any change in vent
            if self.previous_heater_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new heaterstate low row appended to CSV -----")
                self.heater_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new  heaterstate hi row appended to CSV -----")
                self.heater_state = ON
                self.state_changed = True
                
        #if ((self.temperature != self.previous_temperature)):  # any change
            #self.state_changed = True

        if self.state_changed == True:
            self._write_to_CSV()    #write modded pre change state(s)
            self.vent_state = vent_state
            self.vent_speed_state = vent_speed_state
            self.heater_state = heater_state
            self.fan_state = fan_state
            self._write_to_CSV()    #write modded post change state(s)
            self.previous_CSV_write_millis = self.current_millis #reset timer
        else: #no state change check temp and timer
            if ((self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval))
                    or (self.temperature != self.previous_temperature)):  # any change
                if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                    print("..interval passed ..time for new CSV write")
                else:
                    print("..new data row appended to CSV cos of temp change")
                self._write_to_CSV()
                self.previous_CSV_write_millis = self.current_millis #reset timer

            
        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state
        self.previous_proc_temp = self.proc_temp
        #self.previous_CSV_write_millis = self.current_millis

        return
        
        
        
    def update_CSV_If_changes_OLD(self, temperature, humidity, vent_state,
                              fan_state, heater_state, vent_speed_state, current_millis,
                              current_time, proc_temp):
        self.temperature = temperature
        self.humidity = humidity
        self.vent_state = vent_state
        self.fan_state = fan_state
        self.heater_state = heater_state
        self.vent_speed_state = vent_speed_state
        self.current_millis = current_millis
        self.current_time = current_time
        self.proc_temp = proc_temp
        
        # update csv if any change
        # check for changes in vent values
        
        if self.vent_state != self.previous_vent_state:  # any change in vent
            #self.write_edge_change( vent_state, self.previous_vent_state)

            if self.previous_vent_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new prevvent low row appended to CSV -----")
                self.vent_state = OFF
                self._write_to_CSV()
                self.vent_state = ON  # restore to actual current val
                self._write_to_CSV()

            if self.previous_vent_state == ON:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new prevvent hi row appended to CSV -----")
                self.vent_state = ON
                self._write_to_CSV()
                self.vent_state = OFF  # restore to actual current val
                self._write_to_CSV()

        if self.vent_speed_state != self.previous_vent_speed_state:  # any change in vent speed
            if self.previous_vent_speed_state == OFF:  # was lo speed
                # write a low record immediately before hi record
                print("----- new prevvspeed low row appended to CSV -----")
                self.vent_speed_state = OFF
                self._write_to_CSV()
                self.vent_speed_state = ON  # restore to actual current val
                self._write_to_CSV()
            else:  # was hi speed going low
                # write a on record immediately before hi record
                print("----- new prevvspeed hi row appended to CSV -----")
                self.vent_speed_state = ON
                self._write_to_CSV()
                self.vent_speed_state = OFF  # restore to actual current val
                self._write_to_CSV()

        if self.fan_state != self.previous_fan_state:  # any change in vent
            #pbref=[self.fan_state]
            #self.write_edge_change(', self.previous_fan_state)

            if self.previous_fan_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new prevfanstate low row appended to CSV -----")
                self.fan_state = OFF
                self._write_to_CSV()
                self.fan_state = ON  # restore to actual current val
                self._write_to_CSV()

            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new  prevfanstate hi row appended to CSV -----")
                self.fan_state = ON
                self._write_to_CSV()
                self.fan_state = OFF  # restore to actual current val
                self._write_to_CSV()


        if self.heater_state != self.previous_heater_state:  # any change in vent
            if self.previous_heater_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("----- new heaterstate low row appended to CSV -----")
                self.heater_state = OFF
                self._write_to_CSV()
                self.heater_state = ON  # restore to actual current val
                self._write_to_CSV()
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("----- new  heaterstate hi row appended to CSV -----")
                self.heater_state = ON
                self._write_to_CSV()
                self.heater_state = OFF  # restore to actual current val
                self._write_to_CSV()

        if ((self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval))
                or (self.temperature != self.previous_temperature)):  # any change
            if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                print("..interval passed ..time for new CSV write")
            else:
                print("..new data row appended to CSV cos of temp change")
            self._write_to_CSV()
            self.previous_CSV_write_millis = self.current_millis
            
        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state
        self.previous_proc_temp = self.proc_temp
        

        return


    def _write_to_CSV(self):
        print('..write data line to CSV')
        data = ['time', 'temp', 'humi', 'heaterstate', 'ventstate', 'fanstate', 'procTemp']
        data[0] = round_time(self.current_time, 1)  # round timestamp to nearest second
#        data[0] = datetime.datetime.now() # round timestamp to nearest second

        data[1] = self.temperature
        data[2] = self.humidity
        if self.heater_state == OFF:
            data[3] = 0  # off line on graph
        else:
            data[3] = 1  # on line on graph
        if self.vent_state == OFF:
            data[4] = 0  # off line on graph
        if self.vent_state == ON:
            if self.vent_speed_state == OFF:  # vent on andspeed ==low
                data[4] = 1  # on line on graph
            if self.vent_speed_state == ON:  # vent on and hi speed
                data[4] = 2  # on line on graph
        if self.fan_state == OFF:
            data[5] = 0  # off line on graph
        else:
            data[5] = 1  # on line on graph

        data[6] = round(self.proc_temp, 1)  # add processed temp value
        print(data)
        with open(path, "ab") as csv_file:
        #with open(path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # for line in data:
            # outfile.write(bytes(plaintext, 'UTF-8'))
            writer.writerow(data)
            self.previous_CSV_write_millis = self.current_millis  # note time row written
        #self.datastore.writedb(self.current_time, self.temperature, self.humidity, self.heater_state, self.vent_state, self.fan_state)
        self.datastore.writedb(data[0], data[1], data[2], data[3], data[4], data[5])

        return

    def _write_extra_data_to_CSV(self):
        extra_data = ['time', 'temp', 'procTemp', 'round-procTemp']
        extra_data[0] = round_time(self.current_time, 1)  # round timestamp to nearest second
        extra_data[1] = temperature
        extra_data[2] = procTemp
        extra_data[3] = round(self.proc_temp, 1)
        with open(extraPath, "ab") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # for line in data:
            writer.writerow(extra_data)
        return


class system_timer(object):
    def __init__(self):
        print("creating system timer")
        self.current_hour = datetime.datetime.now().hour
        self.current_time = 0
        self.start_millis = 0
        self.current_millis = 0
        self.delta = 0
        self.d_state = OFF
        self.start_millis = datetime.datetime.now()  # get time at start of program execution
        self.update_current_millis()

    def update_current_millis(self):
        self.current_time = datetime.datetime.now()  # get current time
        self.delta = self.current_time - self.start_millis  # calc elapsed delta since program began
        self.current_millis = int(self.delta.total_seconds() * 1000)
        return

    def get_d_state(self):
        self.current_hour = datetime.datetime.now().hour
        if self.current_hour in settings.on_hours:
            self.d_state = ON
        else:
            self.d_state = OFF
            
        current_time = datetime.datetime.now()    # get time in h:m
        now = datetime.datetime.now()    # get time in h:m
        
        tlon = now.replace(hour=settings.tlon_hour, minute=settings.tlon_minute, second=0, microsecond=0)
        tloff = now.replace(hour=settings.tloff_hour, minute=settings.tloff_minute, second=0, microsecond=0) 

        #note this sectiononly works if ton < 23:59 and toff >0:0 and toff < ton
        #section start
        print( "..",current_time.time())
        print( "..",tlon.time())
        print( "..",tloff.time())
        
        self.d_state = ON	#on as default posn
        print("..ON defaul at start of range check")
        
        if (current_time.time() > tloff.time()):# and (current_time < tloff):
            print("..OFF time passed...time in OFF range")
            self.d_state = OFF
        if (current_time.time() > tlon.time()): # and (current_time.time() > tloff.time()):
            print("..ON time passed...time in ON range")
            self.d_state = ON
        #section end
        

        return self.d_state
        

class Controller(object):
    def __init__(self):
        print("init controller")
        print("---Creating system Objects---")
        self.board1 = hw.platform()
        self.sensor1 = hw.sensor()
        self.vent1 = Vent()
        self.heater1 = Heater()
        self.fan1 = Fan()
        self.logger1 = Logger()
        self.timer1 = system_timer()


print("--- crispy startup - Creating the controller---")
ctl1 = Controller()


def main():
    start_time = time.time()

    humidity, temperature = ctl1.sensor1.read()
    
    procTemp = temperature

    while 1:
        # if seetings changed - reload
        #if is_changed(settings):
        #settings = importlib.reload(settings)
            
        print("main")
#        print(round_time(ctl1.timer1.current_time, 1))
        print(ctl1.timer1.current_time)

        ctl1.timer1.update_current_millis()
        ctl1.timer1.get_d_state()

        humidity, temperature = ctl1.sensor1.read()
        
        
        ctl1.fan1.control(ctl1.timer1.current_millis)

        if ctl1.timer1.d_state == ON:
            print('.LOn')
            target_temp = settings.temp_d_on_SP
        else:  # off
            print('.LOff')
            target_temp = settings.temp_d_off_SP

        ctl1.vent1.control(ctl1.sensor1.temperature, target_temp,
                      ctl1.timer1.d_state, ctl1.timer1.current_millis)
        ctl1.heater1.control(ctl1.sensor1.temperature, target_temp,
                              ctl1.timer1.current_millis, ctl1.timer1.d_state)
        ctl1.fan1.control(ctl1.timer1.current_millis)
        ctl1.board1.switch_relays(ctl1.heater1.state, ctl1.vent1.state, ctl1.fan1.state,
                            ctl1.vent1.speed_state)  # switch relays according to State vars

        ctl1.logger1.update_CSV_If_changes(ctl1.sensor1.temperature, ctl1.sensor1.humidity,
                                      ctl1.vent1.state, ctl1.fan1.state, ctl1.heater1.state,
                                      ctl1.vent1.speed_state, ctl1.timer1.current_millis,
                                      ctl1.timer1.current_time, ctl1.sensor1.proc_temp)  # write to csv if any state changes

        end_time = time.time()
        uptime = end_time - start_time
        human_uptime = str(timedelta(seconds=int(uptime)))
        print(human_uptime)

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
