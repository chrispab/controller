import yaml
from DatabaseObject import db # singleton

class Config(object):


    def __init__(self):
        print("creating config object")
        #write init config from file to db
        self.config = self.readConfigFromFile()
        self.writeConfigToDB()

        print("________written temp lon sp to db config____\n");
        return

    def readConfigFromFile(self):

        #to start use python settings imported module from tof
        f = open('/home/pi/controlleroo/config.yaml')
        # use safe_load instead load
        config = yaml.safe_load(f)
        print yaml.dump(config)
        f.close()
        return config
        
    def writeConfigToDB(self):
        print("Writing settings to db ..................")

        self.setConfigItemInDB( 'tempSPLOn', self.config['tempSPLOn'])
        self.setConfigItemInDB( 'tempSPLOff', self.config['tempSPLOff'])
        db.updateCentralConfigTable(self.config) 
        return
        
    def setConfigItemInDB(self, name, value):
        db.setConfigItem(name, value)
        
        return
        
    def getConfigItemFromDB(self, name, value):
        return value
        
    def readConfigFromDB(self):
        config = 1
        return config



    def writeConfigToFile(self, settings):
        f = open('/home/pi/controlleroo/config_new.yaml', "w")
        yaml.dump(settings, f)
        f.close()
        return

    def setSetting(self, name, val):
        return

    def getSetting(self, name):
        val = 1
        return val

