import datetime as dt

import yaml
from DatabaseObject import db # singleton
import os

class Config(object):


    def __init__(self):
        print("creating config object")
        #write init config from file to db
        self.config = self.readConfigFromFile()
        self.writeConfigToFile(self.config)

        self.writeConfigToDB()

        print("__written temp lon sp to db config__");
        return

    def readConfigFromFile(self):
        #to start use python settings imported module from tof
        fileStr = os.path.abspath("config.yaml")
        #f = open('/home/pi/controlleroo/config.yaml')
        f = open(fileStr)
        # use safe_load instead load
        config = yaml.safe_load(f)
        print("==Reading config settings from yaml file==")
        print yaml.dump(config)
        f.close()
        #self.config = config
        
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$: ",os.path.abspath("config.yaml"))
        
        return config
        
    def writeConfigToDB(self):
        print("==Writing settings to db ..")
        self.setConfigItemInDB( 'tempSPLOn', self.config['tempSPLOn'])
        self.setConfigItemInDB( 'tempSPLOff', self.config['tempSPLOff'])
        db.updateCentralConfigTable(self.config) 
        return
        
    def setConfigItemInDB(self, name, value):
        db.setConfigItem(name, value)
        return
        
    def getConfigItemFromDB(self, name, value):
        return value
        
    def getItemValue(self, item):
        value = self.config[item]
        return value
        
    def readConfigFromDB(self):
        config = 1
        return config



    def writeConfigToFile(self, config):
        fileStr = os.path.abspath("config_new.yaml")
        f = open(fileStr, "w")
        print("==Writing config settings to new yaml file config_new.yaml==")
        yaml.dump(config, f)
        f.close()
        return

    def getTOn(self):
        hrs = int(float(self.config['lightOnT'][0:2]))
        mins = int(float(self.config['lightOnT'][3:5]))
        return dt.time(hrs,mins)

    def getTOff(self):
        hrs = int(float(self.config['lightOffT'][0:2]))
        mins = int(float(self.config['lightOffT'][3:5]))
        return dt.time(hrs,mins)

