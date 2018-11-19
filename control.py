#!/usr/bin/env python
# control.py
# control for HVAC controller

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

from version import VERSION
# ===================general imports=====================================

import csv
import datetime
import time
from datetime import timedelta
import yaml
import datetime as dt
import sys    # for stdout print
import socket  # to get hostname
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import asyncio
import random
import websockets
import requests  # allows us to send HTML POST request to IFTTT

MQTTBroker = "192.168.0.200"
sub_topic = "/zone1/instructions"    # receive messages on this topic
pub_topic = "/zone1/data"       # send messages to this topic

from myemail import MyEmail
from Logger import Logger
import pprint


logger = logging.getLogger(__name__)

import RPi.GPIO as GPIO
import subprocess
import os


# my singleton objects
from DatabaseObject import db  # singleton global
from ConfigObject import cfg  # singleton global

import hardware as hw
from support import round_time as round_time

OFF = cfg.getItemValueFromConfig('RelayOff')  # state for relay OFF
ON = cfg.getItemValueFromConfig('RelayOn')  # state for on

path = cfg.getItemValueFromConfig('dataPath')

processUptime = 0
systemMessage = 0
emailzone = ""
zoneNumber = 0


from componentClasses import *  # components of controller board

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


# !MQTT stuff - handlers etc
def on_connect(MQTTClient, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    logger.warning("MMMMM - MQTT CONNECTED - MMMMM")
    MQTTClient.subscribe(sub_topic)

# when receiving a mqtt message do this;


def on_message(MQTTClient, userdata, msg):
    message = str(msg.payload)
    print(msg.topic+" "+message)
    # display_sensehat(message)


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
# EMQTT

# IFTTT


def postIFTTT(event_name, val1, val2, val3):
    #event_name = "zone_alert"
    #val1 = zone
    #val2 = "-Reason-"
    #val3 = "=Data="
    iftttUrl = "https://maker.ifttt.com/trigger/" + \
        event_name+"/with/key/dF1NEy_aQ5diUyluM3EKcd"
    r = requests.post(iftttUrl, params={
                      "value1": val1, "value2": val2, "value3": val3})

    #r = requests.post("https://maker.ifttt.com/trigger/zone_alert/with/key/dF1NEy_aQ5diUyluM3EKcd", params={"value1":zone,"value2":"REASON","value3":"DATA"})

# _IFTTT


async def control():

    global systemUpTime
    global processUptime
    global systemMessage
    global controllerMessage
    global miscMessage
    global emailzone

    MQTTClient = mqtt.Client()
    MQTTClient.on_connect = on_connect
    MQTTClient.on_message = on_message
    MQTTClient.connect(MQTTBroker, 1883, 60)
    MQTTClient.loop_start()

    # call to systemd watchdog to hold off restart
    ctl1.timer1.holdOffWatchdog(0, True)

    start_time = time.time()
    humidity, temperature, sensorMessage = ctl1.sensor1.read()

    zone = cfg.getItemValueFromConfig('zoneName')
    zoneNumber = cfg.getItemValueFromConfig('zoneNumber')
    location = cfg.getItemValueFromConfig('locationDisplayName')
    message = zone
    # if just booted
    if ctl1.timer1.secsSinceBoot() < 120:
        emailzone = "Zone " + zoneNumber + ' REBOOTED '

    # emailMe.sendemail( zone + ' ' + location + ' - Process Started', message)
    emailObj.send("Zone " + zoneNumber + " " + emailzone +
                  location + ' - Process Started', message)

    # # Your IFTTT with event name, and json parameters (values)
    postIFTTT("zone_alert", zone, "--ReasoN--", "==DatA==")

    maxWSDisplayRows = 10  # ! TODO FIX THIS - display issue
    currentWSDisplayRow = 1
    while 1:
        logger.info("=main while loop=")
        logger.info("current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.updateClocks()
        current_millis = ctl1.timer1.current_millis

        # call to systemd watchdog to hold off restart
        ctl1.timer1.holdOffWatchdog(current_millis)

        # hold off wireless watchdog
        # check radio link for a ping from watchdog, and respond to indicate alive
        ctl1.radioLink1.holdOffWatchdog()

        await asyncio.sleep(0)

        startT = time.time()
        humidity, temperature, sensorMessage = ctl1.sensor1.read()
        if sensorMessage:
            subject = "Zone " + zoneNumber + " " + emailzone + \
                location + " - : bad sensor reads  - PowerCycle"
            emailObj.send(subject, sensorMessage)
        endT = time.time()
        duration = endT-startT
        # logger.error("^^^^^^^^^^  Aquisition sampletime: %s ^^^^^^^^^^^", duration)

        # get all states
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
        ctl1.vent1.control(temperature, target_temp,
                           lightState, current_millis)
        ctl1.heater1.control(temperature, target_temp,
                             lightState, current_millis)
        ctl1.fan1.control(current_millis)
        # switch relays according to State vars
        ctl1.board1.switch_relays(
            heaterState, ventState, fanState, ventSpeedState)
        stateChanged = ctl1.stateMonitor.checkForChanges(temperature, humidity, ventState,
                                                         fanState, heaterState, ventSpeedState,
                                                         current_millis, ctl1.timer1.current_time)  # write to csv/db etc if any state changes
        if stateChanged:
            logger.warning("QQQQ Publishing MQTT messages...")
            MQTTClient.publish(zone+"/TemperatureStatus", temperature)
            MQTTClient.publish(zone+"/HumidityStatus", humidity)
            MQTTClient.publish(zone+"/HeaterStatus", heaterState)
            MQTTClient.publish(zone+"/VentStatus", ventState)
            MQTTClient.publish(zone+"/FanStatus", fanState)
            MQTTClient.publish(zone+"/VentSpeedStatus", ventSpeedState)
            MQTTClient.publish(zone+"/LightStatus", lightState)

            logger.debug("======== start state changed main list ======")
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

            location = cfg.getItemValueFromConfig('locationDisplayName')
            #logger.debug("Location : %s" % (location))

            end_time = time.time()
            processUptime = end_time - start_time
            processUptime = str(timedelta(seconds=int(processUptime)))
            cfg.setConfigItemInLocalDB('processUptime', processUptime)
            systemUpTime = ctl1.timer1.getSystemUpTimeFromProc()
            cfg.setConfigItemInLocalDB('systemUpTime', systemUpTime)
            cfg.setConfigItemInLocalDB('miscMessage', location)
            cfg.setConfigItemInLocalDB('systemMessage', systemMessage)
            ipAddress = get_ip_address()
            cfg.setConfigItemInLocalDB('controllerMessage', "V: " + VERSION + ", IP: " + "<a href=" +
                                       "https://" + ipAddress + ":10000" + ' target="_blank"' + ">" + ipAddress + "</a>")
            cfg.setConfigItemInLocalDB('lightState', int(lightState))
            execAndTimeFunc(cfg.updateCentralConfigTable)

            logger.info("======== process uptime: %s ======", processUptime)
            mem = psutil.virtual_memory()
            # logger.warning("MMMMMM total memory       : %s MMMMMM",mem.total)

            # logger.warning("MMMMMM memory available   : %s MMMMMM",mem.available)
            logger.debug("MMMMMM memory pc.available: %0.2f MMMMMM",
                         ((float(mem.available)/float(mem.total)))*100)
            # logger.warning("======== % memory available: %s ======",mem.percent)

            currentStatusString = ctl1.stateMonitor.getStatusString()
            currentStatusString = currentStatusString + \
                ", " + str(lightState)

            logger.warning(
                "==== DATA message to send: %s ====", currentStatusString)

            if currentWSDisplayRow >= maxWSDisplayRows:
                header = "Timestamp               T     H     H  V  F  S  L"
                await txwebsocket(header)
                currentWSDisplayRow = 0
            currentWSDisplayRow = currentWSDisplayRow + 1

            await txwebsocket(currentStatusString)
            await asyncio.sleep(0)


wsClients = set()


async def txwebsocket(message):
    removeMe = False
    for clientConn in wsClients:
        logger.warning("DDDD Sending DATA SENT to websocket(s)")
        logger.warning(clientConn)
        try:
            if clientConn.open:
                await asyncio.wait([clientConn.send(message)])
                # await clientConn.send(message)

                logger.warning("EEEE message sent to wdClient EEEE")
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
    #now = str(datetime.datetime.now())
    initialMessage = "websocket server connected on " + \
        cfg.getItemValueFromConfig('zoneName')

    await websocket.send(initialMessage)
    header = "Timestamp               T     H     H  V  F  S  L"
    await websocket.send(header)

    # try ping socket # if response cont
    # if no response remove websocket from set
    while True:
        try:
            msg = await asyncio.wait_for(websocket.recv(), timeout=20)
            logger.warning("SSSS RXED message is: %s ", msg)
        except asyncio.TimeoutError:
            # No data in 20 seconds, check the connection.
            try:
                logger.warning(
                    "NNNN No data in 20 secs from client- checking the connection NNNN")
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
                "RRRR msg RXED from client - still connected so do nothing")

        # do something with msg?
    logger.warning("DDDDD drop our of onConnect handler DDDDDD")


async def main():
    start_server = websockets.serve(MyWSHandler, '', 5678)
    #mywebapp= web.run_app(app)

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
from aiohttp import web


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
