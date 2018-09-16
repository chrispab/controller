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
import sendemail as emailMe

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

# import tornado.httpserver
# import tornado.websocket
# import tornado.ioloop
# import tornado.web
# import socket

# import RF24

import asyncio

# import multiprocessing
import random

# import websocketserver
import websockets


Broker = "192.168.0.200"

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

# import websocketserver
# from websocketserver import clients
# from websocketserver import send_to_all_clients


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
        # start the c watchdog
        # logger.warning("WWWWW starting my_watchdog WWWWW")
#        os.system("sudo ./watchdog/my_watchdog &")
        # os.system("sudo ./watchdog/my_watchdog -r &")

        # subprocess.call(["sudo","./watchdog/my_watchdog"])

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


# while True:
#    sensor_data = [read_temp(), read_humidity(), read_pressure()]
#    client.publish("monto/solar/sensors", str(sensor_data))
#    time.sleep(1*60)
##################################################

'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes.
'''

# class WSHandler(tornado.websocket.WebSocketHandler):
#     def open(self):
#         print ('new connection')

#     def on_message(self, message):
#         print ('message received:  %s' % message)
#         # Reverse Message and send it back
#         print ('sending back message: %s' % message[::-1])
#         self.write_message(message[::-1])

#     def on_close(self):
#         print ('connection closed')

#     def check_origin(self, origin):
#         return True

# application = tornado.web.Application([
#     (r'/ws', WSHandler),
# ])
# cfg.


# !MQTT stuff - handlers etc
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(sub_topic)

# when receiving a mqtt message do this;


def on_message(client, userdata, msg):
    message = str(msg.payload)
    print(msg.topic+" "+message)
    # display_sensehat(message)


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(sub_topic)

# import websocketserver


async def control():

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(Broker, 1883, 60)
    client.loop_start()

    # call to systemd watchdog to hold off restart
    ctl1.timer1.holdOffWatchdog(0, True)

    start_time = time.time()
    humidity, temperature, sensorMessage = ctl1.sensor1.read()

    global systemUpTime
    global processUptime
    global systemMessage
    global controllerMessage
    global miscMessage
    global emailzone

    # TODO ENABLE EMAIL ENABLED OBEY
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
    row = 11
    while 1:
        # tornado.ioloop.IOLoop.instance().loop()

        logger.info("=main while loop=")
        # logger.warning("== process uptime: %s =",processUptime)

        # logger.debug(socket.gethostname())
        logger.info("current time: %s" % (ctl1.timer1.current_time))
        ctl1.timer1.updateClocks()
        current_millis = ctl1.timer1.current_millis

        # call to systemd watchdog to hold off restart
        ctl1.timer1.holdOffWatchdog(current_millis)

        # hold off wireless arduino watchdog
        # check radio link for a ping from Arduino watchdog, and respond to indicate alive
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
            # logger.error("^^^^^^^^^^  Aquisition sampletime: %d ^^^^^^^^^^^", duration)

            sensor_data = [str(temperature), str(humidity), str(lightState)]
            # , sensor_data)
            logger.warning("========== start publish MQTT messages...")
            client.publish(zone+"/TemperatureStatus", temperature)
            client.publish(zone+"/HumidityStatus", humidity)
            client.publish(zone+"/HeaterStatus", heaterState)

            client.publish(zone+"/VentStatus", ventState)
            client.publish(zone+"/FanStatus", fanState)
            client.publish(zone+"/VentSpeedStatus", ventSpeedState)
            client.publish(zone+"/LightStatus", lightState)
            logger.warning("============= MQTT sendt=")  # , sensor_data)

            # print("->")
            logger.debug("======== start state changed main list ======")
            # check for alarm levels etc
            if temperature > cfg.getItemValueFromConfig('tempAlertHi'):
                try:
                    emailObj.send(zone + ' - Hi Temp warning' +
                                  temperature, message)
                except:
                    logger.error("...ERROR SENDING EMAIL - for hi temp alert")

            if temperature < cfg.getItemValueFromConfig('tempAlertLo'):
                try:
                    emailObj.send(zone + ' - Lo Temp warning' +
                                  temperature, message)
                except:
                    logger.error("...ERROR SENDING EMAIL - low temp alert")

            location = cfg.getItemValueFromConfig('locationDisplayName')
            logger.debug("LLLLLLLLLL - loc : %s" % (location))

            end_time = time.time()
            processUptime = end_time - start_time
            processUptime = str(timedelta(seconds=int(processUptime)))
            # cfg.setConfigItemInLocalDB('processUptime', "Process Up Time: " +processUptime)
            cfg.setConfigItemInLocalDB('processUptime', processUptime)

            systemUpTime = ctl1.timer1.getSystemUpTimeFromProc()
            # cfg.setConfigItemInLocalDB('systemUpTime',  "System Up Time: " + systemUpTime)
            cfg.setConfigItemInLocalDB('systemUpTime', systemUpTime)

            cfg.setConfigItemInLocalDB('miscMessage', location)

            # systemMessage = ctl1.timer1.getUpTime().strip()
            cfg.setConfigItemInLocalDB('systemMessage', systemMessage)

            ipAddress = get_ip_address()
            cfg.setConfigItemInLocalDB('controllerMessage', "V: " + VERSION + ", IP: " + "<a href=" +
                                       "https://" + ipAddress + ":10000" + ' target="_blank"' + ">" + ipAddress + "</a>")

            cfg.setConfigItemInLocalDB('lightState', int(lightState))

            # time1 = datetime.datetime.now()
            # cfg.updateCentralConfigTable()
            # time2 = datetime.datetime.now()
            # duration = time2 - time1
            # logger.warning("TTTTT - update central CONFIG table duration : %s" % (duration))

            execAndTimeFunc(cfg.updateCentralConfigTable)

            # uptime = cfg.getConfigItemFromLocalDB('processUptime')
            logger.info("======== process uptime: %s ======", processUptime)
            mem = psutil.virtual_memory()
            # logger.warning("MMMMMM total memory       : %s MMMMMM",mem.total)

            # logger.warning("MMMMMM memory available   : %s MMMMMM",mem.available)
            logger.debug("MMMMMM memory pc.available: %0.2f MMMMMM",
                         ((float(mem.available)/float(mem.total)))*100)
            # logger.warning("======== % memory available: %s ======",mem.percent)

            data = systemUpTime
            currentStatusString = ctl1.stateMonitor.getStatusString()
            currentStatusString = currentStatusString + \
                ", " + str(lightState)

            logger.warning(
                "==== DATA message to send: %s ====", currentStatusString)

            if row >= 15:
                header = "<samp style='white-space:pre;'>Timestamp               T     H     H  V  F  S  L</samp>"
                await txwebsocket(header)
                row = 0
            row = row + 1

            await txwebsocket("<samp style='white-space:pre;'>" + currentStatusString + "</samp>")
            await asyncio.sleep(0)


async def txwebsocket(message):
    global proxysock
    if proxysock is None:
        logger.warning("======== NO OPEN SOCKETS - DATA NOT SENT=================")
    else:
        await proxysock.send(message)
        logger.warning("======== DATA SENT to websocket =================")
    await asyncio.sleep(0)


async def mytime(websocket, path):
    global proxysock
    proxysock = websocket
    logger.warning("CCCCCC CONNECTION MADE CCCCCC")
    #now = str(datetime.datetime.now())
    now = "websocket server connected on " + \
        cfg.getItemValueFromConfig('zoneName')
    await websocket.send(now)

    header = "<samp style='white-space:pre;'>Timestamp               T     H     H  V  F  S  L</samp>"
    await websocket.send(header)
    
    while True:
        await asyncio.sleep(30)

proxysock = None


async def main():
    start_server = websockets.serve(mytime, '', 5678)
    #mywebapp= web.run_app(app)



    server = web.Server(hello)
    await asyncio.get_event_loop().create_server(server, "", 8081)
    print("======= Serving on http://127.0.0.1:8080/ ======")
    # pause here for very long time by serving HTTP requests and
    # waiting for keyboard interruption
    #await asyncio.sleep(100*3600)


    tasks = [control(), start_server]
    #web.run_app(app)
    await asyncio.gather(*tasks)


#==============================
from aiohttp import web

async def hello(request):
    #return web.Response(text="Hello, world")
    return web.FileResponse('websocketTests/zones.html')



app = web.Application()
app.add_routes([web.get('/', hello)])

#web.run_app(app)


#===================================


if __name__ == "__main__":
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(main())
    ioloop.close()
