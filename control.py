#!/usr/bin/env python
# control.py
# control for enviro controller
#

import settings
import hardware as hw

#===================general imports=====================================
import sys
import time
import datetime
from datetime import timedelta
import csv
import sendemail as emailMe


#============targets/settings/tuneable params from settings file========
tempLOnSP = settings.tempLOnSP   #temp set point max with lon
tempLOffSP = settings.tempLOffSP #target = 16.9, target loff
temp_max = settings.temp_max #26
readDelay = settings.readDelay
#tempHumiReadDelta   = settings.tempHumiReadDelta # min time to elapse in millis between sensor reads - 2 secs for dht22
minCSVWriteInterval = settings.minCSVWriteInterval  #3 * 60 * 1000 #interval min bet csv writes
#ventSpeedState = OFF

#----L control params----
onHours = settings.onHours  #[ 0,1,2,3,4,5,6,7,8,9,22,23 ] #hours when l on
heatOffHours = settings.heatOffHours    #[ 22 ]   #hours when heater should NOT operate

OFF = settings.OFF #state for relay OFF
ON = settings.ON  #state for on

testDivisor = settings.testDivisor  #divisor to speed up sequencing to test timings

heaterOnDelta = settings.heaterOnDelta  #4 * 1000 / testDivisor  #min time heater is on or off for
heaterOffDelta = settings.heaterOffDelta #15 * 1000 / testDivisor  #min time heater is on or off for

ventOnDelta = settings.ventOnDelta      #60 * 1000 / testDivisor   #duration vent is on in millis
ventOffDelta = settings.ventOffDelta    #30 * 1000 / testDivisor  #vent off duration in miili sec
ventPulseOnDelta = settings.ventPulseOnDelta    #20 * 1000 #60 secs cooling on delta

fanOnDelta = settings.fanOnDelta    #20000 * 1000 / testDivisor   #vent on time
fanOffDelta = settings.fanOffDelta  #5 * 1000 / testDivisor#vent off time

path = settings.dataPath    
extraPath = settings.extraPath




#===========initial settings============================================
temperature = 20    #global temp var
humidity = 50   #global humidity var
procTemp = 0

#related global vars
heaterState = OFF
ventState = ON
fanState = ON
ventSpeedState = OFF
lState = OFF

#=================initialised global vars etc===========================

currentMillis = 0
previousTemperature = 24
previousProcTemp = 24
previousHumidity = 40
previousHeaterState = ON
previousVentState = OFF
previousFanState = OFF
previousVentSpeedState = OFF
prevTempHumiMillis = 0  #previous time  sensors routine called and data read

#heater control params
#heaterState = OFF

prevHeaterMillis = 0   #last time heater switched on or off

# Vent control parameters
#ventState = ON
#ventOnDelta = 15 * 1000 / testDivisor   #duration vent is on in millis
#ventOffDelta = 30 * 1000 / testDivisor  #vent off duration in miili sec
prevVentMillis = 0
ventPulseActive = False
ventOverride = OFF

#Fan control parameters
#fanState = ON
prevFanMillis = 0   #last time vent state updated

previousCSVWriteMillis = 0 #last time CSV file row added

startMillis = 0    #time at start of program execution
currentTime = 0
start_time = time.time()
up_time = time.time()


 

#============================common code start==========================
def setup():
    global temperature
    global humidity
    global prevTempHumiMillis
    global procTemp
 
    hw.powerCycleSensor()
    
    readErrs = 0    #reset err count
    humidity, temperature = hw.readSensor()
    #repeat read until valid data or too many errorserror
    while (humidity is None or temperature is None) and readErrs < 10:   
        print('Setup - ERROR TRYING TO READ SENSOR')
        readErrs += 1
        humidity, temperature = hw.readSensor()    # get temp, humi

    if readErrs == 10:  # powercyle if 10 read errors
        hw.powerCycleSensor()
        print "Setup - 10 errors reading sensor"
        print "Setup - POWER CYCLE sensor"
    else:
        print "Setup - READ SUCCESS-"
    
    prevTempHumiMillis = currentMillis

    temperature = round(temperature, 1)
    procTemp = temperature
    humidity = round(humidity, 1)

    hw.setupIOPins()

def delay(ms):
    time.sleep(1.0*ms/1000)
    
def readTempHumi():
    # loop and read till ret 0 - ok. timeout if no valid adata got after timeout
    global currentMillis        #current time
    global prevTempHumiMillis   #last time sensor read
#    global tempHumiReadDelta    #time between reads
    global temperature
    global humidity
    global procTemp # processedsed / filter temp reading
    
    #only read if delta delay passed secs past since last read
    #if (currentMillis - prevTempHumiMillis >= tempHumiReadDelta):
        #sys.stdout.write('-readth READ SENSOR Due-')
    print "    try to read sensor"
        
    readErrs = 0    #reset err count
    prevTemp = temperature
    prevHumi = humidity
    delay(readDelay)
    humidity, temperature = hw.readSensor()    # get temp, huni
    while (humidity is None or temperature is None) and readErrs < 10:   #repeat read until valid data or too many errorserror
        sys.stdout.write('    ERROR TRYING TO READ SENSOR on sensor read-')
        readErrs += 1
        delay(readDelay) #wait secs before re-read
        humidity, temperature = hw.readSensor()    # get temp, humi

    if readErrs == 10:  # powercyle if 10 read errors
        powerCycleSensor()
        print "    POWER CYCLE during sensor read++++"
    else:#good read if here
        if ( abs(temperature - prevTemp) < 10) and ( (humidity >= 0) and (humidity <= 100)): #if temp diff smallish, assume good sample
            sys.stdout.write( "    read sensor SUCCESS ## -" )
            
            prevTempHumiMillis = currentMillis
            temperature = round(temperature, 1)
            humidity = round(humidity, 1)
            
            #filter temp function
            procTemp = procTemp + ( 0.333 * (temperature - procTemp))
            procTemp = round(procTemp, 3)
            print 'temp: %2.1f, procTemp: %2.1f, humi: %2.1f' %(temperature, procTemp, humidity)
        else:
            #bad sample even though good crc
            print 'DODGY TEMP READING USING - OLD VALS---------------- '
            if settings.emailEnabled == True:
                message = 'Readings, Temp = '+ str(temperature) + ',  Humi = '+ str(humidity)
                emailMe.sendemail('Spike in Reading', message)
            temperature = prevTemp  #restore prev sample readings
            humidity = prevHumi
            
    
 
    
def heatControl(currTemp, tempSP):
    print 'Heat ctl'
    #add hysteresis with time delay between poss chnages to heater
    global heaterState
    global heaterOffDelta #min time heater is on or off for
    global heaterOnDelta #min time heater is on or off for
    global currentMillis
    global prevHeaterMillis   #last time heater switched on or off

    
    if currTemp >= tempSP:#if over temp immediately turn off
        heaterState = OFF
        print "    temp over sp - HEATER OFF"
        prevHeaterMillis = currentMillis
    elif (heaterState == ON):  #t below tsp if time is up, so change the state to OFF
        if (currentMillis - prevHeaterMillis >= heaterOnDelta):
            heaterState = OFF
            print "    in cycle - HEATER OFF"
            prevHeaterMillis = currentMillis
        else:
            print('    Heater on - during low temp heat pulse')
    elif (currentMillis - prevHeaterMillis >= heaterOffDelta):#heater is off, turn on after delta
        heaterState = ON
        print "    in cycle - HEATER ON"
        prevHeaterMillis = currentMillis
    else:
        print "    in cycle - during heat OFF period"
        
    
    print(' ')
    return

        
        

def ventControl(currTemp, targetTemp, ventSpeed):
    print 'Vent ctl'
    #vent routine and temp ovveride
    global ventState
    global currentMillis        #current time
    global prevVentMillis   #last time vent state updated
    global ventOnDelta    #vent on time
    global ventOffDelta #vent off time
    global ventPulseActive
    global ventPulseDelta
    global ventPulseOnDelta
    global ventOverride
    global ventSpeedState

    ventSpeedState = ventSpeed
    if currTemp > targetTemp:
        ventOverride = ON
        ventState = ON
        prevVentMillis = currentMillis  #retrigeer time period
        print "    VENT ON - HI TEMP OVERRIDE - (Re)Triggering cooling pulse"
    elif ( (ventOverride == ON) and ((currentMillis - prevVentMillis) >= ventPulseOnDelta) ):#temp below target, change state to OFF after pulse delay
            ventState = OFF
            ventOverride = OFF
            prevVentMillis = currentMillis
            print "    VENT OFF - temp ok, OVERRIDE - OFF"
    elif ventOverride == ON:
        print('    Vent on - override in progress')
        
    
    #periodic vent control - only execute if vent ovveride not active
    if ventOverride == OFF: #process periodic vent activity
        if (ventState == OFF): ##if the vent is off, we must wait for the interval to expire before turning it on 
            ## iftime is up, so change the state to ON
            if (currentMillis - prevVentMillis >= ventOffDelta):
                ventState = ON
                print "    VENT ON cycle period start"
                prevVentMillis = currentMillis
            else:
                print('    Vent off - during cycle OFF period')
        else:
            #vent is on, we must wait for the duration to expire before turning it off
            if (currentMillis - prevVentMillis) >= ventOnDelta:#time up, change state to OFF
                ventState = OFF
                print "    VENT OFF cycle period start"
                prevVentMillis = currentMillis
            else:
                print('    Vent on - during cycle ON period')
    print(' ')
    return


def doFanControl():
    #print 'fan ctl'
    #fan control and temp overide
    #print "FAN CONTROL: current time in secs ", time.time()
    #setup access to global vars
    global fanState
    global currentMillis        #current time
    global prevFanMillis   #last time vent state updated
    global fanOnDelta    #vent on time
    global fanOffDelta #vent off time
    
    #if fan off, we must wait for the interval to expire before turning it on
    if (fanState == OFF):  
        # iftime is up, so change the state to ON
        if (currentMillis - prevFanMillis >= fanOffDelta):
            fanState = ON
            print "FAN ON"
            prevFanMillis += fanOffDelta
    #else if fanState is ON
    else:
        #time is up, so change the state to LOW
        if (currentMillis - prevFanMillis) >= fanOnDelta:
            fanState = OFF
            print "FAN OFF"
            prevFanMillis += fanOnDelta

   
    
def writeToCSV():
    #print 'write to csv'
    global currentTime
    global temperature
    global humidity
    global heaterState
    global ventState
    global fanState
    global ventSpeedState
    global previousCSVWriteMillis
    global currentMillis        #current time
    global dataLogInterval    #vent on time
    global minCSVWriteInterval  #csv log write min interval
     
    #path = "/home/pi/projects/controller1/thdata.csv"
    data =['time','temp','humi','heaterstate','ventstate','fanstate','procTemp']
    data[0] = roundTime(currentTime, 1) #round timestamp to nearest second
    data[1] = temperature
    data[2] = humidity
    if heaterState== OFF:
        data[3] = 0;    #off line on graph
    else:
        data[3] = 1    #on line on graph
    
    if ventState == OFF:
        data[4] = 0    #off line on graph
    if ventState == ON:
        if ventSpeedState == OFF:#vent on andspeed ==low
            data[4] = 1    #on line on graph
        if ventSpeedState == ON:#vent on and hi speed
            data[4] = 2    #on line on graph
    
    if fanState== OFF:
        data[5] = 0;    #off line on graph
    else:
        data[5] = 1    #on line on graph
        
    data[6] = round(procTemp, 1)  #add processed temp value
    
    print data
    with open(path, "ab") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        #for line in data:
        writer.writerow(data)
        previousCSVWriteMillis = currentMillis  #note time row written

def writeExtraDataToCSV():
    #extraPath = "/home/pi/projects/controller1/extradata.csv"

    extraData = ['time','temp', 'procTemp','round-procTemp']
    extraData[0] = roundTime(currentTime, 1) #round timestamp to nearest second
    extraData[1] = temperature
    extraData[2] = procTemp
    extraData[3] = round(procTemp, 1)
    with open(extraPath, "ab") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        #for line in data:
        writer.writerow(extraData)
        #previousCSVWriteMillis = currentMillis  #note time row written

    
def updateCSVIfChanges():
    global previousTemperature
    global previousHumidity
    global previousHeaterState
    global previousVentState
    global previousFanState
    global previousVentSpeedState
    global previousProcTemp
    global ventState
    global fanState
    global heaterState
    global ventSpeedState
    global previousHeater
    global previousCSVWriteMillis
    
    writeExtraDataToCSV()
    
    # update csv if any chanmge
    #check for changes in vent values
    if (ventState <> previousVentState): # any change in vent
        if previousVentState == OFF:  #must be going OFF to ON
            #write a low record immediately before hi record
            print "----- new prevvent low row appended to CSV -----"
            ventState = OFF
            writeToCSV()
            ventState = ON  #restore to actual current val
        if previousVentState == ON:   # must be going ON TO OFF
            #write a on record immediately before hi record
            print "----- new hi row appended to CSV -----"
            ventState = ON
            writeToCSV()
            ventState = OFF  #restore to actual current val
            
    if (ventSpeedState <> previousVentSpeedState): # any change in vent speed
        if previousVentSpeedState == OFF:  #was lo speed
            #write a low record immediately before hi record
            print "----- new low row appended to CSV -----"
            ventSpeedState = OFF
            writeToCSV()
            ventSpeedState = ON  #restore to actual current val
            writeToCSV()
        else:   #was hi speed going low
            #write a on record immediately before hi record
            print "----- new hi row appended to CSV -----"
            ventSpeedState = ON
            writeToCSV()
            ventSpeedState = OFF  #restore to actual current val
            writeToCSV()
 
     
    if (fanState <> previousFanState): # any change in vent
        if previousFanState == OFF:  #must be going OFF to ON
            #write a low record immediately before hi record
            print "----- new low row appended to CSV -----"
            fanState = OFF
            writeToCSV()
            fanState = ON  #restore to actual current val
        else:   # must be going ON TO OFF
            #write a on record immediately before hi record
            print "----- new hi row appended to CSV -----"
            fanState = ON
            writeToCSV()
            fanState = OFF  #restore to actual current val
            
           
    if (heaterState <> previousHeaterState): # any change in vent
        if previousHeaterState == OFF:  #must be going OFF to ON
            #write a low record immediately before hi record
            print "----- new low row appended to CSV -----"
            heaterState = OFF
            writeToCSV()
            heaterState = ON  #restore to actual current val
        else:   # must be going ON TO OFF
            #write a on record immediately before hi record
            print "----- new hi row appended to CSV -----"
            heaterState = ON
            writeToCSV()
            heaterState = OFF  #restore to actual current val
            
    if ( (currentMillis > (previousCSVWriteMillis + minCSVWriteInterval))
            or (heaterState <> previousHeaterState) 
            or (ventState <> previousVentState) 
            or (ventSpeedState <> previousVentSpeedState) 
            or (round(procTemp,1) <> round(previousProcTemp,1)) 
            or (fanState <> previousFanState)  or (temperature <> previousTemperature) ): # any change
            #: # 

        print "----- new data row appended to CSV cos of some change -----"
        writeToCSV()
        previousTemperature = temperature
        previousHumidity = humidity
        previousHeaterState = heaterState
        previousVentState = ventState
        previousFanState = fanState
        previousVentSpeedState = ventSpeedState
        previousProcTemp = procTemp
        previousCSVWriteMillis = currentMillis
 

def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time laps in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   # // is a floor division, not a comment on following line:
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)
   
def updateCurrentMillis():
    global currentTime
    global currentMillis
    global startMillis 
       
    currentTime = datetime.datetime.now()   #get current time
    delta = currentTime - startMillis   #calc elapsed delta since program began
    currentMillis = int(delta.total_seconds() * 1000)
        
def  getLState():
    """ Function doc """
    global lState
    global tLOn
    global tLOff

    #if time between 7am and 7pm L on else L off
    currentHour = datetime.datetime.now().hour
    if currentHour in onHours:
        lState = ON
    else:
        lState = OFF
        
      
def main():
    global startMillis
    global temperature
    global procTemp
    global lState
    global ventState
    global fanState
    global heaterState
    global ventSpeedState

    
    
    print("---Powering up the device---")
    
    start_time = time.time()

    startMillis = datetime.datetime.now()   # get time at start of program execution
    setup()
 
    while(1):
        print 'main'
        #print(roundTime(currentTime, 1))
        updateCurrentMillis() 
        getLState()
        readTempHumi()
        doFanControl()        
        
        if lState == ON:
            print('.LON')
            #heat
            currentHour = datetime.datetime.now().hour
            if currentHour in heatOffHours:  #l on and not 10:xx pm
                print('xx skipping lon heatctl')
            else:
                print('xx do lon heatctl')
                heatControl(temperature, tempLOnSP)
            #vent    
            if temperature > tempLOnSP + 0.2:  #if over temp by ? deg
                ventHiSpeed = ON    #setFanSpeed(fanSpeedHigh)
            else:
                ventHiSpeed = OFF   #lo speed
            ventControl(temperature, tempLOnSP, ventHiSpeed)
                
        if lState == OFF:
            print('.LOFF')
            heatControl(temperature, tempLOffSP)
            ventHiSpeed = OFF   #ensure low speed if light off
            ventControl(temperature, tempLOffSP, ventHiSpeed)

        hw.switchRelays(heaterState, ventState, fanState, ventSpeedState)  #switch relays according to State vars
        updateCSVIfChanges()#write to csv if any state changes
        
        end_time = time.time()
        uptime = end_time - start_time
        human_uptime = str(timedelta(seconds=int(uptime)))


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   main()
   
