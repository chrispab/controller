#!/usr/bin/env python
# hardware.py
# hardware specific for rpi platform
#for control.py for enviro controller
#

# general im ports
from time import sleep
import datetime
import sendemail as emailMe


##import settings
#import socket # to get hostname 
##note: hostName expected zone1 or zone2
#hostName = socket.gethostname()
#settingsFileName = 'settings_' + hostName
#print(settingsFileName)
##import as settings
#settings = __import__(settingsFileName)


from support import round_time as round_time
from support import delay as delay

from ConfigObject import cfg # singleton global


#******************** hardware specifics********************************
#================hardware dependant imports=============================
if cfg.getItemValueFromConfig('platform_name') == "RPi2": #rpi platform
    import RPi.GPIO as GPIO
    import Adafruit_DHT
    sensor = Adafruit_DHT.DHT22
    #=================hardware dependant pins values etc====================
    #----pin assignments and related hardware defs----
    powerPin = 2    #pyhs pin 3
    led2 = 3        #phys pin 5
    sensorPin = 4   #phys pin 7
    heaterRelay = 5 #pyhs pin 29
    ventRelay = 6   #phys pin 31
    fanRelay = 7    #phys pin 26
    relay4 = 8      #pyhs pin 24
elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":    # pcduino platform
    import gpio
    import dht22 as dht22
    #=================hardware dependant pins values etc====================
    #Make sure the GPIO pins are ready:
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)
    #dht22.setup()               #init dht22 pins etc
    #----pin assignments----
    led1_pin = "gpio0"
    led2_pin = "gpio1"
    powerPin = "gpio2"
    relaypins=("gpio3","gpio4","gpio5","gpio6")
    heaterRelay = "gpio3"
    ventRelay = "gpio4"
    fanRelay = "gpio5"
    relay4 = "gpio6"




#====================hardware dependant functions=======================

class sensor(object):

    def __init__(self):
        print("create sensor object")
        self.humidity = 55.5
        self.temperature = 18.0
        #self.prevTempHumiMillis = 0   #last time sensor read
        self.proc_temp = 0       # processedsed, filter temp reading
        self.currentTime = 0
        self.prevTemp = 0
        self.prevHumi = 0
        self.readErrs = 0
        self._power_cycle()
            
    def _read_sensor(self):
        if cfg.getItemValueFromConfig('platform_name') == "RPi2":
            sensor = Adafruit_DHT.DHT22
            self.humidity, self.temperature = Adafruit_DHT.read_retry(sensor, sensorPin)
            #sleep(settings.readDelay)
            
        elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":
            if dht22.getth() == 0:
                #humidity, temperature = Adafruit_DHT.read_retry(sensor, sensorPin)
                self.temperature = round(dht22.cvar.temperature, 1)
                self.humidity = round(dht22.cvar.humidity, 1)
            else:
                self.temperature = None
                self.humidity = None
            #sleep(settings.readDelay)

        return self.humidity, self.temperature

    def read(self):
        #read till ret 0-ok. timeout if no valid data after timeout
        #global currentMillis        #current time

        print ("...try to read sensor at: %s" % (datetime.datetime.now().strftime("%H:%M:%S")))
        self.readErrs = 0    #reset err count
        self.prevTemp = self.temperature
        self.prevHumi = self.humidity
        
        sleep(cfg.getItemValueFromConfig('readDelay'))
        
        self.humidity, self.temperature = self._read_sensor()    # get temp, humi
        
        #repeat read until valid data or too many errorserror
        while (self.humidity is None or self.temperature is None) and self.readErrs < 10:
            print("..ERROR TRYING TO READ SENSOR on sensor read")
            self.readErrs += 1
            sleep(cfg.getItemValueFromConfig('readDelay')) #wait secs before re-read
            self.humidity, self.temperature = self._read_sensor()    # get temp, humi
    
        if self.readErrs == 10:  # powercyle if 10 read errors
            print("..ten read errors logged")
            self._power_cycle()
            print ("..POWER CYCLE complete during sensor read")
            print ("..DODGY TEMP READING USING")
            if cfg.getItemValueFromConfig('emailEnabled') == True:
                self.message = 'Power cycling sensor due to too many errors'
                try:
                    emailMe.sendemail('PowerCycle', self.message)
                except:
                    print("...ERROR SENDING EMAIL - POWER CYCLE - DODGY READING")
            self.temperature = self.prevTemp  #restore prev sample readings
            self.humidity = self.prevHumi
        else:#good read CRC if here
            if ( abs(self.temperature - self.prevTemp) < 10) and ( (self.humidity >= 10)
                and (self.humidity <= 100)): #if temp diff smallish, assume good sample
                #print( "..read sensor SUCCESS" )
                print ("..read sensor success at: %s" % (datetime.datetime.now().strftime("%H:%M:%S")))
                #self.prevTempHumiMillis = self.currentMillis
                self.temperature = round(self.temperature, 1)
                self.humidity = round(self.humidity, 1)
                
                #filter temp function
                self.proc_temp = self.proc_temp + ( 0.333 * (self.temperature - self.proc_temp))
                self.proc_temp = round(self.proc_temp, 3)
                print ('..temp: %2.1f, humi: %2.1f' %(self.temperature, self.humidity))
            else:
                #bad sample even though good crc
                print ('..temp: %2.1f, proc_temp: %2.1f, humi: %2.1f' %(self.temperature, self.proc_temp, self.humidity))
                print ('..DODGY TEMP READING USING - OLD VALS---------------- ')
                if cfg.getItemValueFromConfig('emailEnabled') == True:
                    self.message = 'Readings, Temp = '+ str(self.temperature) + ',  Humi = '+ str(self.humidity)
                    try:
                        emailMe.sendemail('Spike in Reading', self.message)
                    except:
                        print("ERROR SENDING EMAIL - DODGY READING")
                self.temperature = self.prevTemp  #restore prev sample readings
                self.humidity = self.prevHumi
        
        return self.humidity, self.temperature   
         
    def _power_cycle(self):
            print("entering power cycle")
            if cfg.getItemValueFromConfig('platform_name') == "RPi2":
                GPIO.setup(powerPin, GPIO.OUT)  #set pin as OP
                GPIO.output(powerPin, 0)        #set low to power off sensor
                sleep(1.0 * 3000 / 1000)
                GPIO.output(powerPin, 1)        #hi to power on sensor
                sleep(1.0 * 3000 / 1000)
            elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":
                gpio.pinMode(powerPin, gpio.OUTPUT)
                gpio.digitalWrite(powerPin, gpio.LOW)   #power off
                sleep(1.0 * 3000 / 1000)
                gpio.digitalWrite(powerPin, gpio.HIGH)  #power on
                sleep(1.0 * 3000 / 1000)
        
class platform(object):
    def __init__(self):
        print('creating platform board')
        #Make sure the GPIO pins are ready:
        if cfg.getItemValueFromConfig('platform_name') == "RPi2":
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":
            dht22.setup()               #init dht22 pins etc
        
        self._setupIO_pins()
        pass
        
    def _setupIO_pins(self):
        print('initialising io pins')
        if cfg.getItemValueFromConfig('platform_name') == "RPi2":
            GPIO.setup(heaterRelay, GPIO.OUT)   #set pin as OP
            GPIO.output(heaterRelay, 1)         #heat off
            GPIO.setup(ventRelay, GPIO.OUT)     #set pin as OP
            GPIO.output(ventRelay, 0)           #vent on
            GPIO.setup(fanRelay, GPIO.OUT)      #set pin as OP
            GPIO.output(fanRelay, 0)            #fan on
            GPIO.setup(relay4, GPIO.OUT)        #set pin as OP
            GPIO.output(relay4, 1)              #speed low
        elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":
            for portpin in relaypins:
                gpio.pinMode(portpin, gpio.OUTPUT)    #
            for portpin in relaypins:
                gpio.digitalWrite(portpin, gpio.HIGH)    #turn off all relays        
        
    def switch_relays(self, heaterState, ventState, fanState, ventSpeedState):
        #print('....fan switch state', fanState)
        if cfg.getItemValueFromConfig('platform_name') == "RPi2":
            GPIO.output(heaterRelay, heaterState)
            GPIO.output(ventRelay, ventState)
            GPIO.output(fanRelay, fanState)
            GPIO.output(relay4, ventSpeedState)
        elif cfg.getItemValueFromConfig('platform_name') == "PCDuino":
            #print 'switch relays'
            gpio.digitalWrite(heaterRelay, heaterState)
            gpio.digitalWrite(ventRelay, ventState)
            gpio.digitalWrite(fanRelay, fanState)
            gpio.digitalWrite(relay4, ventSpeedState)

#******************end of hardware specific*****************************
