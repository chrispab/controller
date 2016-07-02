from flask import Flask, render_template, request, jsonify, Markup
#from threading import Thread
import thread
from datetime import datetime
from datetime import timedelta
import gpio
#import dht22
import control as ctl
from bisect import bisect_left
from bisect import bisect_right

from csv import reader
import pdb

app = Flask(__name__)

relays = {
         'gpio3':{'name':'heaterRelay','state':False},
         'gpio4':{'name':'ventRelay','state':True},
         'gpio5':{'name':'fanRelay','state':False},
         'gpio6':{'name':'relay4','state':False}
        }


def getStartSampleIndex(timeList, targetTimeDelta):
    lastSampleDTO = datetime.strptime(timeList[len(timeList)-1], '%Y-%m-%d %H:%M:%S')# conv to DTO from string format YYY-MM-DD HH:mm:ss
    reqStartDTO = lastSampleDTO - targetTimeDelta  #calc target DTO
    targetDateTimeStr = datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') #conv targetDTO to string format
    startSampleIndex = bisect_right(timeList, targetDateTimeStr)
    print "ooooooooooooooooooo %s ooooooooooooooooooooooooo" % startSample
    return startSampleIndex

@app.route("/multit_30")
def multit_30():  #1 hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')# conv to DTO from string format YYY-MM-DD HH:mm:ss
    reqStartDTO = lastSampleDT - timedelta(minutes=30)  #calc target DTO
    timeList = [item[0] for item in data]
    del timeList[:0]    #del 1st element of list - start to elem 0
    targetDateTimeStr = datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') #conv targetDTO to string format
    startSample = bisect_right(timeList, targetDateTimeStr)
    print "ooooooooooooooooooo %s ooooooooooooooooooooooooo" % startSample

    labels = [i[0] for i in data[startSample::]]
    tempvalues = [i[1] for i in data[startSample::]]
    humivalues = [i[2] for i in data[startSample::]]
    heatervalues = [i[3] for i in data[startSample::]]
    ventvalues = [i[4] for i in data[startSample::]]
    fanvalues = [i[5] for i in data[startSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)


@app.route("/multit1")
def multit1():  #1 hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 2hrs data
    #get last sample time stamp
    #convert string in CSV to datetime obhect
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')#in format YYY-MM-DD HH:mm:ss
    #print data[0][len(data)
    print lastSampleDT
    #raw_input("Press Enter to continue...")
    #scan thru label(timestamp) array to get sample that is at least 2hrs previous to last sample
    #calc start time string looking for for start of time frame sample
    reqStartDTO = lastSampleDT - timedelta(hours=1)
    
    timeList = [item[0] for item in data]
    #print timeList
    
    #thing_index = thing_list.index(elem) if elem in thing_list else -1
    while ( (timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) if datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') in timeList else -1) == -1 ):
    #while ( timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) == ValueError ):
        #inc value to check for in list
        reqStartDTO += timedelta(seconds=1)
        #print reqStartDTO
    #got valid entry time - exists in data list
    locOfStartSample = timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S'))
    #if error - not found, inc seconds and try again
    
    
    numsamples = 200
    listlen = len(data)
    #print hours
    #print listlen
    startsample = listlen - numsamples
    #print startsample
    #raw_input("Press Enter to continue...")

    labels = [i[0] for i in data[locOfStartSample::]]
    tempvalues = [i[1] for i in data[locOfStartSample::]]
    humivalues = [i[2] for i in data[locOfStartSample::]]
    heatervalues = [i[3] for i in data[locOfStartSample::]]
    ventvalues = [i[4] for i in data[locOfStartSample::]]
    fanvalues = [i[5] for i in data[locOfStartSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)


@app.route("/multit2")
def multit2():  #2 hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 2hrs data
    #get last sample time stamp
    #convert string in CSV to datetime obhect
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')#in format YYY-MM-DD HH:mm:ss
    #print data[0][len(data)
    print lastSampleDT
    #raw_input("Press Enter to continue...")
    #scan thru label(timestamp) array to get sample that is at least 2hrs previous to last sample
    #calc start time string looking for for start of time frame sample
    reqStartDTO = lastSampleDT - timedelta(hours=2)
    
    timeList = [item[0] for item in data]
    #print timeList
    
    #thing_index = thing_list.index(elem) if elem in thing_list else -1
    while ( (timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) if datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') in timeList else -1) == -1 ):
    #while ( timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) == ValueError ):
        #inc value to check for in list
        reqStartDTO += timedelta(seconds=1)
        print reqStartDTO
    #got valid entry time - exists in data list
    locOfStartSample = timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S'))
    #if error - not found, inc seconds and try again
    
 

    labels = [i[0] for i in data[locOfStartSample::]]
    tempvalues = [i[1] for i in data[locOfStartSample::]]
    humivalues = [i[2] for i in data[locOfStartSample::]]
    heatervalues = [i[3] for i in data[locOfStartSample::]]
    ventvalues = [i[4] for i in data[locOfStartSample::]]
    fanvalues = [i[5] for i in data[locOfStartSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/multit4")
def multit4():  # hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 2hrs data
    #get last sample time stamp
    #convert string in CSV to datetime obhect
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')#in format YYY-MM-DD HH:mm:ss
    #print data[0][len(data)
    #print lastSampleDT
    #raw_input("Press Enter to continue...")
    #scan thru label(timestamp) array to get sample that is at least 2hrs previous to last sample
    #calc start time string looking for for start of time frame sample
    reqStartDTO = lastSampleDT - timedelta(hours=4)
    
    timeList = [item[0] for item in data]
    #print timeList
    
    #thing_index = thing_list.index(elem) if elem in thing_list else -1
    while ( (timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) if datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') in timeList else -1) == -1 ):
    #while ( timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) == ValueError ):
        #inc value to check for in list
        reqStartDTO += timedelta(seconds=1)
        print reqStartDTO
    #got valid entry time - exists in data list
    locOfStartSample = timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S'))
    #if error - not found, inc seconds and try again
    
 

    labels = [i[0] for i in data[locOfStartSample::]]
    tempvalues = [i[1] for i in data[locOfStartSample::]]
    humivalues = [i[2] for i in data[locOfStartSample::]]
    heatervalues = [i[3] for i in data[locOfStartSample::]]
    ventvalues = [i[4] for i in data[locOfStartSample::]]
    fanvalues = [i[5] for i in data[locOfStartSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/multit8")
def multit8():  # hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 2hrs data
    #get last sample time stamp
    #convert string in CSV to datetime obhect
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')#in format YYY-MM-DD HH:mm:ss
    #print data[0][len(data)
    #print lastSampleDT
    #raw_input("Press Enter to continue...")
    #scan thru label(timestamp) array to get sample that is at least 2hrs previous to last sample
    #calc start time string looking for for start of time frame sample
    reqStartDTO = lastSampleDT - timedelta(hours=8)
    
    timeList = [item[0] for item in data]
    #print timeList
    
    #thing_index = thing_list.index(elem) if elem in thing_list else -1
    while ( (timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) if datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') in timeList else -1) == -1 ):
    #while ( timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) == ValueError ):
        #inc value to check for in list
        reqStartDTO += timedelta(seconds=1)
        print reqStartDTO
    #got valid entry time - exists in data list
    locOfStartSample = timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S'))
    #if error - not found, inc seconds and try again
    
 

    labels = [i[0] for i in data[locOfStartSample::]]
    tempvalues = [i[1] for i in data[locOfStartSample::]]
    humivalues = [i[2] for i in data[locOfStartSample::]]
    heatervalues = [i[3] for i in data[locOfStartSample::]]
    ventvalues = [i[4] for i in data[locOfStartSample::]]
    fanvalues = [i[5] for i in data[locOfStartSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/multit24")
def multit24():  # hours of samples

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 2hrs data
    #get last sample time stamp
    #convert string in CSV to datetime obhect
    lastSampleDT = datetime.strptime(data[len(data)-1][0], '%Y-%m-%d %H:%M:%S')#in format YYY-MM-DD HH:mm:ss
    #print data[0][len(data)
    #print lastSampleDT
    #raw_input("Press Enter to continue...")
    #scan thru label(timestamp) array to get sample that is at least 2hrs previous to last sample
    #calc start time string looking for for start of time frame sample
    reqStartDTO = lastSampleDT - timedelta(hours=24)
    
    timeList = [item[0] for item in data]
    #print timeList
    
    #thing_index = thing_list.index(elem) if elem in thing_list else -1
    while ( (timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) if datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S') in timeList else -1) == -1 ):
    #while ( timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S')) == ValueError ):
        #inc value to check for in list
        reqStartDTO += timedelta(seconds=1)
        print reqStartDTO
    #got valid entry time - exists in data list
    locOfStartSample = timeList.index(datetime.strftime(reqStartDTO, '%Y-%m-%d %H:%M:%S'))
    #if error - not found, inc seconds and try again
    
 

    labels = [i[0] for i in data[locOfStartSample::]]
    tempvalues = [i[1] for i in data[locOfStartSample::]]
    humivalues = [i[2] for i in data[locOfStartSample::]]
    heatervalues = [i[3] for i in data[locOfStartSample::]]
    ventvalues = [i[4] for i in data[locOfStartSample::]]
    fanvalues = [i[5] for i in data[locOfStartSample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)


@app.route("/multit")
def multit():

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    listlen = len(data)
    startsample = 1

    labels = [i[0] for i in data[startsample::]]
    tempvalues = [i[1] for i in data[startsample::]]
    humivalues = [i[2] for i in data[startsample::]]
    heatervalues = [i[3] for i in data[startsample::]]
    ventvalues = [i[4] for i in data[startsample::]]
    fanvalues = [i[5] for i in data[startsample::]]
    
    return render_template('multit.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/chartx/<int:timeh>")
def chartx(timeh):

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 4hrs data, 4*60*2 samples, 1 every 30 secs
    hours = timeh   #hoursreq
    numsamples = hours * 60 * 2
    listlen = len(data)
    #print hours
    #print listlen
    startsample = listlen - numsamples
    #print startsample
    #raw_input("Press Enter to continue...")

    labels = [i[0] for i in data[startsample::]]
    tempvalues = [i[1] for i in data[startsample::]]
    humivalues = [i[2] for i in data[startsample::]]
    heatervalues = [i[3] for i in data[startsample::]]
    ventvalues = [i[4] for i in data[startsample::]]
    fanvalues = [i[5] for i in data[startsample::]]
    
    return render_template('multi4.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)


@app.route("/multi1")
def multi1():

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))
    
    #select only last 4hrs data, 4*60*2 samples, 1 every 30 secs
    hours = 1   #hoursreq
    numsamples = hours * 60 * 2
    listlen = len(data)
    #print hours
    #print listlen
    startsample = listlen - numsamples
    #print startsample
    #raw_input("Press Enter to continue...")

    labels = [i[0] for i in data[startsample::]]
    tempvalues = [i[1] for i in data[startsample::]]
    humivalues = [i[2] for i in data[startsample::]]
    heatervalues = [i[3] for i in data[startsample::]]
    ventvalues = [i[4] for i in data[startsample::]]
    fanvalues = [i[5] for i in data[startsample::]]
    
    return render_template('multi4.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)




@app.route("/chart1")
def chart1():
    
    with open('thdata.csv', 'r') as f:
        data = list(reader(f))

    labels = [i[0] for i in data[1::]]
    tempvalues = [i[1] for i in data[1::]]
    humivalues = [i[2] for i in data[1::]]
    heatervalues = [i[3] for i in data[1::]]
    ventvalues = [i[4] for i in data[1::]]
    fanvalues = [i[5] for i in data[1::]]
    
    return render_template('chart.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/chart2")
def chart2():
    
    with open('thdata.csv', 'r') as f:
        data = list(reader(f))

    labels = [i[0] for i in data[1::]]
    tempvalues = [i[1] for i in data[1::]]
    humivalues = [i[2] for i in data[1::]]
    heatervalues = [i[3] for i in data[1::]]
    ventvalues = [i[4] for i in data[1::]]
    fanvalues = [i[5] for i in data[1::]]

    
    return render_template('chart2.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)

@app.route("/multi")
def multi():

    with open('thdata.csv', 'r') as f:
        data = list(reader(f))

    labels = [i[0] for i in data[1::]]
    tempvalues = [i[1] for i in data[1::]]
    humivalues = [i[2] for i in data[1::]]
    heatervalues = [i[3] for i in data[1::]]
    ventvalues = [i[4] for i in data[1::]]
    fanvalues = [i[5] for i in data[1::]]
    
    return render_template('multi4.html', tempvalues=tempvalues, humivalues=humivalues, heatervalues=heatervalues, ventvalues=ventvalues, fanvalues=fanvalues, labels=labels)


@app.route("/home")
def home():
    message = "Controller Status Page"
    
    #get relay states
    for relay in relays:
        relays[relay]['state'] = gpio.digitalRead(relay)
        
    #get sensor data
    #dht22.setup()
    #dht22.getth()
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
    
    #get relay states
    for relay in relays:
        relays[relay]['state'] = gpio.digitalRead(relay)

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
    #if ctl.heaterState:
    #    state = "Heater OFF"
    #else:
    state = round(ctl.dht22.cvar.temperature, 1)
    print "STATE FOR TEMP AJAX", state
    return jsonify(tempRelayState=state)
    
@app.route("/_getHumi")
def _getHumi():
    #if ctl.heaterState:
    #    state = "Heater OFF"
    #else:
    state = round(ctl.dht22.cvar.humidity, 1)
    print "STATE FOR HUMI AJAX", state
    return jsonify(humiRelayState=state)
    
# ajax GET call this function periodically to read heater state
# the state is sent back as json data
@app.route("/_heaterRelay")
def _heaterRelay():
    if ctl.heaterState:
        state = "Heater OFF"
    else:
        state = "Heater ON"
    print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(heaterRelayState=state)
    
@app.route("/_ventRelay")
def _ventRelay():
    if ctl.ventState:
        state = "Vent OFF"
    else:
        state = "Vent ON"
    #print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(ventRelayState=state)
    
@app.route("/_fanRelay")
def _fanRelay():
    if ctl.fanState:
        state = "Fan OFF"
    else:
        state = "Fan ON"
    #print "STATE FOR HEATER RELAY AJAX", state
    return jsonify(fanRelayState=state)
    
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


#if __name__ == '__main__':
 #   app.run(debug=True, host='0.0.0.0')
    #ctl.main()
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
   
#t = Thread(target=start_web_server)
#t.daemon = True
#t.start()

#c = Thread(target=docontrol)
#c.daemon = True        
#c.start() 

#app.run(host='0.0.0.0', debug=True, use_reloader=False, threaded=True)  

#ctl.main()
