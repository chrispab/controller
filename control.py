#!/usr/bin/env python
# control.py
# control for enviro controller

# ===================general imports=====================================
import csv
import datetime
import time
from datetime import timedelta

import hardware as hw
import settings
from support import round_time as round_time

# ============targets/settings/tuneable params from settings file========
#temp_alarm = settings.temp_alarm  # 26
#readDelay = settings.readDelay
#minCSVWriteInterval = settings.min_CSV_write_interval  # 3 * 60 * 1000 #interval min bet csv writes

# ----L control params----
#onHours = settings.on_hours  # hours when l on
#heat_off_hours = settings.heat_off_hours  # hours when heater should NOT operate

OFF = settings.OFF  # state for relay OFF
ON = settings.ON  # state for on

path = settings.dataPath
extraPath = settings.extraPath

# ===========initial settings============================================
#temperature = 20  # global temp var
#humidity = 50  # global humidity var
#procTemp = temperature

# initial state parameter global var values
#heaterState = OFF
#ventState = ON
#fanState = ON
#ventSpeedState = OFF
#lState = OFF

# =================initialised global vars etc===========================
#currentMillis = 0
#previousTemperature = 24
#previousProcTemp = 24
#previousHumidity = 40

#previousHeaterState = ON
#previousVentState = OFF
#previousFanState = OFF
#previousVentSpeedState = OFF
#prevTempHumiMillis = 0  # previous time  sensors routine called and data read
#prevHeaterMillis = 0  # last time heater switched on or off

# Vent control parameters
#prevVentMillis = 0
#ventPulseActive = False
#ventOverride = OFF

# Fan control parameters
#prevFanMillis = 0  # last time vent state updated
#previousCSVWriteMillis = 0  # last time CSV file row added

# general time use params
#startMillis = 0  # time at start of program execution
#currentTime = 0
#start_time = time.time()
#up_time = time.time()


# ============================common code start==========================

class Relay(object):
    def __init__(self):
        print("creating relay - dummy so far")


class Vent(object):
    def __init__(self):
        print("creating vent")
        self.state = OFF
        self.speed_state = OFF
        self.prev_vent_millis = 0  # last time vent state updated
        self.vent_on_delta = settings.ventOnDelta  # vent on time
        self.vent_off_delta = settings.ventOffDelta  # vent off time
        self.vent_pulse_active = OFF  # settings.ventPulseActive
        self.vent_pulse_delta = 0  # ventPulseDelta
        self.vent_pulse_on_delta = settings.ventPulseOnDelta
        self.vent_override = OFF  # settings.ventOverride

    def control(self, current_temp, target_temp, d_state, current_millis):
        print('.Vent ctl')


        if d_state == ON:
            self.speed_state = ON  # high speed
        else:
            self.speed_state = OFF  # lo speed

        if current_temp > target_temp:
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
        
        #self.state = ON
        
        print(' ')
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

    def control(self, current_temp, target_temp, current_millis, d_state):
        print('.Heat ctl')
        #if d_state == ON:
        current_hour = datetime.datetime.now().hour
        if current_hour in settings.heat_off_hours:  # l on and not 10:xx pm
            print('..d on, in heat off hours - skipping lon heatctl')
        else:#d state on or off here
            print('..do lon or off heatctl')
            if current_temp >= target_temp:  # if over temp immediately turn off
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
        # self.writeExtraDataToCSV()
        
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
        """ Function doc """

        # if time between 7am and 7pm L on else L off
        self.current_hour = datetime.datetime.now().hour
        if self.current_hour in settings.on_hours:
            self.d_state = ON
        else:
            self.d_state = OFF

        return self.d_state

class Controller(object):
    def __init__(self):
        print("creating controller")
        print("---Creating Objects---")
        self.board1 = hw.platform()
        self.sensor1 = hw.sensor()
        self.vent1 = Vent()
        self.heater1 = Heater()
        self.fan1 = Fan()
        self.logger1 = Logger()
        self.timer1 = system_timer()


print("---Creating the controller---")
ctl1 = Controller()


def main():
    #print("---Creating the controller---")
    #ctl1 = Controller()
    #print("---Creating Objects---")
    #board1 = hw.platform()
    #sensor1 = hw.sensor()
    #vent1 = Vent()
    #heater1 = Heater()
    #fan1 = Fan()
    #logger1 = Logger()
    #timer1 = system_timer()

    start_time = time.time()

    humidity, temperature = ctl1.sensor1.read()
    
    procTemp = temperature

    while 1:
        print("main")
        print(round_time(ctl1.timer1.current_time, 1))

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
