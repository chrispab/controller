import logging
logger = logging.getLogger(__name__)

from ConfigObject import cfg # singleton global
OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on
import socket
import subprocess


class MessageService(object):

    def __init__(self):
        logger.info("Creating TelemetryService")
        self.zoneName = cfg.getItemValueFromConfig('zoneName')  # e.g Zone1, Zone3
        self.lastMqttPublishTeleMillis = 0
        self.mqttPublishTeleIntervalMillis = cfg.getItemValueFromConfig('mqttPublishTeleIntervalMillis')
        self.lastMqttPublishHeartBeatMillis = 0
        self.mqttPublishIntervalMillis = cfg.getItemValueFromConfig('mqttPublishIntervalMillis')
        self.ackMessage = cfg.getItemValueFromConfig('ackMessage')

    # send mqtt message heartbeat, to be subscribed by the 433 gateway, which power cyles this controller
    # useful cos supplements the rf24 link heartbeat link to the 433 hub
    # send every mqttPublishIntervalMillis
    def alertAbnormalTemps(self, temperature):

            # check for alarm levels etc
            if temperature > cfg.getItemValueFromConfig('tempAlertHi'):
                try:
                    emailObj.send(zone + ' - Hi Temp warning' +
                                  temperature, 'Hi Temp warning')
                except:
                    logger.error("...ERROR SENDING EMAIL - for hi temp alert")

            if temperature < cfg.getItemValueFromConfig('tempAlertLo'):
                try:
                    emailObj.send(zone + ' - Lo Temp warning' +
                                  temperature, 'Lo Temp warning')
                except:
                    logger.error("...ERROR SENDING EMAIL - low temp alert")
            
    #! send telemetry periodically
    # long intervasl mqtt messages of low priority, e.g rssi, online, ventOn/Off Deltas etc
    def pubMQTTTeleIfDue(self, current_millis, MQTTClient):
        logger.info('==  publish MQTT Telemetry  ==')

        if current_millis - self.lastMqttPublishTeleMillis > self.mqttPublishTeleIntervalMillis:
            logger.warning('---> publish MQTT TELE info')

            MQTTClient.publish(self.zoneName + "/vent_on_delta_secs",
                                int(cfg.getItemValueFromConfig('ventOnDelta')/1000))
            MQTTClient.publish(self.zoneName + "/vent_off_delta_secs",
                                int(cfg.getItemValueFromConfig('ventOffDelta')/1000))

            logger.warning('===---> ' + self.zoneName + "/vent_on_delta_secs : " +
                            str(int(cfg.getItemValueFromConfig('ventOnDelta')/1000)))
            logger.warning('===---> ' + self.zoneName + "/vent_off_delta_secs : " +
                            str(int(cfg.getItemValueFromConfig('ventOffDelta')/1000)))
            # logger.warning('==-> ' + zone + "/LWT:" + "Online")

            MQTTClient.publish(self.zoneName + "/rssi", self.getRSSI())
            MQTTClient.publish(self.zoneName + "/LWT", "Online", 0, True)
            self.lastMqttPublishTeleMillis = current_millis
            # anyChanges = True

    # get rssi
    def getRSSI(self):
        rssi = ""
        try:
            wifn = socket.if_nameindex()[2][1]
            proc = subprocess.Popen(
                ["iwconfig", wifn], stdout=subprocess.PIPE, universal_newlines=True)
            out, err = proc.communicate()
            rssi = self.derive_rssi(out)
            rssi = rssi.strip()
            # logger.warning(rssi)
        except:
            print("-------CANNOT get wifi RSSI info=======!!!")
        return rssi

# !RSSI
    # interface = "wlxe091f5545119:"


    def derive_rssi(self, iwconfigStr):
        # Signal level is on same line as Quality data so a bit of ugly
        # hacking needed...
        # arrWords = iwconfigStr
        # return
        x = iwconfigStr.find("Quality=")
        lines = iwconfigStr[x:].split()
        kval = lines[0].split("=")
        kval2 = kval[1].split("/")

    # line = matching_line(cell,"Quality=")
    # level = line.split()[0].split('/')
        return str(int(round(float(kval2[0]) / float(kval2[1]) * 100))).rjust(3)
    #  + " %"
    # return kval2
# !_RSSI
