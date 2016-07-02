from flask import Flask, render_template, request, jsonify, Markup
#from threading import Thread
import thread
from datetime import datetime
from datetime import timedelta

import control as ctl
from bisect import bisect_left
from bisect import bisect_right

from csv import reader
import pdb

app = Flask(__name__)

relays = {
         5:{'name':'heaterRelay','state':False},
         6:{'name':'ventRelay','state':True},
         7:{'name':'fanRelay','state':False},
         8:{'name':'relay4','state':False}
        }


def getStartSampleIndex(timeList, targetTimeDelta):
    lastSampleDTO = datetime.strptime(timeList[len(timeList)-1], '%Y-%m-%d %H:%M:%S')# conv to DTO from string format YYY-MM-DD HH:mm:ss
    reqStartDTO = lastSampleDTO - targetTimeDelta  #calc target DTO
    targetDateTimeStr = datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') #conv targetDTO to string format
    startSampleIndex = bisect_right(timeList, targetDateTimeStr)
    print "WEB Server - time delta: %s , sample index: %s oooooooo" % (targetTimeDelta, startSampleIndex)
    return startSampleIndex



@app.route("/multitall")
def multit():

    with open('/home/pi/projects/controller1/thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #listlen = len(data)
    startsample = 1

    labels = [i[0] for i in data[startsample::]]
    tempvalues = [i[1] for i in data[startsample::]]
    humivalues = [i[2] for i in data[startsample::]]
    heatervalues = [i[3] for i in data[startsample::]]
    ventvalues = [i[4] for i in data[startsample::]]
    fanvalues = [i[5] for i in data[startsample::]]

    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/chart/<float:timeh>")
def chartx(timeh):
    with open('/home/pi/projects/controller1/thdata.csv', 'r') as f:
        data = list(reader(f))
    timeList = [item[0] for item in data]
    del timeList[:0]    #del 1st element of list - start to elem 0
    startsample = getStartSampleIndex(timeList, timedelta( hours = timeh ))   #bisect_right(timeList, targetDateTimeStr)

    labels = [i[0] for i in data[startsample::]]
    tempvalues = [i[1] for i in data[startsample::]]
    humivalues = [i[2] for i in data[startsample::]]
    heatervalues = [i[3] for i in data[startsample::]]
    ventvalues = [i[4] for i in data[startsample::]]
    fanvalues = [i[5] for i in data[startsample::]]
    
    proctempvalues = [i[6] for i in data[startsample::]]
    timePeriod = timeh
    
    return render_template('multitc3.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels, proctempvalues=proctempvalues, timePeriod=timePeriod)


@app.route("/home")
def home():
    message = "Controller Status Page"
    
    #get relay states
    relays[5]['state'] = ctl.heaterState
    relays[6]['state'] = ctl.ventState
    relays[7]['state'] = ctl.fanState
    relays[8]['state'] = ctl.heaterState
            
    temp = ctl.temperature
    humi = ctl.humidity
     
    templateData = {
                'message' :  message ,
                'temp' : temp,
                'humi' : humi,
                'relays' : relays,
                'uptime' : GetUptime()
            }
    return render_template('temptest1.html',**templateData)
    
@app.route("/status")
def status():
    message = "Controller Status Page"
    
    relays[5]['state'] = ctl.heaterState
    relays[6]['state'] = ctl.ventState
    relays[7]['state'] = ctl.fanState
    relays[8]['state'] = ctl.heaterState
    
    temp = ctl.temperature
    humi = ctl.humidity
     
    templateData = {
                'message' :  message ,
                'temp' : temp,
                'humi' : humi,
                'relays' : relays,
                'uptime' : GetUptime()
            }
    return render_template('status.html',**templateData)
    
@app.route("/_getTemp")
def _getTemp():
    state = round(ctl.temperature, 1)
    print "STATE FOR TEMP AJAX", state
    return jsonify(tempRelayState=state)
    
@app.route("/_getHumi")
def _getHumi():
    state = round(ctl.humidity, 1)
    print "STATE FOR HUMI AJAX", state
    return jsonify(humiRelayState=state)
    
# ajax GET call this function periodically to read heater state
# the state is sent back as json data
@app.route("/_heaterRelay")
def _heaterRelay():
    if ctl.heaterState:
        state = "OFF"
    else:
        state = "ON"
    print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(heaterRelayState=state)
    
@app.route("/_ventRelay")
def _ventRelay():
    if ctl.ventState:
        state = "OFF"
    else:
        state = "ON"
    #print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(ventRelayState=state)
    
@app.route("/_fanRelay")
def _fanRelay():
    if ctl.fanState:
        state = "OFF"
    else:
        state = "ON"
    #print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(fanRelayState=state)
    
@app.route("/_fanSpeedRelay")
def _fanSpeedRelay():
    if ctl.relay4State:
        state = "LOW"
    else:
        state = "HIGH"
    #print "STATE FOR fan speed  RELAY AJAX", state
    return jsonify(fanSpeedRelayState=state)
    
        
# ajax GET call this function to set led state
# depeding on the GET parameter sent
@app.route("/_led")
def _led():
    state = request.args.get('state')
    if state=="on":
        ctl.relay4State = 0   #Pins.LEDon()
    else:
        ctl.relay4State = 1 #Pins.LEDoff()
    return ""


def GetUptime():
    # get uptime from the linux terminal command
    from subprocess import check_output
    output = check_output(["uptime"])
    # return only uptime info
    #uptime = output[output.find("up"):output.find("user")-5]
    uptime= output
    return uptime
    
def docontrol():
    while True:
        pass
        #print "DOCONTROL"
        ctl.main()


def start_web_server():
    # run the webserver on standard port 80, requires sudo
    app.run(host='0.0.0.0', debug=True, use_reloader=False, threaded=True)  


try:
   thread.start_new_thread( start_web_server, () )
   thread.start_new_thread( docontrol, () )
except:
   print "Error: unable to start thread"

while 1:
   pass   
