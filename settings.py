#============targets/settings/tuneable params===========================

# comment out for hardware used as appropriate
platform_name = "RPi2"
#platformName = "PCDuino"
hardware = "RaspberryPi2"
#hardware = "PCDuino"

temp_d_on_SP = 22.5   #temp set point max with lon
temp_d_off_SP = 16.9 #16.9 #target = 16.9, target loff
temp_alarm = 33
readDelay = 3
min_CSV_write_interval = 1 * 60 * 1000 #interval min bet csv writes
#ventSpeedState = OFF

#----L control params----
on_hours = [ 0,1,2,3,4,5,6,7,8,9,22,23 ] #hours when l on
heat_off_hours = [ 22 ]   #hours when heater should NOT operate
tlon_hour = 21
tlon_minute = 45    # time on
tloff_hour = 9
tloff_minute = 45	# time off

OFF = 1 #state for relay OFF
ON = 0  #state for on

testDivisor = 1 #divisor to speed up sequencing to test timings

heater_on_t = 10 * 1000 / testDivisor  #min time heater is on or off for
heater_off_t = 21 * 1000 / testDivisor  #min time heater is on or off for
heater_sp_offset = -1.0

ventOnDelta = 5 * 1000 / testDivisor   #duration vent is on in millis
ventOffDelta = 59 * 1000 / testDivisor  #vent off duration in miili sec
ventPulseOnDelta = 20 * 1000 #60 secs cooling on delta

fan_on_t = 29 * 60 * 1000 / testDivisor   #vent on time
#fan_on_t = 30 * 1000 / testDivisor   #vent on time

fan_off_t = 10 * 1000 / testDivisor#vent off time

dataPath = "/home/pi/controlleroo/thdata.csv"
    
extraPath = "/home/pi/controlleroo/extradata.csv"

emailEnabled = False

tSPHi = temp_d_on_SP
tSPLo = temp_d_off_SP

#db params
db_hostname = "localhost"
db_username = "controller"
db_password = "password"
db_dbname = "sensordata_db"
