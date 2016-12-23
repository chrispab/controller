import yaml

class Settings(object):


    def __init__(self):
        print("creating settings object")
        #write init settings from file to db
        self.settings = self.readSettingsFromFile()
        self.writeSettingsToDB(self.settings)
        return

    def readSettingsFromFile(self):
        #settings = 1
        #to start use python settings imported module from tof
        f = open('/home/pi/controlleroo/config.yaml')
        # use safe_load instead load
        settings = yaml.safe_load(f)
        print yaml.dump(settings)
        f.close()
        return settings
        
    def writeSettingsToDB(self, settings):
        print("Writing settings to db ..................")
        
        #self.writeSettingsToFile( settings)
        
        #f = open('newtree.yaml', "w")
        #yaml.dump(settings, f)
        #f.close()        
        
        #self.setDBConfigItem(name, value)
        #
        
        return
        
    def setDBConfigItem(self, name, value):
        return
        
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

