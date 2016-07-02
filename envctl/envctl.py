from flask import Flask, render_template
import datetime
import gpio
#import dht22
import control


app = Flask(__name__)

relays = {
         'gpio3':{'name':'heaterRelay','state':False},
         'gpio4':{'name':'ventRelay','state':True},
         'gpio5':{'name':'fanRelay','state':False},
         'gpio6':{'name':'relay4','state':False}
        }


@app.route('/')
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
        'title' : 'HELLO!',
        'time': timeString
    }
    return render_template('main.html', **templateData)
    #return render_template('index.html')

@app.route("/status")
def status():
    message = "Controller Status Page"
    
    #get relay states
    for relay in relays:
        relays[relay]['state'] = gpio.digitalRead(relay)
        
    #get sensor data
    #dht22.setup()
    #dht22.getth()
    temp = dht22.cvar.temperature
    humi = dht22.cvar.humidity
     
    templateData = {
                'message' :  message ,
                'temp' : temp,
                'humi' : humi,
                'relays' : relays
            }
    return render_template('status.html',**templateData)
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
