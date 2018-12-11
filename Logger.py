import logging
import csv
import datetime
import sys
import time

logger = logging.getLogger(__name__)

from ConfigObject import cfg  # singleton global
from DatabaseObject import db  # singleton global

from support import round_time as round_time

OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on
path = cfg.getItemValueFromConfig('dataPath')

#processUptime = 0
#systemMessage = 0


class Logger(object):
    # roundT = roundTime

    def __init__(self):
        logger.info("creating logger object")
        self.temperature = 0
        self.humidity = 0
        self.heater_state = OFF
        self.vent_state = OFF
        self.fan_state = OFF
        self.light_state = OFF
        self.vent_speed_state = OFF
        self.current_millis = 0
        self.current_time = 0
        self.previous_temperature = 0
        self.previous_humidity = 0
        self.previous_heater_state = OFF
        self.previous_vent_state = OFF
        self.previous_fan_state = OFF
        self.previous_vent_speed_state = OFF
        self.previous_proc_temp = 0
        self.previous_CSV_write_millis = 0
        self.min_CSV_write_interval = cfg.getItemValueFromConfig(
            'min_CSV_write_interval')

    def getStatusString(self):
        #data = self._write_to_CSV()

        statusString = self.format_time() + ": "+str(self.temperature) + \
            ", " + str(self.humidity) + ", " + str(self.heater_state) + \
            ", " + str(self.vent_state) + ", " + str(self.fan_state) + \
            ", " + str(self.vent_speed_state) + ", " + str(self.light_state) + \
            ", " + str(self.vent_state+self.vent_speed_state)

        return str(statusString)

    def format_time(self):
        t = datetime.datetime.now()
        s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        return s[:-4]

    def checkForChanges(self, temperature, humidity, vent_state,
                        fan_state, heater_state, vent_speed_state, light_state,
                        current_millis, current_time):

        self.temperature = temperature
        self.humidity = humidity
        self.vent_state = vent_state
        self.fan_state = fan_state
        self.heater_state = heater_state
        self.vent_speed_state = vent_speed_state
        self.light_state = light_state
        self.current_millis = current_millis
        self.current_time = current_time
        self.state_changed = False
        logger.info('== Checking for changes ==')

        # check each for state change and set new prewrite states
        if self.vent_state != self.previous_vent_state:  # any change in vent
            if self.previous_vent_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logger.info("--new prevvent low row appended to CSV -----")
                self.vent_state = OFF
                self.state_changed = True
            else:  # if self.previous_vent_state == ON:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logger.info("-- new prevvent hi row appended to CSV -----")
                self.vent_state = ON
                self.state_changed = True

        if self.vent_speed_state != self.previous_vent_speed_state:  # any change in vent speed
            if self.previous_vent_speed_state == OFF:  # was lo speed
                # write a low record immediately before hi record
                logger.info("-- new prevvspeed low row appended to CSV -----")
                self.vent_speed_state = OFF
                self.state_changed = True
            else:  # was hi speed going low
                # write a on record immediately before hi record
                logger.info("-- new prevvspeed hi row appended to CSV -----")
                self.vent_speed_state = ON
                self.state_changed = True

        if self.fan_state != self.previous_fan_state:  # any change in vent
            if self.previous_fan_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logger.info(
                    "-- new prevfanstate low row appended to CSV -----")
                self.fan_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logger.info(
                    "-- new  prevfanstate hi row appended to CSV -----")
                self.fan_state = ON
                self.state_changed = True

        if self.heater_state != self.previous_heater_state:  # any change in vent
            if self.previous_heater_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logger.info("-- new heaterstate low row appended to CSV -----")
                self.heater_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logger.info("-- new  heaterstate hi row appended to CSV -----")
                self.heater_state = ON
                self.state_changed = True

        # if ((self.temperature != self.previous_temperature)):  # any change
            #self.state_changed = True

        if self.state_changed == True:
            logger.debug("-- O/P State Change - OLD state --")
            self.dataHasChanged()  # write modded old change state(s)
            # restore new vals
            self.vent_state = vent_state
            self.vent_speed_state = vent_speed_state
            self.heater_state = heater_state
            self.fan_state = fan_state

            logger.debug("-- O/P State Change - NEW state --")
            # write new states
            self.dataHasChanged()  # write modded post change state(s)

            #processUptime = cfg.getConfigItemFromLocalDB('processUptime')
            #systemMessage = cfg.getConfigItemFromLocalDB('systemMessage')
            #logger.debug('=Process uptime: %s' % (processUptime))
            #logger.debug('=System message: %s' % (systemMessage))
            # cfg.updateCentralConfigTable()

            self.previous_CSV_write_millis = self.current_millis  # reset timer
        else:  # no state change check temp change or and timer csv write interval done
            if ((self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval))
                    or (self.temperature != self.previous_temperature)):  # any change
                if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                    logger.debug(
                        "..min interval passed with no new samples..time for new CSV write")
                else:
                    logger.debug("..new data row generated.. new temp")
                self.dataHasChanged()

                self.previous_CSV_write_millis = self.current_millis  # reset timer
                self.state_changed = True
        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state
        #self.previous_proc_temp = self.proc_temp

        return self.state_changed

    # routine called when any data has changed state or temp or periodic timer
    def dataHasChanged(self):
        logger.warning("Readings have changed - updating local and remote dbs")
        #logger.warning("DataChanged Time: %s", str(datetime.datetime.now()))
        #logger.warning("DataChanged Time: %s", str(datetime.datetime.now()))
        data = self._write_to_CSV()
        data = self._write_to_CSV()
        db.writeSampleToLocalDB(
            data[0], data[1], data[2], data[3], data[4], data[5])
        time1 = datetime.datetime.now()
        db.update_central_db()
        time2 = datetime.datetime.now()
        duration = time2 - time1
        logger.debug("TTTTT - update central db duration : %s" % (duration))
        return

    def _write_to_CSV(self):

        logger.info('=== _write_to_CSV data record ===')
        data = ['time', 'temp', 'humi', 'heaterstate',
                'ventstate', 'fanstate']
        # round timestamp to nearest second
#        data[0] = self.current_time

        sample_dt = datetime.datetime.now()  # gives time with 6 dp
        # convert to string and trim off last 3 digits
        sample_txt = sample_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        sample_txt = sample_txt[:-3]
        data[0] = sample_txt

        data[1] = self.temperature
        data[2] = self.humidity
        if self.heater_state == OFF:
            data[3] = 0  # off line on graph
        else:
            data[3] = 1  # on line on graph
        if self.vent_state == OFF:
            data[4] = 0  # off line on graph
        if self.vent_state == ON:
            if self.vent_speed_state == OFF:  # vent on andspeed ==low
                data[4] = 1  # on line on graph
            if self.vent_speed_state == ON:  # vent on and hi speed
                data[4] = 2  # on line on graph
        if self.fan_state == OFF:
            data[5] = 0  # off line on graph
        else:
            data[5] = 1  # on line on graph

        # with open(path, "ab") as csv_file:
            #writer = csv.writer(csv_file, delimiter=',')
            # writer.writerow(data)
            # self.previous_CSV_write_millis = self.current_millis  # note time row written

        return data
