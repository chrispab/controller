#!/usr/bin/env python
# control.py
# control for HVAC controller

import logging
#logger options
###############
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
#
logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='[%(filename)s:%(lineno)s - %(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='[%(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',filename='myenvctl.log', filemode='w', level=logging.DEBUG)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', filename='myenvctl.log', filemode='w',level=logging.WARNING)
#logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

from version import VERSION
# ===================general imports=====================================

import csv
import datetime
import time
from datetime import timedelta
import yaml
import datetime as dt
import sys    # for stdout print
import socket # to get hostname
import sendemail as emailMe

from myemail import MyEmail

from Logger import Logger

import RPi.GPIO as GPIO

import subprocess
import os


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

from componentClasses import *   #components of controller board

# ============================common code start==========================

def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
    except:
        logging.error("????? cant get a network socket ?????")
        e = sys.exc_info()[0]
        logging.error( "????? Error: %s ?????" % e )
        return "cant get socket"
    return s.getsockname()[0]

def execAndTimeFunc(func):
    time1 = datetime.datetime.now()
    func()
    time2 = datetime.datetime.now()
    duration = time2 - time1
    logging.warning("TTTTTTTTTTTT - update central CONFIG table duration called BY FUNC: %s" % (duration))	


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
emailObj = MyEmail()

#cfg.
def main():

    #call to systemd watchdog to hold off restart
    ctl1.timer1.holdOffWatchdog(0, True)
    
    start_time = time.time()
    humidity, temperature, sensorMessage = ctl1.sensor1.read()

    global systemUpTime
    global processUptime
    global systemMessage
    global controllerMessage
    global miscMessage
    
    
    #TODO ENABLE EMAIL ENABLED OBEY
    zone = cfg.getItemValueFromConfig('zoneName')
    location = cfg.getItemValueFromConfig('locationDisplayName')
    message = zone
    #if just booted
    if ctl1.timer1.secsSinceBoot() < 120:
        zone = zone + ' REBOOT '
    
    #emailMe.sendemail( zone + ' ' + location + ' - Process Started', message)
    emailObj.send( zone + ' emailObj ' + location + ' - Process Started', message)
                
    while 1:

        logging.info("=main=")
        #logging.warning("== process uptime: %s =",processUptime)

        logging.debug(socket.gethostname())
        logging.info("current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.updateClocks()
        current_millis = ctl1.timer1.current_millis
        
        #call to systemd watchdog to hold off restart
        ctl1.timer1.holdOffWatchdog(current_millis)

        startT = time.time()
        
        #read sensor
        humidity, temperature,sensorMessage = ctl1.sensor1.read()
        if sensorMessage :
            #emailMe.sendemail(zone + ': bad sensor reads ' + str(maxSensorReadErrors) + '  - PowerCycle', self.message)	
            emailObj.send(zone + ': bad sensor reads  - PowerCycle', sensorMessage)

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
                    emailObj.send( zone + ' - Hi Temp warning' + temperature, message)
                except:
                    logging.error("...ERROR SENDING EMAIL - for hi temp alert")
                    
            if temperature < cfg.getItemValueFromConfig('tempAlertLo'):
                try:
                    emailObj.send( zone + ' - Lo Temp warning' + temperature, message)
                except:
                    logging.error("...ERROR SENDING EMAIL - low temp alert")
                                    
            location = cfg.getItemValueFromConfig('locationDisplayName')
            logging.warning("LLLLLLLLLL - loc : %s" % (location))
            
            end_time = time.time()
            processUptime = end_time - start_time
            processUptime = str(timedelta(seconds=int(processUptime)))
            #cfg.setConfigItemInLocalDB('processUptime', "Process Up Time: " +processUptime)
            cfg.setConfigItemInLocalDB('processUptime', processUptime)

            systemUpTime = ctl1.timer1.getSystemUpTimeFromProc()
            #cfg.setConfigItemInLocalDB('systemUpTime',  "System Up Time: " + systemUpTime)
            cfg.setConfigItemInLocalDB('systemUpTime', systemUpTime)
            
            cfg.setConfigItemInLocalDB('miscMessage', location)
            
            systemMessage = ctl1.timer1.getUpTime().strip()
            cfg.setConfigItemInLocalDB('systemMessage', systemMessage  )

            ipAddress = get_ip_address()
            cfg.setConfigItemInLocalDB('controllerMessage', "V: " +  VERSION + ", IP: " + "<a href=" + "https://" + ipAddress + ":10000" + ' target="_blank"' + ">"+ ipAddress + "</a>")


            cfg.setConfigItemInLocalDB('lightState', int(lightState) )
            
            #time1 = datetime.datetime.now()
            #cfg.updateCentralConfigTable()
            #time2 = datetime.datetime.now()
            #duration = time2 - time1
            #logging.warning("TTTTT - update central CONFIG table duration : %s" % (duration))
            
            execAndTimeFunc(cfg.updateCentralConfigTable)
            
            #uptime = cfg.getConfigItemFromLocalDB('processUptime')
            logging.warning("======== process uptime: %s ======", processUptime)
            mem = psutil.virtual_memory()
            #logging.warning("MMMMMM total memory       : %s MMMMMM",mem.total)

            #logging.warning("MMMMMM memory available   : %s MMMMMM",mem.available)
            logging.warning("MMMMMM memory pc.available: %0.2f MMMMMM",((float(mem.available)/float(mem.total)))*100)
            #logging.warning("======== % memory available: %s ======",mem.percent)

        sys.stdout.write(">")
        sys.stdout.flush()
        #tracker.print_diff()
        #logging.warning(mem_top()) # Or just print().



if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
