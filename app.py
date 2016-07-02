from flask import Flask
from flask import Markup
from flask import Flask
from flask import render_template
from csv import reader

app = Flask(__name__)
 
@app.route("/")
def chart():
    labels = ["January","February","March","April","May","June","July","August"]
    tempvalues = [10,9,8,7,6,4,7,8]
    humivalues = [12,4,7,8,2,9,5,7]
    
    with open('thdata.csv', 'r') as f:
        data = list(reader(f))

    labels = [i[0] for i in data[1::]]
        
    tempvalues = [i[1] for i in data[1::]]
    humivalues = [i[2] for i in data[1::]]
    
    return render_template('chart.html', tempvalues=tempvalues, humivalues=humivalues, labels=labels)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
