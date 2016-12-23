import yaml
from DatabaseObject import db # singleton

class Settings(object):


    def __init__(self):
        print("creating settings object")
        #write init settings from file to db
        self.settings = self.readSettingsFromFile()
        self.writeSettingsToDB(self.settings)

        print("________written temp lon sp to db config____\n");
        return

    def readSettingsFromFile(self):

        #to start use python settings imported module from tof
        f = open('/home/pi/controlleroo/config.yaml')
        # use safe_load instead load
        settings = yaml.safe_load(f)
        print yaml.dump(settings)
        f.close()
        return settings
        
    def writeSettingsToDB(self, settings):
        print("Writing settings to db ..................")

        self.setConfigItemInDB( 'tempSPLOn', settings['temp_d_on_SP'])
        self.setConfigItemInDB( 'tempSPLOff', settings['temp_d_off_SP'])
        return
        
    def setConfigItemInDB(self, name, value):
        db.setConfigItem(name, value)
        
        return
        
    def getConfigItemFromDB(self, name, value):
        return value
        
    def readSettingsFromDB(self):
        settings = 1
        return settings



    def writeSettingsToFile(self, settings):
        f = open('/home/pi/controlleroo/config_new.yaml', "w")
        yaml.dump(settings, f)
        f.close()
        return

    def setSetting(self, name, val):
        return

    def getSetting(self, name):
        val = 1
        return val

