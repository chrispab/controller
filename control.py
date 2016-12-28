#!/usr/bin/env python
# control.py
# control for enviro controller

# ===================general imports=====================================
import csv
import datetime
import time
from datetime import timedelta
import yaml
import datetime as dt
import sys    # for stdout print
import socket # to get hostname 


#my classes
#from ConfigClass import Config #config object with settings in
#from DatabaseClass import Database
from DatabaseObject import db # singleton global
from ConfigObject import cfg # singleton global


##note: hostName expected zone1 or zone2
#hostName = socket.gethostname()
#settingsFileName = 'settings_' + hostName
#print(settingsFileName)
##import as settings
#settings = __import__(settingsFileName)


import hardware as hw

from support import round_time as round_time

OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on

path = cfg.getItemValueFromConfig('dataPath')
#extraPath = cfg.getItemValueFromConfig('extraPath')


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
        self.speed_state_trigger = 5  # trigger hi state on n counts hi
        self.prev_vent_millis = 0  # last time vent state updated
        self.vent_on_delta = cfg.getItemValueFromConfig('ventOnDelta')  # vent on time
        self.vent_off_delta = cfg.getItemValueFromConfig('ventOffDelta')  # vent off time
        self.vent_pulse_active = OFF  # settings.ventPulseActive
        self.vent_pulse_delta = 0  # ventPulseDelta
        self.vent_pulse_on_delta = cfg.getItemValueFromConfig('ventPulseOnDelta')
        self.vent_loff_sp_offset = cfg.getItemValueFromConfig('vent_loff_sp_offset')
        self.vent_lon_sp_offset = cfg.getItemValueFromConfig('vent_lon_sp_offset')


        self.vent_override = OFF  # settings.ventOverride

    def control(self, current_temp, target_temp, d_state, current_millis):
        print('==Vent ctl==')

        if d_state == ON:
            self.speed_state = ON  # high speed
        else:
            self.speed_state = OFF  # lo speed

        #self.speed_state = OFF  # lo speed

        # loff vent/cooling
        if ((d_state == OFF) and (current_temp > target_temp + self.vent_loff_sp_offset)):
            self.vent_override = ON
            self.state = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            print("..VENT ON Loff - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")

        if ((d_state == ON) and (current_temp > target_temp + self.vent_lon_sp_offset)):
            self.vent_override = ON
            self.state = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            print("..VENT ON - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")
        # temp below target, change state to OFF after pulse delay
        elif (self.vent_override == ON) and ((current_millis - self.prev_vent_millis) >= self.vent_pulse_on_delta):
            self.state = OFF
            self.vent_override = OFF
            self.prev_vent_millis = current_millis
            print("..VENT OFF - temp ok, OVERRIDE - OFF")
        elif self.vent_override == ON:
            print('..Vent on - override in progress')

        # periodic vent control - only execute if vent ovveride not active
        if self.vent_override == OFF:  # process periodic vent activity
            if self.state == OFF:  # if the vent is off, we must wait for the interval to expire before turning it on
                # iftime is up, so change the state to ON
                if current_millis - self.prev_vent_millis >= self.vent_off_delta:
                    self.state = ON
                    print("..VENT ON cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    print('..Vent off - during cycle OFF period')
            else:
                # vent is on, we must wait for the duration to expire before
                # turning it off
                # time up, change state to OFF
                if (current_millis - self.prev_vent_millis) >= self.vent_on_delta:
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
        self.fan_on_delta = cfg.getItemValueFromConfig('fan_on_t')  # vent on time
        self.fan_off_delta = cfg.getItemValueFromConfig('fan_off_t')  # vent off time

    def control(self, current_millis):
        print('==fan ctl==')
        # if fan off, we must wait for the interval to expire before turning it
        # on
        print('==current millis: %s' % (current_millis))
        print('==current fan state: %s' % (self.state))
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
        self.heater_off_delta = cfg.getItemValueFromConfig('heater_off_t')  # min time heater is on or off for
        self.heater_on_delta = cfg.getItemValueFromConfig('heater_on_t')  # min time heater is on or off for
        self.prev_heater_millis = 0  # last time heater switched on or off
        self.heater_sp_offset = cfg.getItemValueFromConfig('heater_sp_offset')

    def control(self, current_temp, target_temp, current_millis, d_state):
        print('==Heat ctl==')
        # if d_state == ON:
        current_hour = datetime.datetime.now().hour
        if current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm
            self.state = OFF
            print('..d on, in heat off hours - skipping lon heatctl')
            # oveeride
            #self.state = ON
        else:  # d state on or off here
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
                    print(
                        '...in heat auto cycle - Heater still on - during low temp heat pulse')
            elif current_millis - self.prev_heater_millis >= self.heater_off_delta:  # heater is off, turn on after delta
                self.state = ON
                print("...in heat auto cycle - switch HEATER ON")
                self.prev_heater_millis = current_millis
            else:
                print("...in heat auto cycle - during heat OFF period")
        # else:
            #print("..in d-off, no heat ctl")

        print(' ')
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
        self.min_CSV_write_interval = cfg.getItemValueFromConfig('min_CSV_write_interval')
        #self.datastore = Database()



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
        print('==Update CSV==')

        # check each for state change and set new prewrite states
        if self.vent_state != self.previous_vent_state:  # any change in vent
            if self.previous_vent_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("--new prevvent low row appended to CSV -----")
                self.vent_state = OFF
                self.state_changed = True
            else:  # if self.previous_vent_state == ON:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("-- new prevvent hi row appended to CSV -----")
                self.vent_state = ON
                self.state_changed = True

        if self.vent_speed_state != self.previous_vent_speed_state:  # any change in vent speed
            if self.previous_vent_speed_state == OFF:  # was lo speed
                # write a low record immediately before hi record
                print("-- new prevvspeed low row appended to CSV -----")
                self.vent_speed_state = OFF
                self.state_changed = True
            else:  # was hi speed going low
                # write a on record immediately before hi record
                print("-- new prevvspeed hi row appended to CSV -----")
                self.vent_speed_state = ON
                self.state_changed = True

        if self.fan_state != self.previous_fan_state:  # any change in vent
            if self.previous_fan_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("-- new prevfanstate low row appended to CSV -----")
                self.fan_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("-- new  prevfanstate hi row appended to CSV -----")
                self.fan_state = ON
                self.state_changed = True

        if self.heater_state != self.previous_heater_state:  # any change in vent
            if self.previous_heater_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                print("-- new heaterstate low row appended to CSV -----")
                self.heater_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                print("-- new  heaterstate hi row appended to CSV -----")
                self.heater_state = ON
                self.state_changed = True

        # if ((self.temperature != self.previous_temperature)):  # any change
            #self.state_changed = True

        if self.state_changed == True:
            self._write_to_CSV()  # write modded pre change state(s)
            self.vent_state = vent_state
            self.vent_speed_state = vent_speed_state
            self.heater_state = heater_state
            self.fan_state = fan_state
            self._write_to_CSV()  # write modded post change state(s)
            self.previous_CSV_write_millis = self.current_millis  # reset timer
        else:  # no state change check temp and timer
            if ((self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval))
                    or (self.temperature != self.previous_temperature)):  # any change
                if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                    print("..interval passed ..time for new CSV write")
                else:
                    print("..new data row appended to CSV cos of temp change")
                self._write_to_CSV()
                self.previous_CSV_write_millis = self.current_millis  # reset timer

        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state
        self.previous_proc_temp = self.proc_temp
        #self.previous_CSV_write_millis = self.current_millis

        return



    def _write_to_CSV(self):
        print('===write data line to CSV')
        data = ['time', 'temp', 'humi', 'heaterstate',
                'ventstate', 'fanstate', 'procTemp']
        # round timestamp to nearest second
        data[0] = round_time(self.current_time, 1)
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
        #sys.stdout.write(data.tostring() )
        with open(path, "ab") as csv_file:
            # with open(path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # for line in data:
            # outfile.write(bytes(plaintext, 'UTF-8'))
            writer.writerow(data)
            self.previous_CSV_write_millis = self.current_millis  # note time row written
        #self.datastore.writedb(self.current_time, self.temperature, self.humidity, self.heater_state, self.vent_state, self.fan_state)
        db.writedb(data[0], data[1], data[
                               2], data[3], data[4], data[5])

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
        # get time at start of program execution
        self.start_millis = datetime.datetime.now()
        self.update_current_millis()

    def update_current_millis(self):
        self.current_time = datetime.datetime.now()  # get current time
        # calc elapsed delta since program began
        self.delta = self.current_time - self.start_millis
        self.current_millis = int(self.delta.total_seconds() * 1000)
        return
    
    def getUpTime(self):
        # get uptime from the linux terminal command
        from subprocess import check_output
        uptime = check_output(["uptime"])
        # return only uptime info
        #uptime = output[output.find("up"):output.find("user")-5]
        #uptime = output
        return uptime
    


class Light(object):
    def __init__(self):
        print("creating light object")
        self.state = OFF
        self.tOn = dt.time()
        self.tOff = dt.time()

    def testGetLightState(self): # testing only routine
        print("??Running get lightstate stet??")
        tOn = dt.time(21,0,0)
        tOff = dt.time(9,0,0)

        for hour in range(0,24):
            for minute in range(0,60):
                print ( hour, minute, tOn, tOff, dt.time(hour,minute))
                print(self.getLightState(tOn, tOff, dt.time(hour,minute)))
                #print("--------")
                
        return
        
    #return true if testTime between timeOn and TimeOff, else false if in off period
    def getLightState(self ):   
        #print('==light - get light state==')

        tOff = cfg.getTOff()
        tOn = cfg.getTOn()
        currT = datetime.datetime.now().time()
        X = False
        if (tOn > tOff):
            X = True
            
        lightState = OFF
        if (( currT > tOn) and (currT < tOff)):
            lightState = ON
        #if ( currT > tOff):
         #   lightState = False
        if (((currT > tOn) or (currT < tOff)) and ( X )):
            lightState = ON

        print ("==light check. ON: %s, OFF: %s, NOW: %s, state: %d" % (tOn.strftime("%H:%M:%S"), tOff.strftime("%H:%M:%S"), currT.strftime("%H:%M:%S"), lightState))

        self.d_state = lightState
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
        self.light = Light()
        self.logger1 = Logger()
        self.timer1 = system_timer()
        #self.config = Config()


print("--- crispy startup - Creating the controller---")
ctl1 = Controller()


def main():
    start_time = time.time()
    humidity, temperature = ctl1.sensor1.read()
    while 1:
        print("=main=")
        print(socket.gethostname())
        print("=current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.update_current_millis()
        current_millis = ctl1.timer1.current_millis
        humidity, temperature = ctl1.sensor1.read()
        lightState = ctl1.light.getLightState()
        heaterState = ctl1.heater1.state
        ventState = ctl1.vent1.state
        fanState = ctl1.fan1.state
        ventSpeedState = ctl1.vent1.speed_state
        if lightState == ON:
            print('=LOn=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOn')

        else:  # off
            print('=LOff=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOff')
        print(target_temp)
        
        ctl1.fan1.control(current_millis)
        ctl1.vent1.control(temperature, target_temp, lightState, current_millis)
        ctl1.heater1.control(temperature, target_temp, current_millis, lightState)
        ctl1.fan1.control(current_millis)
        ctl1.board1.switch_relays(heaterState, ventState, fanState, ventSpeedState)  # switch relays according to State vars
        ctl1.logger1.update_CSV_If_changes(temperature, humidity, ventState, fanState, heaterState, ventSpeedState,
            current_millis, ctl1.timer1.current_time, ctl1.sensor1.proc_temp)  # write to csv if any state changes
        end_time = time.time()
        processUptime = end_time - start_time
        processUptime = str(timedelta(seconds=int(processUptime)))
        systemMessage = ctl1.timer1.getUpTime().strip()
        cfg.setConfigItemInDB('processUptime', processUptime)
        cfg.setConfigItemInDB('systemMessage', systemMessage )
        print('=Process uptime: %s' % (processUptime))
        print('=System message: %s' % (systemMessage))
        #print('=System uptime: %s' % (systemUptime))
        
        cfg.updateCentralConfigTable()



if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
