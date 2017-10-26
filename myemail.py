#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
import secureFile
import logging
import sys    # for stdout print
import datetime


from ConfigObject import cfg # singleton global


class MyEmail(object):

    def __init__(self):
        logging.info("Creating email object")

        self.prevEmailSendMillis = 0  # last time an email was sent
        self.currentDateTime = 0
        self.startDateTime = 0
        self.elapsedMillis = 0
        self.deltaDateTime = 0
        self.prevEmailSendMillis = 0
        self.emailSendTimeGap = 60 * 15 * 1000 #time in milli secs, 60 secs each 1000 ms
        self.emailEnabled = cfg.getItemValueFromConfig('emailEnabled')  # email Enabled T orF
        # get date and time at start of program execution
        self.startDateTime = datetime.datetime.now()
        self.updateClocks()


    def send(self, subject, message):
        logging.info('==try to send email==')
        
        if self.emailEnabled:
            self.updateClocks()
            #check if email has been sent in previous emailSendTimeGap secs
            if (self.prevEmailSendMillis == 0) or ((self.elapsedMillis - self.prevEmailSendMillis) >= self.emailSendTimeGap):
                self.sendemail(subject, message)
                #update time of last email send
                self.prevEmailSendMillis = self.elapsedMillis
                logging.warning("== NEW EMAIL METHOD SENT: %s =", self.elapsedMillis)
            else:
                logging.warning("== NEW EMAIL METHOD NOT_SENT: %s =", self.elapsedMillis)
                    
        return
        
        
    def updateClocks(self):
        self.currentDateTime = datetime.datetime.now()  # get current time
        # calc elapsed delta ms since program began
        self.deltaDateTime = self.currentDateTime - self.startDateTime
        self.elapsedMillis = int(self.deltaDateTime.total_seconds() * 1000)
        return        
   

    def sendemail(self, subject, message):
        #3 params below held in secureFile.py - not uploaded to github
        #USERNAME = "cn@gmail.com"
        #PASSWORD = "in"
        #MAILTO  = "c@gmail.com"
        
        #emailEnabled = cfg.getItemValueFromConfig('emailEnabled')  # email Enabled T orF
        if self.emailEnabled:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = secureFile.USERNAME
            msg['To'] = secureFile.MAILTO
            try:
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo_or_helo_if_needed()
                server.starttls()
                server.ehlo_or_helo_if_needed()
                server.login(secureFile.USERNAME,secureFile.PASSWORD)
                server.sendmail(secureFile.USERNAME, secureFile.MAILTO, msg.as_string())
                server.quit()
            except:
                logging.error("????? Error sending email ???")
                e = sys.exc_info()[0]
                logging.error( "????? Error: %s ?????" % e )
                logging.error("????IN NEW EMAIL ROUTINE????")
        return
    


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   #test for sending email
   temp=23.3
   humi=45.1
   
   message = 'readings, Temp='+ str(temp) + '  Humi='+ str(humi)
   sendemail('Test email from Zone', message)
   #sendEmail( 'Pi Subject test', 'this is the test message im sending')
   
   
