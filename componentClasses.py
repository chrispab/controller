from RF24 import *
import sdnotify
import subprocess
from Logger import Logger
import socket  # to get hostname
import yaml
from datetime import timedelta
import csv
import os
import sys    # for stdout print
import psutil
import time
import RPi.GPIO as GPIO
import datetime as dt
import datetime
import logging
#from Logger import Logger
from ConfigObject import cfg  # singleton global
OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on


logger = logging.getLogger(__name__)


# for nrf radio link
irq_gpio_pin = None


def millis(): return int(round(time.time() * 1000))


class RadioLink(object):

    def __init__(self):
        logger.info("Creating radio Link")
        self.lastHeartBeatSentMillis = 0
        self.heartBeatInterval = cfg.getItemValueFromConfig(
            'heartBeatInterval')
        self.radio = RF24(17, 0)  # setup rf 24l01 radio on pins

        self.prev_radio_millis = 0  # last time vent state updated
        self.writingPipeAddress = cfg.getItemValueFromConfig(
            'writingPipeAddress').encode()
        self.readingPipeAddress = cfg.getItemValueFromConfig(
            'readingPipeAddress').encode()
        self.ackMessage = cfg.getItemValueFromConfig('ackMessage')

        #self.pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
        self.min_payload_size = 4
        self.max_payload_size = 32
        self.payload_size_increments_by = 1
        self.next_payload_size = self.min_payload_size
        self.inp_role = 'none'
        self.send_payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012'

        print(' ************ setting up radio Link *********** ')
        self.radio.begin()
        self.radio.setPALevel(RF24_PA_MAX)
        self.radio.setDataRate(RF24_250KBPS)
        self.radio.enableDynamicPayloads()
        # self.radio.setRetries(5,15)
        self.radio.setChannel(124)
        self.radio.printDetails()

        # setup pipes
        self.radio.openWritingPipe(self.writingPipeAddress)

        # self.radio.openWritingPipe(self.pipes[1])
        self.radio.openReadingPipe(1, self.readingPipeAddress)

        # self.radio.openReadingPipe(1,self.pipes[0])
        self.radio.startListening()

        return

    # hold wireless arduino watchdog

    def holdOffWatchdog(self):
        self.sendHeartBeatMessage()
        # self.respondToPing()
        return

    # respond to ping from arduino
    def respondToPing(self):
        self.try_read_data()

        return

    def sendHeartBeatMessage(self):
        self.radio.stopListening()

        ticks = millis()
        if (((ticks) - self.lastHeartBeatSentMillis) >= self.heartBeatInterval):  # ready to send
            logger.debug(
                '..sending RF24 radio heartbeat message : %s' % self.ackMessage)
            # logger.warning(self.ackMessage)
            self.lastHeartBeatSentMillis = millis()

            self.radio.write(self.ackMessage.encode())

        return

    ##########################################
    def try_read_data(self, channel=0):
        logger.debug('checking for nRF ping from arduino')

        self.radio.startListening()

        if self.radio.available():
            while self.radio.available():
                self.payloadSize = self.radio.getDynamicPayloadSize()
                self.receive_payload = self.radio.read(self.payloadSize)
                print('Got payload size={} value="{}"'.format(
                    self.payloadSize, self.receive_payload.decode('utf-8')))
                # First, stop listening so we can talk
                self.radio.stopListening()

                # Send the final one back.
                #send_payload_2 = b'from pi -Ping Received'
                # self.radio.write(send_payload_2)
                self.radio.write(self.ackMessage)

                #logger.warning('Sent - IM ALIVE - response to arduino ping')
                logger.warning(self.ackMessage)

                # Now, resume listening so we catch the next packets.
        self.radio.startListening()
        # self.radio.flush_rx()
        return


class Relay(object):

    def __init__(self):
        logger.info("creating relay - dummy so far")


class Vent(object):

    def __init__(self):
        logger.debug("creating vent")
        self.ventState = OFF
        self.speed_state = OFF
        self.speed_state_count = 0
        self.speed_state_trigger = 5  # trigger hi state on n counts hi
        self.prev_vent_millis = 0  # last time vent state updated
        self.vent_on_delta = cfg.getItemValueFromConfig(
            'ventOnDelta')  # vent on time
        self.vent_off_delta = cfg.getItemValueFromConfig(
            'ventOffDelta')  # vent off time
        self.vent_pulse_active = OFF  # settings.ventPulseActive
        self.vent_pulse_delta = 0  # ventPulseDelta
        self.vent_pulse_on_delta = cfg.getItemValueFromConfig(
            'ventPulseOnDelta')
        self.vent_loff_sp_offset = cfg.getItemValueFromConfig(
            'vent_loff_sp_offset')
        self.vent_lon_sp_offset = cfg.getItemValueFromConfig(
            'vent_lon_sp_offset')
        self.ventDisableTemp = cfg.getItemValueFromConfig('ventDisableTemp')
        self.ventDisableHumi = cfg.getItemValueFromConfig('ventDisableHumi')
        self.platformName = cfg.getItemValueFromConfig('hardware')
        self.vent_override = OFF  # settings.ventOverride
        self.ventEnableHighSpeed = cfg.getItemValueFromConfig(
            'ventEnableHighSpeed')

        self.ventDark_status = 'inactive'
        # self.ventDark_onDelta = cfg.getItemValueFromConfig(
        #     'ventDark_onDelta')  # vent on time
        # self.ventDark_offDelta = cfg.getItemValueFromConfig(
        #     'ventDark_offDelta')  # vent on time
        self.ventDarkOnDelta = cfg.getItemValueFromConfig(
            'ventDarkOnDelta')  # vent on time
        self.ventDarkOffDelta = cfg.getItemValueFromConfig(
            'ventDarkOffDelta')  # vent on time
        self.ventDark_ON_startTime = 0
        self.ventDark_OFF_startTime = 0

    def control(self, currentTemp, currentHumi, target_temp, lightState, current_millis):
        logger.debug('==Vent ctl==')
        # refresh in case changed while running
        self.vent_on_delta = cfg.getItemValueFromConfig(
            'ventOnDelta')  # vent on time
        self.vent_off_delta = cfg.getItemValueFromConfig(
            'ventOffDelta')  # vent off time
        self.ventDarkOnDelta = cfg.getItemValueFromConfig(
            'ventDarkOnDelta')  # vent on time
        self.ventDarkOffDelta = cfg.getItemValueFromConfig(
            'ventDarkOffDelta')  # vent on time

        # loff vent/cooling
        # if light off - do a minimal vent routine
        if (lightState == OFF):
            # self.ventState = OFF
            # self.speed_state = OFF
            if (self.ventDark_status == 'inactive'):
                logger.debug('--- lets start the vent dark ON period')
                # lets start the vent dark ON period
                self.ventDark_status = ON
                self.ventState = ON
                self.speed_state = OFF
                # set time it was switched ON
                self.ventDark_ON_startTime = current_millis
                return

            # if at end of ON period
            if ((self.ventDark_status == ON) and (current_millis > (self.ventDark_ON_startTime + self.ventDarkOnDelta))):
                logger.debug('--- now at end of ON cylce')
                # now at end of ON cylce
                # enable off period
                self.ventDark_status = OFF
                self.ventState = OFF
                self.speed_state = OFF
                # set time it was switched ON
                self.ventDark_OFF_startTime = current_millis
                return

            # if at end of OFF period
            if ((self.ventDark_status == OFF) and (current_millis > (self.ventDark_OFF_startTime + self.ventDarkOffDelta))):
                logger.debug('--- now at end of OFF cylce')
                # now at end of OFF cylce
                # so - enable ON period
                self.ventDark_status = ON
                self.ventState = ON
                self.speed_state = OFF
                # set time it was switched ON
                self.ventDark_ON_startTime = current_millis
                return
            # return
        else:  # mark light off period as inactive
            logger.debug('--- turn off all vent - in dark off settings')
            self.ventDark_status = 'inactive'

        #! vent off if loff - temp/humi test mod TODO fix/finalise
        # and (currentHumi < self.ventDisableHumi):
        # if (lightState == OFF) and (currentTemp < self.ventDisableTemp):
        #     self.ventState = OFF
        #     self.speed_state = OFF
        #     return

        # force hispeed if over temp and lon
        #!add some hysteresys here
        # only for upperlon control
        if (lightState == ON):
            lowerHys = target_temp - 0.1
            upperHys = target_temp + 0.2
            # maybe use a dead band?

            if (self.speed_state == ON):
                if (currentTemp > lowerHys):
                    self.speed_state = ON  # high speed - leave on
                else:  # (currentTemp < lowerHys):
                    self.speed_state = OFF  # lo speed
            else:  # speedstate is OFF
                if (currentTemp < upperHys):
                    self.speed_state = OFF  # high speed - leave on
                else:  # (currentTemp > upperHys):
                    self.speed_state = ON  # lo speed

        # if (self.speed_state==ON) and (currentTemp < upperHys):#
        #     self.speed_state=ON# high speed - leave on

        # if (currentTemp > target_temp +0.1) and (lightState==ON):
        #     self.speed_state=ON# high speed
        # if (currentTemp < ) and (lightState==ON): #attempt at hysteresis
        #     self.speed_state=OFF# lo speed

        # if ((lightState == OFF) and (currentTemp > target_temp + self.vent_loff_sp_offset)):
        #     self.vent_override = ON
        #     self.ventState = ON
        #     #self.speed_state = ON
        #     self.prev_vent_millis = current_millis  # retrigeer time period
        #     logger.info(
        #         "..VENT ON Loff - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")

        if ((lightState == ON) and (currentTemp > target_temp + self.vent_lon_sp_offset)):
            self.vent_override = ON
            self.ventState = ON
            self.prev_vent_millis = current_millis  # retrigeer time period
            logger.debug(
                "..VENT ON - HI TEMP OVERRIDE - (Re)Triggering cooling pulse")
        # temp below target, change state to OFF after pulse delay
        elif (self.vent_override == ON) and ((current_millis - self.prev_vent_millis) >= self.vent_pulse_on_delta):
            self.ventState = OFF
            self.vent_override = OFF
            self.prev_vent_millis = current_millis
            logger.debug("..VENT OFF - temp ok, OVERRIDE - OFF")
        elif self.vent_override == ON:
            logger.debug('..Vent on - override in progress')

        # periodic vent control - only execute if vent ovveride not active
        if self.vent_override == OFF:  # process periodic vent activity
            if self.ventState == OFF:  # if the vent is off, we must wait for the interval to expire before turning it on
                # iftime is up, so change the state to ON
                if current_millis - self.prev_vent_millis >= self.vent_off_delta:
                    self.ventState = ON
                    logger.debug("VVVVVVVVVVVV..VENT ON cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    logger.debug('..Vent off - during cycle OFF period')
            else:
                # vent is on, we must wait for the 'on' duration to expire before
                # turning it off
                # time up, change state to OFF
                if (current_millis - self.prev_vent_millis) >= self.vent_on_delta:
                    self.ventState = OFF
                    logger.debug("VVVVVVVVVVVVV..VENT OFF cycle period start")
                    self.prev_vent_millis = current_millis
                else:
                    logger.debug('..Vent on - during cycle ON period')
        return


class Fan(object):

    def __init__(self):
        logger.debug("Creating fan")
        self.fanState = OFF
        self.prev_fan_millis = 0  # last time vent state updated
        self.fan_on_delta = cfg.getItemValueFromConfig(
            'fan_on_t')  # vent on time
        self.fan_off_delta = cfg.getItemValueFromConfig(
            'fan_off_t')  # vent off time

    def control(self, current_millis):
        logger.debug('==fan ctl==')
        # if fan off, we must wait for the interval to expire before turning it on
        logger.debug('==current millis: %s' % (current_millis))
        logger.debug('==current fan state: %s' % (self.fanState))
        if self.fanState == OFF:
            # if time is up, so change the state to ON
            if current_millis - self.prev_fan_millis >= self.fan_off_delta:
                self.fanState = ON
                logger.debug("..FAN ON")
                self.prev_fan_millis = current_millis
        # else if fanState is ON
        else:
            # time is up, so change the state to LOW
            if (current_millis - self.prev_fan_millis) >= self.fan_on_delta:
                self.fanState = OFF
                logger.debug("..FAN OFF")
                self.prev_fan_millis = current_millis
        #self.fanState = ON
        return


class Heater(object):

    def __init__(self):
        logger.info("creating heater")
        self.heaterState = OFF
        self.heatOffMs = cfg.getItemValueFromConfig(
            'heatOffMs')  # min time heater is on or off for
        self.heatOnMs = cfg.getItemValueFromConfig(
            'heatOnMs')  # min time heater is on or off for
        # last time heater switched on or off - enables immediate action if process restarted
        self.lastStateChangeMillis = -180000

        self.heater_sp_offset = cfg.getItemValueFromConfig('heater_sp_offset')

        self.InternalTDiffMs = cfg.getItemValueFromConfig(
            'heatInternalTDiffMs')
        self.ExternalTDiffMs = cfg.getItemValueFromConfig(
            'heatExternalTDiffMs')

        self.status = 0
        self.heatingCycleState = 'INACTIVE'

    def control(self, currentTemp, target_temp, lightState, current_millis, outsideTemp):
        # logger.warning('==Heat ctl==')
        # calc new heater on t based on t gap
        # self.heatOnMs = ((target_temp - currentTemp) * 20 * 1000)  + cfg.getItemValueFromConfig('heatOnMs')
        # logger.warning('==Heat tdelta on: %s',self.heatOnMs)

        # check for heater OFF hours #todo improve this
        #current_hour = datetime.datetime.now().hour
        # if current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm
        # current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm
        if lightState == ON:
            self.heaterState = OFF
            # logger.warning('..d on, in heat off hours - skipping lon heatctl')
        else:  # d off here
            # logger.warning('..light off..do heatctl')
            # logger.warning('self.heatingCycleState: %s' , (self.heatingCycleState) )
            if currentTemp >= (target_temp + self.heater_sp_offset):
                if self.heatingCycleState == 'INACTIVE':
                    self.heaterState = OFF
            # just trigger a defined ON period - force it to complete
            # then force a defined OFF period - force it to complete
            # is a on or off pulse active?
            if currentTemp < (target_temp + self.heater_sp_offset):
                if self.heatingCycleState == 'INACTIVE':
                    #! look at on period based on external temp
                    # extra heater time based on diff from set point per 0.1 degree diff
                    # internalDiffT = int( ((target_temp - currentTemp) * 10 * self.InternalTDiffMs) )
                    #logger.warning('--INTERNAL DIFF extra time to add ms : %s',internalDiffT)

                    # extra  heater time based on external temp diff
                    # do if external diff is >2 deg c
                    if outsideTemp is None:
                        outsideTemp = 10
                    # externalDiffT = int( (target_temp - 2 - outsideTemp) * self.ExternalTDiffMs ) # milli secs per degree diff
                    # milli secs per degree diff
                    externalDiffT = int(
                        (target_temp - outsideTemp) * self.ExternalTDiffMs)

                    #logger.warning('--EXTERNAL DIFF tdelta on to add  ms : %s',externalDiffT)

                    # self.heatOnMs = cfg.getItemValueFromConfig('heatOnMs') + internalDiffT + externalDiffT#+ (float(outsideTemp)/50)
                    self.heatOnMs = cfg.getItemValueFromConfig(
                        'heatOnMs') + externalDiffT  # + (float(outsideTemp)/50)

                    logger.warning(
                        '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>    CALCULATED TOTAL delta ON  ms : %s', self.heatOnMs)

                    # start a cycle - ON first
                    self.heatingCycleState = 'ON'
                    # init ON state timer
                    self.lastStateChangeMillis = current_millis
                    self.heaterState = ON
                    logger.warning(
                        "..........temp low - currently INACTIVE - TURN HEATing cycle state ON")

            if self.heatingCycleState == 'ON':
                if (current_millis - self.lastStateChangeMillis) >= self.heatOnMs:
                    self.heatingCycleState = 'OFF'
                    self.heaterState = OFF
                    self.lastStateChangeMillis = current_millis
                    logger.warning(
                        ".......... - currently ON - TURN HEATing cycle state OFF")

            if self.heatingCycleState == 'OFF':
                if (current_millis - self.lastStateChangeMillis) >= self.heatOffMs:
                    self.heatingCycleState = 'INACTIVE'
                    logger.warning(
                        ".......... - currently OFF - MAKE HEATing cycle state INACTIVE")
                    self.heaterState = OFF
                    self.lastStateChangeMillis = current_millis

        return

    def controlv2(self, currentTemp, target_temp, lightState, current_millis, outsideTemp):
        logger.debug('==Heat ctl==')
        logger.debug('OTOTOTOT outside temp OTOTOTOTO : %s', outsideTemp)

        # current_hour in cfg.getItemValueFromConfig('heat_off_hours'):  # l on and not hh:xx pm
        if lightState == ON:
            #self.heaterState = OFF
            logger.info('..d on, heat off - skipping lon heatctl')
            #self.lastStateChangeMillis = current_millis
            target_temp = 15
            # return

        # lightState OFF if here
        logger.info('..do heatctl')
        if currentTemp >= target_temp + self.heater_sp_offset:
            # turn off and leave
            self.heaterState = OFF
            # current_millis - 180000 # allows immediate on on next cycle if reqd
            self.lastStateChangeMillis = -180000
            logger.info('..d on, in heat off hours - skipping lon heatctl')
            return

        # calc new heater on t based on current temp gap from required temp sp
        #self.heatOnMs = self.heatOnMs + ((target_temp - currentTemp) * 20 * 1000)
        # add extar time
        #! look at on period based on external temp
        # extra heater time based on diff from set point per 0.1 degree diff
        internalDiffT = int(((target_temp - currentTemp)
                             * 10 * self.InternalTDiffMs))
        #logger.warning('--INTERNAL DIFF extra time to add ms : %s',internalDiffT)

        # extra  heater time based on external temp diff
        # do if external diff is >2 deg c
        if outsideTemp is None:
            outsideTemp = 10
        # milli secs per degree diff
        externalDiffT = int((target_temp - 2 - outsideTemp)
                            * self.ExternalTDiffMs)
        #logger.warning('--EXTERNAL DIFF tdelta on to add  ms : %s',externalDiffT)

        self.heatOnMs = cfg.getItemValueFromConfig(
            'heatOnMs') + internalDiffT + externalDiffT  # + (float(outsideTemp)/50)
        logger.info('--     CALCULATED TOTAL delta ON  ms : %s', self.heatOnMs)

    #        self.heatOffMs = cfg.getItemValueFromConfig('heatOffMs') + internalDiffT + externalDiffT#+ (float(outsideTemp)/50)
        # self.heatOffMs = cfg.getItemValueFromConfig('heatOffMs') + internalDiffT # + externalDiffT#+ (float(outsideTemp)/50)
        self.heatOffMs = cfg.getItemValueFromConfig(
            'heatOffMs') + (self.heatOnMs/2)
        #logger.warning('--     CALCULATED TOTAL HEAT OFF ms  : %s',self.heatOffMs)
        #logger.warning('==HDHDHDHDHDHDDHHD Heat tdelta on: %s',self.heatOnMs)
        # below temp sp here
        # check if this is start of a heat cycle - long time passed since last state change
        if self.heaterState == OFF:
            if (current_millis > (self.lastStateChangeMillis + self.heatOffMs)):
                # currentTemp >= target_temp + self.heater_sp_offset:  # if over temp immediately turn off
                self.heaterState = ON
                logger.info("...temp below sp - HEATER ON")
                self.lastStateChangeMillis = current_millis
                return
        # if here must be in a current cycle
        if self.heaterState == ON:  # t below tsp, check if has not been on for currt-last_off_time
            if current_millis > (self.lastStateChangeMillis + self.heatOnMs):
                self.heaterState = OFF
                logger.info(
                    "...in heat auto cycle - switch HEATER OFF after pulse on")
                self.lastStateChangeMillis = current_millis
            else:
                logger.info(
                    'in heat auto cycle - Heater still on - during low temp heat pulse')

        logger.info('Heater state: %s', ('OFF' if self.heaterState else 'ON'))
        return


class Light(object):
    def __init__(self):
        logger.info("creating light object")
        self.lightState = OFF
        self.tOn = dt.time()
        self.tOff = dt.time()

    # return true if testTime between timeOn and TimeOff, else false if in off period
    def getLightState(self):

        # new ldr based routine test
        count = RCtime(cfg.getItemValueFromConfig(
            'RCPin'))  # Measure timing using GPIO4

        if (count > 1000):
            lightState = OFF
        else:
            lightState = ON

        self.lightState = lightState
        return self.lightState


# Function to measure res-cap charge time
def RCtime(RCPin):
    # Discharge capacitor
    GPIO.setup(RCPin, GPIO.OUT)
    GPIO.output(RCPin, GPIO.LOW)
    time.sleep(0.1)  # give time for C to discharge
    GPIO.setup(RCPin, GPIO.IN)  # set RC pin to hi impedance
    # Count loops until voltage across capacitor reads high on GPIO
    measurement = 0
    while (GPIO.input(RCPin) == GPIO.LOW) and (measurement < 9999):
        measurement += 1
    return measurement


class system_timer(object):

    def __init__(self):
        logger.info("creating system timer")
        self.current_hour = datetime.datetime.now().hour
        self.current_time = 0
        self.start_millis = 0
        self.current_millis = 0
        self.delta = 0
        self.lightState = OFF
        self.prevWDPulseMillis = 0
        self.WDPeriod = 10000  # systend sofware process watchdog holdoff space period

        self.watchDogPin = cfg.getItemValueFromConfig('watchDogPin')  #

        # get time at start of program execution
        self.start_millis = datetime.datetime.now()
        self.updateClocks()

    # hold off the process systemd watchdog

    def holdOffWatchdog(self, current_millis, forceWatchdogToggle=False):

        n = sdnotify.SystemdNotifier()

        logger.debug('==Hold Off Watchdog==')
        logger.debug('==current millis: %s' % (current_millis))
        #logger.info('==current fan state: %s' % (self.state))
        # if self.state == OFF:
        # if time is up, so change the state to ON
        if (current_millis - self.prevWDPulseMillis) >= self.WDPeriod:
            #uptime = cfg.getConfigItemFromLocalDB('processUptime')
            #logger.warning("== process uptime: %s =", uptime)

            logger.debug("- Pat the DOG -")
            # print('==WOOF==')
            # reset timer
            self.prevWDPulseMillis = current_millis

            # toggle watchdog pin
            GPIO.output(self.watchDogPin, not GPIO.input(self.watchDogPin))

            logger.debug("DDDDDDDDDD Patted the Systemd watch DOG  DDDDDDDDDD")

            logger.debug(
                "starting : python daemon watchdog and fail test script started\n")

            # notify systemd that we've started
            # retval = sd_notify(0, "READY=1")
            retval = n.notify("READY=1")
            # if (retval != 0):
            #     logger.debug("terminating : fatal sd_notify() error for script start\n")
            # exit(1)

            # after the init, ping the watchdog and check for errors
           # retval = sd_notify(0, "WATCHDOG=1")
            retval = n.notify("WATCHDOG=1")
            # if (retval != 0):
            #     logger.error("terminating : fatal sd_notify() error for watchdog ping\n")

        elif (forceWatchdogToggle == True):
            logger.warning("- FORCE Pat the DOG -")
            # print('==WOOF==')
            # reset timer
            self.prevWDPulseMillis = current_millis

            # toggle watchdog pin
            GPIO.output(self.watchDogPin, not GPIO.input(self.watchDogPin))

            logger.warning("FORCING Pat the Systemd watchDOG")
            retval = n.notify("WATCHDOG=1")

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

    # return sys up time in HH:MM:SS format if poss
    def getSystemUpTime(self):
        # get uptime from the linux terminal command
        from subprocess import check_output
        output = check_output(["uptime"])
        # return only uptime info
        uptime = output[output.find("up")+2:output.find("user")-5]

        return uptime

    def getSystemUpTimeFromProc(self):
        from datetime import timedelta

        with open('/proc/uptime', 'r') as f:
            uptime_seconds = int(float(f.readline().split()[0]) // 1)
            uptime_string = str(timedelta(seconds=uptime_seconds))

        return(uptime_string)

    def secsSinceBoot(self):
        now = datetime.datetime.now()
        current_timestamp = time.mktime(now.timetuple())
        return current_timestamp - psutil.boot_time()


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
        if init:  # report this only one time
            logger.info("Notify socket xxx = " + str(s_adr) + "\n")
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
            logger.error("error : incorrect sock.sendto  return value\n")
            return(1)
    except:
        logger.error("????? sd_notify error ???")
        e = sys.exc_info()[0]
        logger.error("????? Error: %s ?????" % e)
    finally:
        # terminate the socket connection
        if sock:
            sock.close()
        if unset_environment:
            if 'NOTIFY_SOCKET' in os.environ:
                del os.environ['NOTIFY_SOCKET']
    return(0)  # OK
