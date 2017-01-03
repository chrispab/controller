import logging
import csv

from ConfigObject import cfg # singleton global
from DatabaseObject import db # singleton global

from support import round_time as round_time

OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on
path = cfg.getItemValueFromConfig('dataPath')

#processUptime = 0
#systemMessage = 0


class Logger(object):
    # roundT = roundTime

    def __init__(self):
        logging.info("creating logger object")
        self.temperature = 0
        self.humidity = 0
        self.heater_state = OFF
        self.vent_state = OFF
        self.fan_state = OFF
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
        self.min_CSV_write_interval = cfg.getItemValueFromConfig('min_CSV_write_interval')


    def update_CSV_If_changes(self, temperature, humidity, vent_state,
                              fan_state, heater_state, vent_speed_state, current_millis,
                              current_time, proc_temp):
        self.temperature = temperature
        self.humidity = humidity
        self.vent_state = vent_state
        self.fan_state = fan_state
        self.heater_state = heater_state
        self.vent_speed_state = vent_speed_state
        self.current_millis = current_millis
        self.current_time = current_time
        self.proc_temp = proc_temp

        self.state_changed = False
        logging.info('==Update CSV==')

        # check each for state change and set new prewrite states
        if self.vent_state != self.previous_vent_state:  # any change in vent
            if self.previous_vent_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logging.info("--new prevvent low row appended to CSV -----")
                self.vent_state = OFF
                self.state_changed = True
            else:  # if self.previous_vent_state == ON:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logging.info("-- new prevvent hi row appended to CSV -----")
                self.vent_state = ON
                self.state_changed = True

        if self.vent_speed_state != self.previous_vent_speed_state:  # any change in vent speed
            if self.previous_vent_speed_state == OFF:  # was lo speed
                # write a low record immediately before hi record
                logging.info("-- new prevvspeed low row appended to CSV -----")
                self.vent_speed_state = OFF
                self.state_changed = True
            else:  # was hi speed going low
                # write a on record immediately before hi record
                logging.info("-- new prevvspeed hi row appended to CSV -----")
                self.vent_speed_state = ON
                self.state_changed = True

        if self.fan_state != self.previous_fan_state:  # any change in vent
            if self.previous_fan_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logging.info("-- new prevfanstate low row appended to CSV -----")
                self.fan_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logging.info("-- new  prevfanstate hi row appended to CSV -----")
                self.fan_state = ON
                self.state_changed = True

        if self.heater_state != self.previous_heater_state:  # any change in vent
            if self.previous_heater_state == OFF:  # must be going OFF to ON
                # write a low record immediately before hi record
                logging.info("-- new heaterstate low row appended to CSV -----")
                self.heater_state = OFF
                self.state_changed = True
            else:  # must be going ON TO OFF
                # write a on record immediately before hi record
                logging.info("-- new  heaterstate hi row appended to CSV -----")
                self.heater_state = ON
                self.state_changed = True

        # if ((self.temperature != self.previous_temperature)):  # any change
            #self.state_changed = True

        if self.state_changed == True:
            logging.warning("O/P State Change - prewrite")
            self.dataHasChanged()  # write modded pre change state(s)
            self.vent_state = vent_state
            self.vent_speed_state = vent_speed_state
            self.heater_state = heater_state
            self.fan_state = fan_state
            self.dataHasChanged()  # write modded post change state(s)
            self.previous_CSV_write_millis = self.current_millis  # reset timer
        else:  # no state change check temp change or and timer csv write interval done
            if ((self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval))
                    or (self.temperature != self.previous_temperature)):  # any change
                if self.current_millis > (self.previous_CSV_write_millis + self.min_CSV_write_interval):
                    logging.warning("..interval passed ..time for new CSV write")
                else:
                    logging.warning("..new data row generated")
                self.dataHasChanged()
                self.previous_CSV_write_millis = self.current_millis  # reset timer

        self.previous_temperature = self.temperature
        self.previous_humidity = self.humidity
        self.previous_heater_state = self.heater_state
        self.previous_vent_state = self.vent_state
        self.previous_fan_state = self.fan_state
        self.previous_vent_speed_state = self.vent_speed_state
        self.previous_proc_temp = self.proc_temp

        return

    #routine called when any data has changed state temp or periodic timer
    def dataHasChanged(self):

        global processUptime
        global systemMessage
        
        logging.warning("Data Has Changed")
        data = self._write_to_CSV()
        
        db.writeSampleToLocalDB(data[0], data[1], data[2], data[3], data[4], data[5])

        db.update_central_db()
        
        #cfg.setConfigItemInDB('processUptime', processUptime)
        #cfg.setConfigItemInDB('systemMessage', systemMessage )
        
        processUptime = cfg.getConfigItemFromLocalDB('processUptime')
        systemMessage = cfg.getConfigItemFromLocalDB('systemMessage')
        logging.debug('=Process uptime: %s' % (processUptime))
        logging.debug('=System message: %s' % (systemMessage))
        
        cfg.updateCentralConfigTable()
        
        return
        

    def _write_to_CSV(self):

        logging.warning('=== _write_to_CSV data record ===')
        data = ['time', 'temp', 'humi', 'heaterstate',
                'ventstate', 'fanstate', 'procTemp']
        # round timestamp to nearest second
        data[0] = round_time(self.current_time, 1)
#        data[0] = datetime.datetime.now() # round timestamp to nearest second

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

        data[6] = round(self.proc_temp, 1)  # add processed temp value
        #sys.stdout.write(data.tostring() )
        with open(path, "ab") as csv_file:
            # with open(path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            # for line in data:
            # outfile.write(bytes(plaintext, 'UTF-8'))
            writer.writerow(data)
            self.previous_CSV_write_millis = self.current_millis  # note time row written
        #self.datastore.writedb(self.current_time, self.temperature, self.humidity, self.heater_state, self.vent_state, self.fan_state)
        
        return data

