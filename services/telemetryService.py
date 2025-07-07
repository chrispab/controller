import subprocess
import socket
from ConfigObject import cfg  # singleton global
import logging

logger = logging.getLogger(__name__)
from version import VERSION

OFF = cfg.getItemValueFromConfig("RelayOff")  # state for relay OFF
ON = cfg.getItemValueFromConfig("RelayOn")  # state for on


class TelemetryService(object):

    def __init__(self):
        logger.info("Creating TelemetryService")
        self.zoneName = cfg.getItemValueFromConfig("zoneName")  # e.g Zone1, Zone3
        self.lastMqttPublishTeleMillis = -1  # -1 to indicate not yet valid ms
        self.mqttPublishTeleIntervalMillis = cfg.getItemValueFromConfig(
            "mqttPublishTeleIntervalMillis"
        )
        self.lastMqttPublishHeartBeatMillis = 0
        self.mqttPublishIntervalMillis = cfg.getItemValueFromConfig(
            "mqttPublishIntervalMillis"
        )
        self.ackMessage = cfg.getItemValueFromConfig("ackMessage")

    def pubMQTTReadings(
        self,
        MQTTClient,
        ctl1,
        humidity,
        temperature,
        lightState,
        heaterState,
        fanState,
        ventState,
        ventSpeedState,
    ):
        """
        Publishes MQTT messages for zone telemetry readings, but only for values that have changed.

        This method checks for changes in various telemetry readings (temperature, humidity, fan state, vent state, vent speed, vent percent, heater state, and light state)
        using the provided controller's state monitor. If a change is detected in any of these readings, the corresponding MQTT message is published to the appropriate topic.
        The method returns a boolean indicating whether any changes were detected and published.

        Args:
            MQTTClient: The MQTT client instance used to publish messages.
            ctl1: The controller instance containing the state monitor for change detection.
            humidity (float): The current humidity reading.
            temperature (float): The current temperature reading.
            lightState (int): The current state of the light.
            heaterState (int): The current state of the heater.
            fanState (int): The current state of the fan.
            ventState (int): The current state of the vent.
            ventSpeedState (int): The current speed state of the vent.

        Returns:
            bool: True if any telemetry readings changed and were published, False otherwise.
        """
        logger.info("==  publish MQTT Readings  ==")
        # only send mqtt messages for the changed i/o - not all as previous message
        onlyPublishMQTTOnChange = cfg.getItemValueFromConfig("onlyPublishMQTTOnChange")
        anyChanges = False

        if onlyPublishMQTTOnChange:
            temperatureChanged = ctl1.stateMonitor.checkForChangeInTemperature(
                temperature
            )
            if temperatureChanged:
                MQTTClient.publish(self.zoneName + "/TemperatureStatus", temperature)
                MQTTClient.publish(self.zoneName + "/HumidityStatus", humidity)
                logger.debug("Temp change MQTT published temp and humi")
                anyChanges = True

            fanChanged = ctl1.stateMonitor.checkForChangeInFanState(fanState)
            if fanChanged:
                MQTTClient.publish(self.zoneName + "/FanStatus", fanState)
                # logger.warning(
                #     '++++++++++++++++================================')
                # logger.warning(
                #     '++++++++++++++++ Fan state change MQTT published')
                # logger.warning(fanState)
                # logger.warning(
                #     '++++++++++++++++================================')
                anyChanges = True

            # publish vent data
            ventStateChanged = ctl1.stateMonitor.checkForChangeInVentState(ventState)
            if ventStateChanged:
                MQTTClient.publish(self.zoneName + "/VentStatus", ventState)
                # logger.warning("Vent state change MQTT published")
                MQTTClient.publish(
                    self.zoneName + "/VentValue", ventState + ventSpeedState
                )
                logger.warning("Vent value 0,1,2 change MQTT published")
                anyChanges = True

            ventSpeedChanged = ctl1.stateMonitor.checkForChangeInVentSpeedState(
                ventSpeedState
            )
            if ventSpeedChanged:
                MQTTClient.publish(self.zoneName + "/VentSpeedStatus", ventSpeedState)
                logger.warning(
                    "++++++++++++++++ Vent Speed state change MQTT published"
                )
                anyChanges = True

            ventPercent = ventState * ((ventSpeedState + 1) * 50)
            ventPercentChanged = ctl1.stateMonitor.checkForChangeInVentPercent(
                ventPercent
            )
            if ventPercentChanged:
                MQTTClient.publish(self.zoneName + "/VentPercent", ventPercent)
                logger.warning("++++++++++++++++ Vent percent change MQTT published")
                anyChanges = True

            heaterStateChangeed = ctl1.stateMonitor.checkForChangeInHeaterState(
                heaterState
            )
            if heaterStateChangeed:
                MQTTClient.publish(self.zoneName + "/HeaterStatus", heaterState)
                logger.warning("++++++++++++++++ Heater state change MQTT published")
                anyChanges = True

            lightChanged = ctl1.stateMonitor.checkForChangeInLightState(lightState)
            if lightChanged:
                MQTTClient.publish(self.zoneName + "/LightStatus", lightState)
                logger.warning("++++++++++++++++ Light state change MQTT published")
                anyChanges = True

            return anyChanges  # return if changes or not are detected

    # send mqtt message heartbeat, to be subscribed by the 433 gateway, which power cyles this controller
    # useful cos supplements the rf24 link heartbeat link to the 433 hub
    # send every mqttPublishIntervalMillis
    def pubMQTTHeartBeat(self, current_millis, MQTTClient):

        if (
            current_millis - self.lastMqttPublishHeartBeatMillis
            > self.mqttPublishIntervalMillis
        ):

            MQTTClient.publish(self.zoneName + "/HeartBeat", self.ackMessage)

            logger.warning(self.zoneName + " MQTT published HeartBeat")
            logger.warning(self.zoneName + "/HeartBeat:" + self.ackMessage)
            logger.warning(self.zoneName + "/LWT:" + "Online")
            self.lastMqttPublishHeartBeatMillis = current_millis
            # anyChanges = True


    #! send telemetry periodically
    # long intervasl mqtt messages of low priority, e.g rssi, online, ventOn/Off Deltas etc
    def pubMQTTTele(self, current_millis, MQTTClient, ctl1):
        logger.info("==  publish MQTT Telemetry  ==")

        # check for first run

        if (
            current_millis - self.lastMqttPublishTeleMillis
            > self.mqttPublishTeleIntervalMillis
        ) or (self.lastMqttPublishTeleMillis == -1):
            logger.warning("---> publish MQTT TELE info")

            MQTTClient.publish(
                self.zoneName + "/vent_on_delta_secs",
                int(cfg.getItemValueFromConfig("ventOnDelta") / 1000),
            )
            MQTTClient.publish(
                self.zoneName + "/vent_off_delta_secs",
                int(cfg.getItemValueFromConfig("ventOffDelta") / 1000),
            )
            # repeat for vent_on_delta_dark_secs and vent_off_delta_dark_secs
            MQTTClient.publish(
                self.zoneName + "/vent_on_delta_dark_secs",
                int(cfg.getItemValueFromConfig("ventDarkOnDelta") / 1000),
            )
            MQTTClient.publish(
                self.zoneName + "/vent_off_delta_dark_secs",
                int(cfg.getItemValueFromConfig("ventDarkOffDelta") / 1000),
            )

            MQTTClient.publish(
                self.zoneName + "/low_setpoint",
                cfg.getItemValueFromConfig("tempSPLOff"),
            )
            MQTTClient.publish(
                self.zoneName + "/high_setpoint",
                cfg.getItemValueFromConfig("tempSPLOn"),
            )

            lightState = ctl1.light.getLightState()
            MQTTClient.publish(self.zoneName + "/LightStatus", lightState)
            logger.warning("===---> " + self.zoneName + "/LightStatus : ")
            MQTTClient.publish(self.zoneName + "/version", VERSION)

            logger.warning(
                "===---> "
                + self.zoneName
                + "/vent_on_delta_secs : "
                + str(int(cfg.getItemValueFromConfig("ventOnDelta") / 1000))
            )
            logger.warning(
                "===---> "
                + self.zoneName
                + "/vent_off_delta_secs : "
                + str(int(cfg.getItemValueFromConfig("ventOffDelta") / 1000))
            )

            logger.warning(
                "===---> "
                + self.zoneName
                + "/vent_on_delta_dark_secs : "
                + str(int(cfg.getItemValueFromConfig("ventDarkOnDelta") / 1000))
            )
            logger.warning(
                "===---> "
                + self.zoneName
                + "/vent_off_delta_dark_secs : "
                + str(int(cfg.getItemValueFromConfig("ventDarkOffDelta") / 1000))
            )

            # logger.warning('==-> ' + zone + "/LWT:" + "Online")
            logger.warning("===---> " + self.zoneName + "/version : " + VERSION)

            MQTTClient.publish(self.zoneName + "/rssi", self.getRSSI())
            MQTTClient.publish(self.zoneName + "/LWT", "Online", 0, True)
            self.lastMqttPublishTeleMillis = current_millis
            # anyChanges = True

    #! support routines
    # get rssi

    def getRSSI(self):
        rssi = ""
        try:
            wifn = socket.if_nameindex()[2][1]
            proc = subprocess.Popen(
                ["iwconfig", wifn], stdout=subprocess.PIPE, universal_newlines=True
            )
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
