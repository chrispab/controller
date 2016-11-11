#!/usr/bin/env python
# iotestpytest.py
# Python test code for dht22 sensor c driver - wrapped for python use
#

import gpio
import time
import iotest as dht22
from datetime import timedelta



led1_pin = "gpio0"
led2_pin = "gpio1"
relaypins=("gpio3","gpio4","gpio5","gpio6")
heaterPin = "gpio3"
setPoint = 22   #temp switch poit
start_time =time.time()
up_time=time.time()



def delay(ms):
    time.sleep(1.0*ms/1000)

def setup():
    dht22.setup()                               #init dht22 pins etc
    for portpin in relaypins:
        gpio.pinMode(portpin, gpio.OUTPUT)    #
    for portpin in relaypins:
        gpio.digitalWrite(portpin, gpio.HIGH)    #turn off all relays
    for portpin in relaypins:
        gpio.digitalWrite(portpin, gpio.LOW)    #turn on relays in turn
        delay(200)                              #pause a bit
    for portpin in relaypins:
        delay(500)                              #pause
        gpio.digitalWrite(portpin, gpio.HIGH)   #turn off
    start_time = time.time()

def loop():
    while(1):
        dht22.loop()    #perform loop in c driver
        gpio.digitalWrite(led1_pin, gpio.HIGH)
        delay(50)
        gpio.digitalWrite(led1_pin, gpio.LOW)
        
        #switch ops if reqd
        if dht22.cvar.temperature < setPoint:
            gpio.digitalWrite(heaterPin, gpio.LOW)	#turn on heater
        else:
            gpio.digitalWrite(heaterPin, gpio.HIGH)	#turn off heater
        #delay(100)

        end_time = time.time()
        uptime = end_time - start_time
        human_uptime = str(timedelta(seconds=int(uptime)))
        #print human_uptime
        
        print "degrees:%.1f , humidity:%.1f, uptime:%s " % (dht22.cvar.temperature, dht22.cvar.humidity, human_uptime)
        print
        #print a.cvar.temperature
        #print a.cvar.humidity
        
        

        #str(timedelta(seconds=elapsed))

def main():
    setup()
    loop()

main()

