#!/usr/bin/env python
# control.py
# control for HVAC controller

from services.MessageService import MessageService
from services.telemetryService import TelemetryService
from aiohttp import web
import version
from componentClasses import *  # components of controller board
from support import round_time as round_time
import hardware as hw
from ConfigObject import cfg  # singleton global
from DatabaseObject import db  # singleton global
import os
import subprocess
import RPi.GPIO as GPIO
import pprint
from Logger import Logger
from myemail import MyEmail
import json
import requests  # allows us to send HTML POST request to IFTTT
import websockets
import random
import asyncio
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import socket  # to get hostname
import sys    # for stdout print
import datetime as dt
import yaml
from datetime import timedelta
import time
import datetime
import csv
from version import VERSION
import logging
# logger options
###############
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)
#
logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
# logging.basicConfig(format='[%(filename)s:%(lineno)s - %(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
# logging.basicConfig(format='[%(funcName)s() ]%(levelname)s:%(asctime)s %(message)s', level=logging.WARNING)
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s',filename='myenvctl.log', filemode='w', level=logging.DEBUG)
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', filename='myenvctl.log', filemode='w',level=logging.WARNING)
# logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

# ===================general imports=====================================

#! import services


MQTTBroker = "192.168.0.100"
# sub_topic = "/zone1/instructions"    # receive messages on this topic
# pub_topic = "/zone1/data"       # send messages to this topic


logger = logging.getLogger(__name__)


# my singleton objects


OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on

path = cfg.getItemValueFromConfig('dataPath')

processUptime = 0
systemMessage = 0
emailzone = ""
zoneNumber = 0
outsideTemp = 12


# ============================common code start==========================


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
    except:
        logger.error("????? cant get a network socket ?????")
        e = sys.exc_info()[0]
        logger.error("????? Error: %s ?????" % e)
        return "cant get socket"
    return s.getsockname()[0]


def execAndTimeFunc(func):
    time1 = datetime.datetime.now()
    func()
    time2 = datetime.datetime.now()
    duration = time2 - time1
    logger.debug("execute and time a function: %s, duration: %s" %
                 (func, duration))


class Controller(object):

    def __init__(self):
        logger.info("init controller")
        logger.info("---Creating system Objects---")
        self.board1 = hw.platform()
        self.sensor1 = hw.sensor()
        self.vent1 = Vent()
        self.heater1 = Heater()
        self.fan1 = Fan()
        self.light = Light()
        self.radioLink1 = RadioLink()
        self.stateMonitor = Logger()
        self.timer1 = system_timer()


# main routine
#############

logger.info("--- Creating the controller---")
ctl1 = Controller()
emailObj = MyEmail()

# ! set up serviuces to use
teleService = TelemetryService()
MessageService = MessageService()


def on_connect(MQTTClient, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    logger.warning(" - MQTT CONNECTED - MMMMM")
    # MQTTClient.subscribe(sub_topic)
    zoneName = cfg.getItemValueFromConfig('zoneName')

    MQTTClient.subscribe("Outside_Sensor/tele/SENSOR")
    MQTTClient.subscribe(zoneName+"/vent_off_delta_secs/set")
    MQTTClient.subscribe(zoneName+"/vent_on_delta_secs/set")
    MQTTClient.subscribe(zoneName+"/low_setpoint/set")
    MQTTClient.subscribe(zoneName+"/high_setpoint/set")

# when receiving a mqtt message do this;
def on_message(MQTTClient, userdata, msg):

    global outsideTemp


    message = str(msg.payload.decode("utf-8"))    
    logger.warning("MMMMMM: subscibed message rxed topic : %s" % (msg.topic))    
    logger.warning("MMMMMM: subscibed message rxed payload : %s" % (message))    
    # logger.warning("subscribed message rxed : %s" % str(message)) )

    zoneName = cfg.getItemValueFromConfig('zoneName')
    logger.warning("MMMMMM: subscibed message rxedm, zone name used : %s" % (zoneName))    

    # logger.warning(" MRMRMRMRMR- MQTT rx - MRMRMRMRMRMRMRMRMRMR")

    # logger.warning("sub message rxed : %s" % str(message.payload.decode("utf-8")) )
    data = json.loads(message)
    outSideTempSensor = cfg.getItemValueFromConfig('outSideTempSensor')
    try:
        outsideTemp = data[outSideTempSensor]['Temperature']
    except:
        logger.error(
            "<====---- outside temp mqtt in temp error redoing payload")

    logger.warning(
        "<====---- subscibed message rxed from outside sensor: %s" % (outsideTemp))

    logger.warning(msg.topic+" :: "+message)
    logger.warning(zoneName + "/vent_on_delta_secs/set!!!" +
                   " ::: " + msg.topic+" :: "+message)

    # vent deltas
    if msg.topic == (zoneName + "/vent_on_delta_secs/set"):
        # vent on time rxed in secs, convert to ms - used in code
        cfg.setItemValueToConfig('ventOnDelta', int(msg.payload)*1000)
        logger.warning(zoneName + "/vent_on_delta_secs/set!!!")
        cfg.writeConfigToFile()

    if msg.topic == (zoneName + "/vent_off_delta_secs/set"):
        cfg.setItemValueToConfig('ventOffDelta', int(
            msg.payload)*1000)  # vent on time
        logger.warning(zoneName + "/vent_off_delta_secs/set!!!")
        cfg.writeConfigToFile()
    
    # setpoints
    if msg.topic == (zoneName + "/low_setpoint/set"):
        cfg.setItemValueToConfig('tempSPLOff', float(msg.payload))
        logger.warning(zoneName + "/low_setpoint/set!!!")
        cfg.writeConfigToFile()

    if msg.topic == (zoneName + "/high_setpoint/set"):
        cfg.setItemValueToConfig('tempSPLOn', float(msg.payload))  # vent on time
        logger.warning(zoneName + "/high_setpoint/set!!!")
        cfg.writeConfigToFile()


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
# EMQTT



#
async def control():

    # global systemUpTime
    # global processUptime
    # global systemMessage
    # global controllerMessage
    # global miscMessage
    global emailzone
    # global outsideTemp

    # logger.warning("MQTT CANNOT CONNECT!!!")

    # print("MQTT CANNOT CONNECT!!!")

    try:
        MQTTClient = mqtt.Client()
    except:
        print("MQTT CANNOT CONNECT!!!")

    MQTTClient.on_connect = on_connect
    MQTTClient.on_message = on_message
    try:
        #    MQTTClient.will_set(zoneName + "/LWT", "Offline", 0, True)
        zoneName = cfg.getItemValueFromConfig('zoneName')
        MQTTClient.will_set(zoneName+"/LWT", "Offline", 0, False)

        MQTTClient.connect(MQTTBroker, 1883, 60)

        # MQTTClient.subscribe("Outside_Sensor/tele/SENSOR")
        # MQTTClient.subscribe(zoneName+"/vent_off_delta_secs/set")
        # MQTTClient.subscribe(zoneName+"/vent_on_delta_secs/set")

        MQTTClient.loop_start()
    except:
        print("MQTT CANNOT CONNECT!!!")
    print("Subscribing to topic", "Outside_Sensor/tele/SENSOR")

    # call to systemd watchdog to hold off restart
    ctl1.timer1.holdOffWatchdog(0, True)

    # start_time = time.time()
    humidity, temperature, sensorMessage = ctl1.sensor1.read()

    zoneName = cfg.getItemValueFromConfig('zoneName')
    zoneNumber = cfg.getItemValueFromConfig('zoneNumber')
    location = cfg.getItemValueFromConfig('locationDisplayName')
    mqttPublishIntervalMillis = cfg.getItemValueFromConfig(
        'mqttPublishIntervalMillis')
    # mqttPublishTeleIntervalMillis = cfg.getItemValueFromConfig('mqttPublishTeleIntervalMillis')
    lastMqttPublishHeartBeatMillis = ctl1.timer1.current_millis - 50000
    # lastMqttPublishTeleMillis = ctl1.timer1.current_millis - 100000

    ackMessage = cfg.getItemValueFromConfig('ackMessage')

#    MQTTClient.will_set(zoneName + "/LWT", "Offline", 0, True)
    # publish(topic, payload=None, qos=0, retain=False)
    MQTTClient.publish(zoneName + "/LWT", "Online", 0, True)

    message = zoneName
    # if just booted
    if ctl1.timer1.secsSinceBoot() < 120:
        emailzone = "Zone " + zoneNumber + ' REBOOTED '

    # emailMe.sendemail( zoneName + ' ' + location + ' - Process Started', message)
    emailObj.send("Zone " + zoneNumber + " " + emailzone +
                  location + ' - Controller Process Started', message)

    # # Your IFTTT with event name, and json parameters (values)
    # postIFTTT("zone_alert", zoneName, "--ReasoN--", "==DatA==")

    maxWSDisplayRows = 5  # ! TODO FIX THIS - display issue
    currentWSDisplayRow = 1

    # ! publish all I/O to broker on start up
    logger.warning("----+++====  SENDING INITIAL MQTT ===+++++-------")

    lightState = ctl1.light.getLightState()
    heaterState = ctl1.heater1.state
    ventState = ctl1.vent1.state
    fanState = ctl1.fan1.state
    ventSpeedState = ctl1.vent1.speed_state
    humidity, temperature, sensorMessage = ctl1.sensor1.read()

    MQTTClient.publish(zoneName+"/HeartBeat", ackMessage)
    MQTTClient.publish(zoneName+"/TemperatureStatus", temperature)
    MQTTClient.publish(zoneName+"/HumidityStatus", humidity)
    MQTTClient.publish(zoneName+"/FanStatus", fanState)
    MQTTClient.publish(zoneName+"/VentStatus", ventState)
    MQTTClient.publish(zoneName+"/HeaterStatus", heaterState)
    MQTTClient.publish(zoneName+"/VentSpeedStatus", ventSpeedState)
    MQTTClient.publish(zoneName+"/VentValue", ventState + ventSpeedState)
    ventPercent = ventState*((ventSpeedState+1)*50)
    MQTTClient.publish(zoneName+"/VentPercent", ventPercent)

    MQTTClient.publish(zoneName+"/LightStatus", lightState)
    # MQTTClient.publish(zoneName+"/VentPercent", ventPercent)

    while 1:
        logger.info("=main while loop=")
        logger.info("current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.updateClocks()
        current_millis = ctl1.timer1.current_millis

        #! send telemetry periodically
        teleService.pubMQTTTele(current_millis, MQTTClient)
        teleService.pubMQTTHeartBeat(current_millis, MQTTClient)

        # if !MQTTClient.connected:
        #     MQTTClient.connect(MQTTBroker, 1883, 60)

        # call to systemd watchdog to hold off restart
        ctl1.timer1.holdOffWatchdog(current_millis)

        # hold off wireless watchdog
        # check radio link for a ping from watchdog, and respond to indicate alive
        ctl1.radioLink1.holdOffWatchdog()

        await asyncio.sleep(0)

        # startT = time.time()

        humidity, temperature, sensorMessage = ctl1.sensor1.read()
        if sensorMessage:
            subject = "Zone " + zoneNumber + " " + emailzone + \
                location + " - : bad sensor reads  - PowerCycle"
            emailObj.send(subject, sensorMessage)

        # endT = time.time()
        # duration = endT-startT

        # get all current states
        lightState = ctl1.light.getLightState()
        heaterState = ctl1.heater1.state
        ventState = ctl1.vent1.state
        fanState = ctl1.fan1.state
        ventSpeedState = ctl1.vent1.speed_state

        if lightState == ON:
            logger.info('=LOn=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOn')
        else:  # off
            logger.info('=LOff=')
            target_temp = cfg.getItemValueFromConfig('tempSPLOff')
        logger.debug(target_temp)

        ctl1.fan1.control(current_millis)
        ctl1.vent1.control(temperature, humidity, target_temp,
                           lightState, current_millis)


        # ctl1.heater1.controlv2(temperature, target_temp,
        #                        lightState, current_millis, outsideTemp)

        ctl1.heater1.control(temperature, target_temp,
                               lightState, current_millis, outsideTemp)
# 

        ctl1.fan1.control(current_millis)
        # switch relays according to State vars
        ctl1.board1.switch_relays(
            heaterState, ventState, fanState, ventSpeedState)


        anyChanges = teleService.pubMQTTReadings(MQTTClient, ctl1, humidity, temperature, lightState, heaterState, fanState, ventState, ventSpeedState)
        # # only send mqtt messages for the changed i/o - not all as previous message

        if anyChanges:
            currentStatusString = ctl1.stateMonitor.getDisplayStatusString()
            if currentWSDisplayRow >= maxWSDisplayRows:
                await txwebsocket(ctl1.stateMonitor.getDisplayHeaderString())
                currentWSDisplayRow = 0
            currentWSDisplayRow = currentWSDisplayRow + 1

            await txwebsocket(currentStatusString)
            await asyncio.sleep(0)

        stateChanged = ctl1.stateMonitor.checkForChanges(temperature, humidity, ventState,
                                                         fanState, heaterState, ventSpeedState, lightState,
                                                         current_millis, ctl1.timer1.current_time)  # write to csv/db etc if any state changes

        if stateChanged:
            logger.warning(
                ">>>>>>>>>>>>>>>>>>>>>>>QQQQ Publishing MQTT messages...")


            logger.debug("======== start state changed main list ======")
            # check for alarm levels etc
            MessageService.alertAbnormalTemps(temperature) # alert if abnormal temps

            location = cfg.getItemValueFromConfig('locationDisplayName')
            # logger.debug("Location : %s" % (location))

            # end_time = time.time()
            # processUptime = end_time - start_time
            # processUptime = str(timedelta(seconds=int(processUptime)))
            # cfg.setConfigItemInLocalDB('processUptime', processUptime)
            systemUpTime = ctl1.timer1.getSystemUpTimeFromProc()
            # cfg.setConfigItemInLocalDB('systemUpTime', systemUpTime)
            # cfg.setConfigItemInLocalDB('miscMessage', location)
            # cfg.setConfigItemInLocalDB('systemMessage', systemMessage)
            ipAddress = get_ip_address()
            # cfg.setConfigItemInLocalDB('controllerMessage', "V: " + VERSION + ", IP: " + "<a href=" +
            #                            "https://" + ipAddress + ":10000" + ' target="_blank"' + ">" + ipAddress + "</a>")
            # cfg.setConfigItemInLocalDB('lightState', int(lightState))
            # execAndTimeFunc(cfg.updateCentralConfigTable)

            logger.info("======== process uptime: %s ======", processUptime)
            mem = psutil.virtual_memory()
            # logger.warning("MMMMMM total memory       : %s MMMMMM",mem.total)

            # logger.warning("MMMMMM memory available   : %s MMMMMM",mem.available)
            logger.debug("MMMMMM memory pc.available: %0.2f MMMMMM",
                         ((float(mem.available)/float(mem.total)))*100)
            # logger.warning("======== % memory available: %s ======",mem.percent)

            currentStatusString = ctl1.stateMonitor.getDisplayStatusString()
            # currentStatusString = currentStatusString + \
            #     ", " + str(lightState)

            logger.warning(
                "DATA to send:%s", currentStatusString)


wsClients = set()


async def txwebsocket(message):
    removeMe = False
    for clientConn in wsClients:
        logger.warning("DDDD Sending DATA SENT to websocket(s)")
        # logger.warning(clientConn)
        try:
            if clientConn.open:
                await asyncio.wait([clientConn.send(message)])
                # await clientConn.send(message)

                logger.info("EEEE message sent to ws Client EEEE")
            else:  # websockets.ConnectionClosed:
                logger.warning("UUUU1 unregging a wsconn UUUU")
                removeMe = clientConn
                # await unregister(clientConn)
                # wsClients.remove(clientConn)
        except:
            logger.warning("UUUU2 unregging a wsconn UUUU")
            # await unregister(clientConn)
            removeMe = clientConn

    # if wsocket marked for removal
    if removeMe:
        wsClients.remove(removeMe)
        # await unregister(clientConn)
    return


async def register(websocket):
    wsClients.add(websocket)


async def unregister(websocket):
    wsClients.remove(websocket)


async def MyWSHandler(websocket, path):
    wsClients.add(websocket)

    logger.warning("CCCCCC CONNECTION MADE CCCCCC")
    # now = str(datetime.datetime.now())
    initialMessage = "websocket server connected from " + \
        cfg.getItemValueFromConfig('zoneName')

    initialMessage = "Version : " + VERSION
    await websocket.send(initialMessage)
    # header = "Timestamp               T     H     H  V  F  S  L  VT"
    await websocket.send(ctl1.stateMonitor.getDisplayHeaderString())

    # try ping socket # if response cont
    # if no response remove websocket from set
    while True:
        try:
            msg = await asyncio.wait_for(websocket.recv(), timeout=20)
            # logger.warning("WS RX message : %s", msg)
            logger.warning("WS RX message")
        except asyncio.TimeoutError:
            # No data in 20 seconds, check the connection.
            try:
                logger.warning(
                    "No data in 20 secs from client- checking connection")
                # await unregister(websocket)
                # break
                pong_waiter = await websocket.ping()
                await asyncio.wait_for(pong_waiter, timeout=10)
                logger.warning("PPPPP ping rxed - client aliveb PPPP")
            except:  # asyncio.TimeoutError:
                # No response to ping in 10 seconds, disconnect.
                logger.warning(
                    "RRRR no ping response - Remove dead client websocet RRRR")

                await unregister(websocket)
                break
        else:
            logger.warning(
                "msg RXED from client - still connected do nothing")

        # do something with msg?
    logger.warning("DDDDD drop our of onConnect handler DDDDDD")


async def main():
    start_server = websockets.serve(MyWSHandler, '', 5678)
    # mywebapp= web.run_app(app)

    server = web.Server(serveConsolePage)
    await asyncio.get_event_loop().create_server(server, "", 8081)
    print("======= Serving on http://127.0.0.1:8080/ ======")
    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    # await asyncio.sleep(100*3600)

    tasks = [control(), start_server]
    # web.run_app(app)
    await asyncio.gather(*tasks)


# ==============================


async def serveConsolePage(request):
    # return web.Response(text="serveConsolePage, world")
    return web.FileResponse('websocketTests/zones.html')


app = web.Application()
app.add_routes([web.get('/', serveConsolePage)])


# ===================================
if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
