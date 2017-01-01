#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
import secureFile


def sendemail(subject, message):
    USERNAME = "cn@gmail.com"
    PASSWORD = "in"
    MAILTO  = "c@gmail.com"
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = USERNAME
    msg['To'] = MAILTO
    
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, MAILTO, msg.as_string())
    server.quit()

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   temp=23.3
   humi=45.1
   
   message = 'readings, Temp='+ str(temp) + '  Humi='+ str(humi)
   sendemail('Spike in Reading', message)
   #sendEmail( 'Pi Subject test', 'this is the test message im sending')
   
   
