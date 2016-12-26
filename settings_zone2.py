#============targets/settings/tuneable params===========================

# comment out for hardware used as appropriate
#platform_name = "RPi2"
platform_name = "PCDuino"
#hardware = "RaspberryPi2"
hardware = "PCDuino"

#temp_d_on_SP = 24.0   #temp set point max with lon
#temp_d_off_SP = 21.0 # was 21.016.9 #target = 16.9, target loff
temp_alarm = 30
readDelay = 3
min_CSV_write_interval = 1 * 60 * 1000 #interval min bet csv writes
#ventSpeedState = OFF

#----L control params----
#on_hours = [ 0,1,2,3,4,5,6,7,8,9,10,11,12,13,20,21,22,23]
#heat_off_hours = [ 20 ]   #hours when heater should NOT operate
#tlon_hour = 20
#tlon_minute = 00    # time on
#tloff_hour = 14
#tloff_minute = 00	# time off

#OFF = 1 #state for relay OFF
#ON = 0  #state for on

testDivisor = 1 #divisor to speed up sequencing to test timings

#heater_on_t = 1 * 1000 / testDivisor  #min time heater is on or off for
#heater_off_t = 30 * 1000 / testDivisor  #min time heater is on or off for
##heater_sp_offset = -1.0


ventOnDelta = 3 * 1000 / testDivisor   #duration vent is on in millis
ventOffDelta = 179 * 1000 / testDivisor  #vent off duration in miili sec
ventPulseOnDelta = 10 * 1000 # secs cooling on delta
vent_sp_offset = 0.0
vent_lon_sp_offset= 0.0 #offset
vent_loff_sp_offset= 1.0 #

fan_on_t = 17 * 1000 / testDivisor   #vent on time
fan_off_t = 37 * 1000 / testDivisor#vent off time

dataPath = "/home/ubuntu/controlleroo/thdata.csv"

extraPath = "/home/ubuntu/controlleroo/extradata.csv"

emailEnabled = False

#tSPHi = temp_d_on_SP
#tSPLo = temp_d_off_SP

#db params
db_hostname = "127.0.0.1"
db_username = "root"
db_password = "ubuntu"
db_dbname = "sensordata_db"

hi_temp_warning = 26.0
lo_temp_warning = 15.0

t_lon = "22:15:00"    # time light on hh:mm:ss
t_loff = "09:45:00"   # time off

central_db_hostname = "192.168.0.201"
central_db_username = "myiot"
central_db_password = "myiot"
central_db_dbname = "zone2_sensordata_db"
