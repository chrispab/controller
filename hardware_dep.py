#!/usr/bin/env python
# control.py
# control for enviro controller
#

#******************** hardware specifics********************************
#================hardware dependant imports=============================
import RPi.GPIO as GPIO
import Adafruit_DHT
sensor = Adafruit_DHT.DHT22

#=================hardware dependant pins values etc====================
#Make sure the GPIO pins are ready:
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#----pin assignments and related hardware defs----
powerPin = 2    #pyhs pin 3
led2 = 3        #phys pin 5
sensorPin = 4   #phys pin 7
heaterRelay = 5 #pyhs pin 29
ventRelay = 6   #phys pin 31
fanRelay = 7    #phys pin 26
relay4 = 8      #pyhs pin 24

OFF = 1 #state for relay OFF
ON = 0  #state for on
#====================hardware dependant functions=======================
def powerCycleSensor():
    GPIO.setup(powerPin, GPIO.OUT)	#set pin as OP
    GPIO.output(powerPin, 0)	#set low to power off sensor
    delay(3000)
    GPIO.output(powerPin, 1)	#hi to power on sensor
    delay(3000)

def readSensor():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, sensorPin)
    return humidity, temperature
        
def setupIOPins():
    GPIO.setup(heaterRelay, GPIO.OUT)	#set pin as OP
    GPIO.output(heaterRelay, 1)	#heat off
    GPIO.setup(ventRelay, GPIO.OUT)	#set pin as OP
    GPIO.output(ventRelay, 0)	#vent on
    GPIO.setup(fanRelay, GPIO.OUT)	#set pin as OP
    GPIO.output(fanRelay, 0)	#fan on
    GPIO.setup(relay4, GPIO.OUT)	#set pin as OP
    GPIO.output(relay4, 1)	#speed low

def switchRelays():
    GPIO.output(heaterRelay, heaterState)
    GPIO.output(ventRelay, ventState)
    GPIO.output(fanRelay, fanState)
    GPIO.output(relay4, ventSpeedState)

#******************end of hardware specific*****************************


