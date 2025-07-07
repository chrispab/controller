from support import round_time as round_time
from DatabaseObject import db  # singleton global
from ConfigObject import cfg  # singleton global
import logging
import csv
import datetime
import sys
import time

logger = logging.getLogger(__name__)


OFF = cfg.getItemValueFromConfig("RelayOff")  # state for relay OFF
ON = cfg.getItemValueFromConfig("RelayOn")  # state for on
path = cfg.getItemValueFromConfig("dataPath")

# processUptime = 0
# systemMessage = 0


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
        self.previous_light_state = OFF
        self.previous_vent_speed_state = OFF
        self.previous_vent_percent = 0
        self.previous_proc_temp = 0
        self.previous_CSV_write_millis = 0
        self.min_CSV_write_interval = cfg.getItemValueFromConfig(
            "min_CSV_write_interval"
        )
        # self.min_CSV_write_interval = 500 #cfg.getItemValueFromConfig('min_CSV_write_interval')

    ###
    #  "Time      [Te]  [Hu]  H V F S L VT"

    def getDisplayHeaderString(self):
        return "Time ---- [Te]--[Hu]--L-H-F-V-S-VT"

    ###
    # build a string with values for the main controlled/monitored values for use in web socket display op
    # example string:
    # Time - HH.MM.SS, Temperature - NN.N, Humidity - NN.N %, Light - 0/1, Heat - 0/1, Fan - 0/1, Vent - 0/1, VentSpeed - 0/1, VentTotal 0/1/2
    #  "17:02:01  20.4  64.1  0 1 1 1 0 2"
    def getDisplayStatusString(self):
        # data = self._write_to_CSV()
        sep = " "
        statusString = (
            self.format_time()
            + sep
            + sep
            + str(self.temperature)
            + sep
            + sep
            + str(self.humidity)
            + sep
            + sep
            + str(self.light_state)
            + sep
            + str(self.heater_state)
            + sep
            + str(self.fan_state)
            + sep
            + str(self.vent_state)
            + sep
            + str(self.vent_speed_state)
            + sep
            + str(self.vent_state + self.vent_speed_state)
        )
        return str(statusString)

    # covert date time to fixed length format string for display
    def format_time(self):
        t = datetime.datetime.now()
        # s = t.strftime('%Y-%m-%d %H:%M:%S.%f')
        s = t.strftime("%H:%M:%S")
        # return s[:-4]
        return s

    def checkForChangeInTemperature(self, temperature):

        self.state_changed = False

        if temperature != self.previous_temperature:  # any change
            self.state_changed = True
        self.previous_temperature = temperature

        return self.state_changed

    def checkForChangeInHumidity(self, humidity):

        self.state_changed = False

        if humidity != self.previous_humidity:  # any change
            self.state_changed = True
        self.previous_humidity = humidity

        return self.state_changed

    # def checkForChangeInFanState(self, fanState):

    #     self.state_changed = False

    #     if fanState != self.previous_fan_state:  # any change
    #         self.state_changed = True
    #     self.previous_fan_state = fanState

    #     return self.state_changed

    def checkForChangeInFanState(self, fanState):
        changed = fanState != self.previous_fan_state
        self.previous_fan_state = fanState
        return changed
        # Repeat for other checkForChangeIn* methods

    def checkForChangeInVentState(self, ventState):

        self.state_changed = False

        if ventState != self.previous_vent_state:  # any change
            self.state_changed = True
        self.previous_vent_state = ventState

        return self.state_changed

    def checkForChangeInHeaterState(self, heaterState):
        self.state_changed = False
        if heaterState != self.previous_heater_state:  # any change
            self.state_changed = True
        self.previous_heater_state = heaterState
        return self.state_changed

    def checkForChangeInVentSpeedState(self, ventSpeedState):
        self.state_changed = False
        if ventSpeedState != self.previous_vent_speed_state:  # any change
            self.state_changed = True
        self.previous_vent_speed_state = ventSpeedState
        return self.state_changed

    def checkForChangeInLightState(self, lightState):
        self.state_changed = False
        if lightState != self.previous_light_state:  # any change
            self.state_changed = True
        self.previous_light_state = lightState
        return self.state_changed

    def checkForChangeInVentPercent(self, ventPercent):
        self.state_changed = False
        if ventPercent != self.previous_vent_percent:  # any change
            self.state_changed = True
        self.previous_vent_percent = ventPercent
        return self.state_changed

    # def checkForChanges(
    #     self,
    #     temperature,
    #     humidity,
    #     vent_state,
    #     fan_state,
    #     heater_state,
    #     vent_speed_state,
    #     light_state,
    #     current_millis,
    #     current_time,
    # ):

    #     self.temperature = temperature
    #     self.humidity = humidity
    #     self.vent_state = vent_state
    #     self.fan_state = fan_state
    #     self.heater_state = heater_state
    #     self.vent_speed_state = vent_speed_state
    #     self.light_state = light_state
    #     self.current_millis = current_millis
    #     self.current_time = current_time
    #     self.state_changed = False
    #     logger.info("== Checking for changes ==")

    #     # check each for state change and set new prewrite states
    #     if self.vent_state != self.previous_vent_state:  # any change in vent
    #         if self.previous_vent_state == OFF:  # must be going OFF to ON
    #             # write a low record immediately before hi record
    #             logger.info("--new prevvent low row appended to CSV -----")
    #             self.vent_state = OFF
    #             self.state_changed = True
    #         else:  # if self.previous_vent_state == ON:  # must be going ON TO OFF
    #             # write a on record immediately before hi record
    #             logger.info("-- new prevvent hi row appended to CSV -----")
    #             self.vent_state = ON
    #             self.state_changed = True

    #     if (
    #         self.vent_speed_state != self.previous_vent_speed_state
    #     ):  # any change in vent speed
    #         if self.previous_vent_speed_state == OFF:  # was lo speed
    #             # write a low record immediately before hi record
    #             logger.info("-- new prevvspeed low row appended to CSV -----")
    #             self.vent_speed_state = OFF
    #             self.state_changed = True
    #         else:  # was hi speed going low
    #             # write a on record immediately before hi record
    #             logger.info("-- new prevvspeed hi row appended to CSV -----")
    #             self.vent_speed_state = ON
    #             self.state_changed = True

    #     if self.fan_state != self.previous_fan_state:  # any change in vent
    #         if self.previous_fan_state == OFF:  # must be going OFF to ON
    #             # write a low record immediately before hi record
    #             logger.info("-- new prevfanstate low row appended to CSV -----")
    #             self.fan_state = OFF
    #             self.state_changed = True
    #         else:  # must be going ON TO OFF
    #             # write a on record immediately before hi record
    #             logger.info("-- new  prevfanstate hi row appended to CSV -----")
    #             self.fan_state = ON
    #             self.state_changed = True

    #     if (
    #         self.heater_state != self.previous_heater_state
    #     ):  # any change in heater state
    #         if self.previous_heater_state == OFF:  # must be going OFF to ON
    #             # write a low record immediately before hi record
    #             logger.info("-- new heaterstate low row appended to CSV -----")
    #             self.heater_state = OFF
    #             self.state_changed = True
    #         else:  # must be going ON TO OFF
    #             # write a on record immediately before hi record
    #             logger.info("-- new  heaterstate hi row appended to CSV -----")
    #             self.heater_state = ON
    #             self.state_changed = True

    #     # if ((self.temperature != self.previous_temperature)):  # any change
    #     # self.state_changed = True

    #     if self.state_changed == True:
    #         logger.debug("-- O/P State Change - OLD state --")
    #         self.dataHasChangedUpdateDb()  # write modded old change state(s)
    #         # restore new vals from original params
    #         self.vent_state = vent_state
    #         self.vent_speed_state = vent_speed_state
    #         self.heater_state = heater_state
    #         self.fan_state = fan_state

    #         logger.debug("-- O/P State Change - NEW state --")
    #         # write new states
    #         self.dataHasChangedUpdateDb()  # write modded post change state(s)

    #         # processUptime = cfg.getConfigItemFromLocalDB('processUptime')
    #         # systemMessage = cfg.getConfigItemFromLocalDB('systemMessage')
    #         # logger.debug('=Process uptime: %s' % (processUptime))
    #         # logger.debug('=System message: %s' % (systemMessage))
    #         # cfg.updateCentralConfigTable()

    #         self.previous_CSV_write_millis = self.current_millis  # reset timer
    #     else:  # no state change check temp change or and timer csv write interval done
    #         if (
    #             self.current_millis
    #             > (self.previous_CSV_write_millis + self.min_CSV_write_interval)
    #         ) or (
    #             self.temperature != self.previous_temperature
    #         ):  # any change
    #             if self.current_millis > (
    #                 self.previous_CSV_write_millis + self.min_CSV_write_interval
    #             ):
    #                 logger.debug(
    #                     "..min interval passed with no new samples..time for new CSV write"
    #                 )
    #             else:
    #                 logger.debug("..new data row generated.. new temp")
    #             self.dataHasChangedUpdateDb()

    #             self.previous_CSV_write_millis = self.current_millis  # reset timer
    #             self.state_changed = True
    #     self.previous_temperature = self.temperature
    #     self.previous_humidity = self.humidity
    #     self.previous_heater_state = self.heater_state
    #     self.previous_vent_state = self.vent_state
    #     self.previous_fan_state = self.fan_state
    #     self.previous_vent_speed_state = self.vent_speed_state
    #     # self.previous_proc_temp = self.proc_temp

    #     return self.state_changed
    

    def checkForChanges(
        self,
        temperature,
        humidity,
        vent_state,
        fan_state,
        heater_state,
        vent_speed_state,
        light_state,
        current_millis,
        current_time,
    ):
        """
        Checks for changes in environmental and device states, updates internal state,
        and triggers database updates if changes are detected or if a minimum interval has passed.

        Args:
            temperature (float): The current temperature reading.
            humidity (float): The current humidity reading.
            vent_state (Any): The current state of the vent.
            fan_state (Any): The current state of the fan.
            heater_state (Any): The current state of the heater.
            vent_speed_state (Any): The current speed/state of the vent.
            light_state (Any): The current state of the light.
            current_millis (int): The current time in milliseconds.
            current_time (Any): The current time (format depends on implementation).

        Returns:
            bool: True if a significant state change was detected or a periodic update was triggered, False otherwise.

        Side Effects:
            - Updates internal state variables to reflect the latest readings.
            - Calls `dataHasChangedUpdateDb()` to persist changes if necessary.
            - Logs state changes and periodic updates.
        """
        # Capture previous states
        old_states = {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "vent_state": self.vent_state,
            "fan_state": self.fan_state,
            "heater_state": self.heater_state,
            "vent_speed_state": self.vent_speed_state,
            "light_state": self.light_state,
        }

        # Update to new states
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
        logger.debug("== Checking for changes ==")

        # Check for any state change
        if (
            old_states["vent_state"] != vent_state
            or old_states["vent_speed_state"] != vent_speed_state
            or old_states["fan_state"] != fan_state
            or old_states["heater_state"] != heater_state
        ):
            self.state_changed = True
            logger.debug("-- O/P State Change - OLD state --")
            # Temporarily set states to old for writing
            self.vent_state = old_states["vent_state"]
            self.vent_speed_state = old_states["vent_speed_state"]
            self.heater_state = old_states["heater_state"]
            self.fan_state = old_states["fan_state"]
            self.dataHasChangedUpdateDb()  # write old state

            # Restore new states
            self.vent_state = vent_state
            self.vent_speed_state = vent_speed_state
            self.heater_state = heater_state
            self.fan_state = fan_state

            logger.debug("-- O/P State Change - NEW state --")
            self.dataHasChangedUpdateDb()  # write new state

            self.previous_CSV_write_millis = self.current_millis  # reset timer
        else:
            # No state change, check for temp change or interval
            if (
                self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval)
                or temperature != self.previous_temperature
            ):
                if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                    logger.debug("..min interval passed with no new samples..time for new CSV write")
                else:
                    logger.debug("..new data row generated.. new temp")
                self.dataHasChangedUpdateDb()
                self.previous_CSV_write_millis = self.current_millis
                self.state_changed = True

        # Update previous states
        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state

        return self.state_changed


    # routine called when any data has changed state or temp or periodic timer


    def dataHasChangedUpdateDb(self):
        """
        Handles the process of updating local and remote databases when data readings have changed.

        This method performs the following actions:
            - Logs a warning indicating that readings have changed and databases are being updated.
            - Writes the current data to a CSV file (twice).
            - Writes the collected sample data to the local database.
            - Updates the central database and logs the duration of this operation.

        Note:
            The method currently returns immediately and does not execute its logic.
            The reason for writing to CSV twice is unclear and may be intentional or a bug.

        Returns:
            None
        """
        return
        # Log that readings have changed and databases are being updated
        logger.debug("Readings have changed - updating local and remote dbs")
        # logger.warning("DataChanged Time: %s", str(datetime.datetime.now()))
        # logger.warning("DataChanged Time: %s", str(datetime.datetime.now()))
        # Write data to CSV (twice, which might be a bug or intentional for some reason)
        data = self._write_to_CSV()
        data = self._write_to_CSV()
        # Write the collected sample data to the local database
        db.writeSampleToLocalDB(data[0], data[1], data[2], data[3], data[4], data[5])
        # Update the central database and measure the duration of this operation
        time1 = datetime.datetime.now()
        db.update_central_db()
        time2 = datetime.datetime.now()
        duration = time2 - time1
        logger.debug("TTTTT - update central db duration : %s" % (duration))
        # return

    def _write_to_CSV(self):
        """
        Prepares a list of sensor and actuator state data for CSV logging.

        The data includes:
            - Current timestamp (rounded to milliseconds)
            - Temperature reading
            - Humidity reading
            - Heater state (0 for OFF, 1 for ON)
            - Vent state (0 for OFF, 1 for ON with low speed, 2 for ON with high speed)
            - Fan state (0 for OFF, 1 for ON)

        Returns:
            list: A list containing the formatted data for CSV writing.
        """

        logger.debug("=== _write_to_CSV data record ===")
        data = ["time", "temp", "humi", "heaterstate", "ventstate", "fanstate"]
        # round timestamp to nearest second
        #        data[0] = self.current_time

        sample_dt = datetime.datetime.now()  # gives time with 6 dp
        # convert to string and trim off last 3 digits
        sample_txt = sample_dt.strftime("%Y-%m-%d %H:%M:%S.%f")
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
        # writer = csv.writer(csv_file, delimiter=',')
        # writer.writerow(data)
        # self.previous_CSV_write_millis = self.current_millis  # note time row written

        return data
