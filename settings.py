#============targets/settings/tuneable params===========================

# comment out for hardware used as appropriate
platform_name = "RPi2"
#platformName = "PCDuino"
hardware = "RaspberryPi2"
#hardware = "PCDuino"

temp_d_on_SP = 22.5   #temp set point max with lon
temp_d_off_SP = 15.3 #16.9 #target = 16.9, target loff

readDelay = 3
min_CSV_write_interval = 1 * 60 * 1000 #interval min bet csv writes

#----L control params----
on_hours = [ 6,7,8,9,10,11,12,13,14,15,16,17 ] #hours when l on
heat_off_hours = [ ]   #hours when heater should NOT operate
tlon_hour = 06
tlon_minute = 0    # time on
tloff_hour = 18
tloff_minute = 0   # time off

OFF = 1 #state for relay OFF
ON = 0  #state for on

testDivisor = 1 #divisor to speed up sequencing to test timings

heater_on_t = 18 * 1000 / testDivisor  #min time heater is on or off for
heater_off_t = 113 * 1000 / testDivisor  #min time heater is on or off for
heater_sp_offset = 0

ventOnDelta = 3 * 1000 / testDivisor   #duration vent is on in millis
ventOffDelta = 197 * 1000 / testDivisor  #vent off duration in miili sec
ventPulseOnDelta = 10 * 1000 #60 secs cooling on delta
vent_sp_offset = 0.0

fan_on_t = 29 * 60 * 1000 / testDivisor   #vent on time
#fan_on_t = 30 * 1000 / testDivisor   #vent on time

fan_off_t = 10 * 1000 / testDivisor#vent off time

dataPath = "/home/pi/controlleroo/data/thdata.csv"
    
extraPath = "/home/pi/controlleroo/data/extradata.csv"

emailEnabled = False

tSPHi = temp_d_on_SP
tSPLo = temp_d_off_SP

#db params
db_hostname = "127.0.0.1"
db_username = "controller"
db_password = "password"
db_dbname = "sensordata_db"

hi_temp_warning = 26.0
lo_temp_warning = 14.0

t_lon = "22:15:00"    # time light on hh:mm:ss
t_loff = "09:45:00"   # time off

central_db_hostname = "192.168.0.201"
central_db_username = "myiot"
central_db_password = "myiot"
central_db_dbname = "zone1_sensordata_db"
