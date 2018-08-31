# this file must be present in the controller dir renamed location.py
# modify this to suit your reqs and save a copy in your controller dir
# each controller has it's own unique location.py file. this file is not 
# kept on github, just the location_example.py file 

######################################
# the zoneName must include a number. This must be specified 1,2 or 3. 
# This setting dictates which cental db to use for this device, and 
# display order/location on the web page
# e.g.
# "Zone 1"
# "Zone 2"
# "Zone 3"
#zoneName = "zone1"
zoneName = "zone2"
#zoneName = "zone3"
#####################################

#####################################
# note: use the "code" value, to set what code looks for as location - 
# different from displayName
# this allows loading cutom settings based on the pi physical location.
#
# Possible values
# "s" - typically zone 1
# "c" - typically zone 2
# "g" - typically zone 3
#this next one is critical as defines which location settings used for this location
#code = "s"
code = "c"  # code used in configClass to build config filename 
#code = "g"
######################################

######################################
# The displayName, corresponds to the loaction name of the controller, 
# this is just the text that will appear on the web page and in emails 
# from this device
# this term is not currently used yet in main code - gets disp name from config_locations.yaml
#displayName = "shd"
displayName = "cnv"
#displayName = "grg"
######################################

