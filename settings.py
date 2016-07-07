#============targets/settings/tuneable params===========================
tempLOnSP = 22.5   #temp set point max with lon
tempLOffSP = 16.9 #16.9 #target = 16.9, target loff
temp_max = 26
readDelay = 3000
minCSVWriteInterval = 3 * 60 * 1000 #interval min bet csv writes
#ventSpeedState = OFF

#----L control params----
onHours = [ 0,1,2,3,4,5,6,7,8,9,22,23 ] #hours when l on
heatOffHours = [ 22 ]   #hours when heater should NOT operate

OFF = 1 #state for relay OFF
ON = 0  #state for on

testDivisor = 1 #divisor to speed up sequencing to test timings

heaterOnDelta = 3 * 1000 / testDivisor  #min time heater is on or off for
heaterOffDelta = 15 * 1000 / testDivisor  #min time heater is on or off for

ventOnDelta = 60 * 1000 / testDivisor   #duration vent is on in millis
ventOffDelta = 30 * 1000 / testDivisor  #vent off duration in miili sec
ventPulseOnDelta = 20 * 1000 #60 secs cooling on delta

fanOnDelta = 20000 * 1000 / testDivisor   #vent on time
fanOffDelta = 5 * 1000 / testDivisor#vent off time

dataPath = "/home/pi/projects/controller1/thdata.csv"
    
extraPath = "/home/pi/projects/controller1/extradata.csv"

emailEnabled = True

platformName = 'RPi2Sh'

tSPHi = tempLOnSP
tSPLo = tempLOffSP
