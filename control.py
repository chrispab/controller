#!/usr/bin/env python
# control.py
# control for enviro controller

import logging
#logger options
###############
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
#
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='[%(filename)s:%(lineno)s - %(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='[%(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',filename='myenvctl.log', filemode='w', level=logging.DEBUG)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', filename='myenvctl.log', filemode='w',level=logging.WARNING)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

VERSION = "0.30 hw watchdog 1"

# ===================general imports=====================================
#from pympler.tracker import SummaryTracker
#tracker = SummaryTracker()

#from mem_top import mem_top

import csv
import datetime
import time
from datetime import timedelta
import yaml
import datetime as dt
import sys    # for stdout print
import socket # to get hostname
import sendemail as emailMe
from Logger import Logger

import RPi.GPIO as GPIO

import subprocess
import os

import psutil

#my singleton objects
from DatabaseObject import db # singleton global
from ConfigObject import cfg # singleton global

import hardware as hw
from support import round_time as round_time

OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on

path = cfg.getItemValueFromConfig('dataPath')

processUptime = 0
systemMessage = 0

# ============================common code start==========================

class Relay(object):

    def __init__(self):
        logging.info("creating relay - dummy so far")


class Vent(object):

    def __init__(self):
        logging.info("creating vent")
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
        self.platformName = cfg.getItemValueFromConfig('hardware')

        self.vent_override = OFF  # settings.ventOverride

    def control(self, current_temp, target_temp, d_state, current_millis):
        logging.info('==Vent ctl==')
        self.speed_state = OFF  # lo speed
        if (self.platformName == 'RaspberryPi2'):
            if d_state == ON:
                self.speed_state = ON  # high speed
            else:
                self.speed_state = OFF  # lo speed



        # loff vent/cooling
        if ((d_state == OFF) and (current_temp > target_temp + self.vent_loff_sp_offset)):
            self.vent_override = ON
            self.state = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            logging.info("..VENT ON Loff - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")

        if ((d_state == ON) and (current_temp > target_temp + self.vent_lon_sp_offset)):
            self.vent_override = ON
            self.state = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            logging.info("..VENT ON - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")
        # temp below target, change state to OFF after pulse delay
        elif (self.vent_override == ON) and ((current_millis - self.prev_vent_millis) >= self.vent_pulse_on_delta):
            self.state = OFF
            self.vent_override = OFF
            self.prev_vent_millis = current_millis
            logging.info("..VENT OFF - temp ok, OVERRIDE - OFF")
        elif self.vent_override == ON:
            logging.info('..Vent on - override in progress')

        # periodic vent control - only execute if vent ovveride not active
        if self.vent_override == OFF:  # process periodic vent activity
            if self.state == OFF:  # if the vent is off, we must wait for the interval to expire before turning it on
                # iftime is up, so change the state to ON
                if current_millis - self.prev_vent_millis >= self.vent_off_delta:
                    self.state = ON
                    logging.info("..VENT ON cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    logging.info('..Vent off - during cycle OFF period')
            else:
                # vent is on, we must wait for the duration to expire before
                # turning it off
                # time up, change state to OFF
                if (current_millis - self.prev_vent_millis) >= self.vent_on_delta:
                    self.state = OFF
                    logging.info("..VENT OFF cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    logging.info('..Vent on - during cycle ON period')
        return


class Fan(object):

    def __init__(self):
        logging.info("Creating fan")
        self.state = OFF
        self.prev_fan_millis = 0  # last time vent state updated
        self.fan_on_delta = cfg.getItemValueFromConfig('fan_on_t')  # vent on time
        self.fan_off_delta = cfg.getItemValueFromConfig('fan_off_t')  # vent off time

    def control(self, current_millis):
        logging.info('==fan ctl==')
        # if fan off, we must wait for the interval to expire before turning it on
        logging.info('==current millis: %s' % (current_millis))
        logging.info('==current fan state: %s' % (self.state))
        if self.state == OFF:
            # if time is up, so change the state to ON
            if current_millis - self.prev_fan_millis >= self.fan_off_delta:
                self.state = ON
                logging.info("..FAN ON")
                self.prev_fan_millis = current_millis
        # else if fanState is ON
        else:
            # time is up, so change the state to LOW
            if (current_millis - self.prev_fan_millis) >= self.fan_on_delta:
                self.state = OFF
                logging.info("..FAN OFF")
                self.prev_fan_millis = current_millis
        #self.state = ON
        return


class Heater(object):

    def __init__(self):
        logging.info("creating heater")
        self.state = OFF
        self.heater_off_delta = cfg.getItemValueFromConfig('heater_off_t')  # min time heater is on or off for
        self.heater_on_delta = cfg.getItemValueFromConfig('heater_on_t')  # min time heater is on or off for
        self.prev_heater_millis = 0  # last time heater switched on or off
        self.heater_sp_offset = cfg.getItemValueFromConfig('heater_sp_offset')

    def control(self, current_temp, target_temp, d_state, current_millis):
        logging.info('==Heat ctl==')
        #calc new heater on t based on t gap
        self.heater_on_delta = ((target_temp - current_temp) * 80 * 1000)  + cfg.getItemValueFromConfig('heater_on_t')
        logging.info('==Heat tdelta on: %s',self.heater_on_delta)

        #check for heater OFF hours #todo improve this
        current_hour = datetime.datetime.now().hour
        #if current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm
        if d_state == ON: #current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm

            self.state = OFF
            logging.info('..d on, in heat off hours - skipping lon heatctl')
        else:  # d state on or off here also in heat on hrs
            logging.info('..do heatctl')
            if current_temp >= target_temp + self.heater_sp_offset:  # if over temp immediately turn off
                self.state = OFF
                logging.info("...temp over sp - HEATER OFF")
                self.prev_heater_millis = current_millis
            elif self.state == ON:  # t below tsp if time is up, so check if change the state to OFF
                if current_millis - self.prev_heater_millis >= self.heater_on_delta:
                    self.state = OFF
                    logging.info("...in heat auto cycle - switch HEATER OFF after pulse on")
                    self.prev_heater_millis = current_millis
                else:
                   logging.info('in heat auto cycle - Heater still on - during low temp heat pulse')
            elif current_millis - self.prev_heater_millis >= self.heater_off_delta:  # heater is off, turn on after delta
                self.state = ON
                logging.info("...in heat auto cycle - switch HEATER ON")
                self.prev_heater_millis = current_millis
            else:
                logging.info("...in heat auto cycle - during heat OFF period")
        # else:
            #print("..in d-off, no heat ctl")
        logging.info('Heater state: %s' , ('OFF' if self.state else 'ON') )
        return




class system_timer(object):

    def __init__(self):
        logging.info("creating system timer")
        self.current_hour = datetime.datetime.now().hour
        self.current_time = 0
        self.start_millis = 0
        self.current_millis = 0
        self.delta = 0
        self.d_state = OFF
        self.prevWDPulseMillis = 0
        self.WDPeriod = 60000   #systend sofware process watchdog holdoff space period
        # get time at start of program execution
        self.start_millis = datetime.datetime.now()
        self.updateClocks()

    def holdOffWatchdog(self, current_millis):
        
        logging.info('==Hold Off Watchdog==')
        logging.info('==current millis: %s' % (current_millis))
        #logging.info('==current fan state: %s' % (self.state))
        #if self.state == OFF:
            # if time is up, so change the state to ON
        if current_millis - self.prevWDPulseMillis >= self.WDPeriod:
            #uptime = cfg.getConfigItemFromLocalDB('processUptime')
            #logging.warning("== process uptime: %s =", uptime)

            logging.info("- Pat the DOG - WOOF -")
            #print('==WOOF==')
            #reset timer
            self.prevWDPulseMillis = current_millis
            # else if fanState is ON
            
            
            #sd_notify(0, WATCHDOG_READY)
            #subprocess.call(['/bin/systemd-notify WATCHDOG=1'], shell=True)
            #subprocess.call(['/bin/systemd-notify','--pid=' + str(os.getpid()),'WATCHDOG=1'] shell=True)
            #subprocess.call(["/bin/systemd-notify","--pid=" + str(os.getpid()),"WATCHDOG=1"] shell=True)
            #subprocess.call(['/bin/systemd-notify','--pid=' + str(os.getpid()),'WATCHDOG=1'], shell=True)
            
            #sys.stderr.write("starting : python daemon watchdog and fail test script started\n")
            # notify systemd that we've started
            #retval = sd_notify(0, "READY=1")
            #if retval <> 0:
                #sys.stderr.write("terminating : fatal sd_notify() error for script start\n")
                #exit(1)
    
            # after the init, ping the watchdog and check for errors
            retval = sd_notify(0, "WATCHDOG=1")
            logging.warning("+++++ Patted the DOG - WOOF +++++")
            if retval <> 0:
                sys.stderr.write("terminating : fatal sd_notify() error for watchdog ping\n")
                #exit(1)

        #sys.stdout.write("WF")
        #sys.stdout.flush()
        return
        

    
    

    def updateClocks(self):
        self.current_time = datetime.datetime.now()  # get current time
        # calc elapsed delta ms since program began
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


    def getSystemUpTime(self):
        # get uptime from the linux terminal command
        from subprocess import check_output
        output = check_output(["uptime"])
        # return only uptime info
        uptime = output[output.find("up")+2:output.find("user")-5]
        
        return uptime
    
    def seconds_elapsed(self):
        now = datetime.datetime.now()
        current_timestamp = time.mktime(now.timetuple())
        return current_timestamp - psutil.boot_time()
    
class Light(object):
    def __init__(self):
        logging.info("creating light object")
        self.state = OFF
        self.tOn = dt.time()
        self.tOff = dt.time()

    #return true if testTime between timeOn and TimeOff, else false if in off period
    def getLightState(self ):
        logging.info('==light - get light state==')

        tOff = cfg.getTOff()
        tOn = cfg.getTOn()
        currT = datetime.datetime.now().time()
        X = False
        if (tOn > tOff):
            X = True

        lightState = OFF
        if (( currT > tOn) and (currT < tOff)):
            lightState = ON
        if (((currT > tOn) or (currT < tOff)) and ( X )):
            lightState = ON

        logging.debug("==light state check. ON: %s, OFF: %s, NOW: %s, state: %d" % (tOn.strftime("%H:%M:%S"), tOff.strftime("%H:%M:%S"), currT.strftime("%H:%M:%S"), lightState))


        #new ldr based routine test
        #print("hi")
        count = RCtime(cfg.getItemValueFromConfig('RCPin')) # Measure timing using GPIO4
        #print count

        if ( count > 2000):
            #sys.stdout.write("OFF")
            #sys.stdout.flush()
            lightState = OFF

            #print("OFF")
        else:
            #sys.stdout.write("ON")
            #sys.stdout.flush()
            #print("ON")
            lightState = ON

        #sys.stdout.write(str(count))
        #sys.stdout.flush()

        self.d_state = lightState


        return self.d_state

# Function to measure res-cap charge time
def RCtime (RCPin):
    # Discharge capacitor
    GPIO.setup(RCPin, GPIO.OUT)
    GPIO.output(RCPin, GPIO.LOW)
    time.sleep(0.1) #give time for C to discharge
    GPIO.setup(RCPin, GPIO.IN)  #set RC pin to hi impedance
    # Count loops until voltage across capacitor reads high on GPIO
    measurement = 0
    while (GPIO.input(RCPin) == GPIO.LOW) and (measurement < 9999):
        measurement += 1
    return measurement


init = True
def sd_notify(unset_environment, s_cmd):

    """
    Notify service manager about start-up completion and to kick the watchdog.

    https://github.com/kirelagin/pysystemd-daemon/blob/master/sddaemon/__init__.py

    This is a reimplementation of systemd's reference sd_notify().
    sd_notify() should be used to notify the systemd manager about the
    completion of the initialization of the application program.
    It is also used to send watchdog ping information.

    """
    global init

    sock = None

    try:
        if not s_cmd:
            sys.stderr.write("error : missing s_cmd\n")
            return(1)

        s_adr = os.environ.get('NOTIFY_SOCKET', None)
        if init : # report this only one time
            sys.stderr.write("Notify socket xxx = " + str(s_adr) + "\n")
            # this will normally return : /run/systemd/notify
            init = False

        if not s_adr:
            sys.stderr.write("error : missing socket\n")
            return(1)

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.sendto(s_cmd, s_adr)
        # sendto() returns number of bytes send
        # in the original code, the return was tested against > 0 ???
        if sock.sendto(s_cmd, s_adr) == 0:
            sys.stderr.write("error : incorrect sock.sendto  return value\n")
            return(1)
    except e:
        pass
    finally:
        # terminate the socket connection
        if sock:
            sock.close()
        if unset_environment:
            if 'NOTIFY_SOCKET' in os.environ:
                del os.environ['NOTIFY_SOCKET']
    return(0) # OK

class Controller(object):

    def __init__(self):
        logging.info("init controller")
        #start the c watchdog
        #logging.warning("WWWWW starting my_watchdog WWWWW")
#        os.system("sudo ./watchdog/my_watchdog &")
        #os.system("sudo ./watchdog/my_watchdog -r &")

        #subprocess.call(["sudo","./watchdog/my_watchdog"])                

        
        logging.info("---Creating system Objects---")
        self.board1 = hw.platform()
        self.sensor1 = hw.sensor()
        self.vent1 = Vent()
        self.heater1 = Heater()
        self.fan1 = Fan()
        self.light = Light()
        self.stateMonitor = Logger()
        self.timer1 = system_timer()


#main routine
#############
logging.info("--- Creating the controller---")
ctl1 = Controller()

#cfg.
def main():

    
    
    start_time = time.time()
    humidity, temperature = ctl1.sensor1.read()

    global systemUpTime
    global processUptime
    global systemMessage
    
    zone = cfg.getItemValueFromConfig('zoneName')
    message = zone
    if ctl1.timer1.seconds_elapsed() < 120:
        zone = zone + ' REBOOT '
    try:
        emailMe.sendemail( zone + ' - Process Started', message)
    except:
        logging.error("...ERROR SENDING EMAIL - for Process start")

        
    while 1:
        logging.info("=main=")
        #logging.warning("== process uptime: %s =",processUptime)

        logging.debug(socket.gethostname())
        logging.info("current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.updateClocks()
        current_millis = ctl1.timer1.current_millis

        startT = time.time()
        humidity, temperature = ctl1.sensor1.read()
        endT= time.time()
        duration = endT-startT
        logging.debug("+++ Aquisition sampletime: %s +++",duration)

        #get all states
        lightState = ctl1.light.getLightState()
        heaterState = ctl1.heater1.state
        ventState = ctl1.vent1.state
        fanState = ctl1.fan1.state
        ventSpeedState = ctl1.vent1.speed_state

        if lightState == ON:
            logging.info('=LOn=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOn')
        else:  # off
            logging.info('=LOff=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOff')
        logging.info(target_temp)

        ctl1.fan1.control(current_millis)
        ctl1.vent1.control(temperature, target_temp, lightState, current_millis)
        ctl1.heater1.control(temperature, target_temp, lightState, current_millis)
        ctl1.fan1.control(current_millis)
        ctl1.board1.switch_relays(heaterState, ventState, fanState, ventSpeedState)  # switch relays according to State vars
        stateChanged = ctl1.stateMonitor.checkForChanges(temperature, humidity, ventState,
                                    fanState, heaterState, ventSpeedState,
                                    current_millis, ctl1.timer1.current_time)  # write to csv/db etc if any state changes
        if stateChanged :
            logging.warning("======== start state changed main list ======")
            # check for alarm levels etc
            if temperature > cfg.getItemValueFromConfig('tempAlertHi'):
                try:
                    emailMe.sendemail( zone + ' - Hi Temp warning' + temperature, message)
                except:
                    logging.error("...ERROR SENDING EMAIL - for Process start")
                    
            if temperature < cfg.getItemValueFromConfig('tempAlertLo'):
                try:
                    emailMe.sendemail( zone + ' - Lo Temp warning' + temperature, message)
                except:
                    logging.error("...ERROR SENDING EMAIL - for Process start")
                                    
            end_time = time.time()
            processUptime = end_time - start_time
            processUptime = str(timedelta(seconds=int(processUptime)))
            systemUpTime = ctl1.timer1.getSystemUpTime()
            systemMessage = ctl1.timer1.getUpTime().strip()
            cfg.setConfigItemInLocalDB('systemUpTime', " Ver: " + VERSION + " : " + systemUpTime)

            cfg.setConfigItemInLocalDB('processUptime', processUptime)
            cfg.setConfigItemInLocalDB('systemMessage', systemMessage + ". V" + VERSION )
            cfg.setConfigItemInLocalDB('lightState', int(not(lightState)) )
            
            time1 = datetime.datetime.now()
            cfg.updateCentralConfigTable()
            time2 = datetime.datetime.now()
            duration = time2 - time1
            logging.warning("TTTTT - update central CONFIG table duration : %s" % (duration))
            
            #uptime = cfg.getConfigItemFromLocalDB('processUptime')
            logging.warning("======== process uptime: %s ======", processUptime)
            mem = psutil.virtual_memory()
            #logging.warning("MMMMMM total memory       : %s MMMMMM",mem.total)

            #logging.warning("MMMMMM memory available   : %s MMMMMM",mem.available)
            logging.warning("MMMMMM memory pc.available: %0.2f MMMMMM",((float(mem.available)/float(mem.total)))*100)
            #logging.warning("======== % memory available: %s ======",mem.percent)

            
        
        sys.stdout.write(">")
        sys.stdout.flush()

        #call to systemd watchdog to hold off restart
        ctl1.timer1.holdOffWatchdog(current_millis)
        #tracker.print_diff()
        #logging.warning(mem_top()) # Or just print().



if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
