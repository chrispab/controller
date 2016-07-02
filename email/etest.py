#!/usr/bin/python
#-*- coding: utf-8 -*-
import smtplib

import time
from adc import analog_read

server= 'smtp.gmail.com'
port = 587

sender = 'cbattisson@gmail.com'
recipient = 'cbattisson@gmail.com'
password='oxtqierdddaakwwo'
subject = 'Water Leakage Detected'
body = 'Water detected at basement water heater 1.'

def delay(ms):
	time.sleep(1.0*ms/1000)

def setup():
		print "read channel ADC2 value ,the V-REF = 3.3V"
		delay(3000)

body = "" + body + ""

headers = ["From: " + sender,
		   "Subject: " + subject,
		   "To: " + recipient,
		   "MIME-Version: 1.0",
		   "Content-Type: text/html"]
headers = "\r\n".join(headers)

def loop():
	while(1):
		value = 0 # analog_read(2)
		voltage = 0 # (value * 3.3)/4096
		print ("value.. =  %4d" %value)
		print ("voltage =  %4.3f  V" %voltage)
		if 1==1 :
			 session = smtplib.SMTP(server, port)
			 session.ehlo()
			 session.starttls()
			 session.ehlo
			 session.login(sender, password)
			 session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
			 session.quit()
			 print("sent")
		delay(10000)

def main():
	setup()
	loop()

main()
