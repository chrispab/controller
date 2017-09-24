#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
import secureFile
import logging
import sys    # for stdout print


from ConfigObject import cfg # singleton global


class Email(object):

    def __init__(self):
        logging.info("Creating email object")
        self.state = OFF
        self.prevEmailSendMillis = 0  # last time an email was sent
        #self.fan_on_delta = cfg.getItemValueFromConfig('fan_on_t')  # vent on time
        #self.fan_off_delta = cfg.getItemValueFromConfig('fan_off_t')  # vent off time
        self.current_time = 0
        self.start_millis = 0
        self.current_millis = 0
        self.delta = 0
        self.prevEmailSendTime = 0
        self.emailSendTimeGap = 60 * 1000 #60 secs each 1000 ms
        # get time at start of program execution
        self.start_millis = datetime.datetime.now()
        self.updateClocks()

    def control(self, current_millis):
        logging.info('==fan ctl==')
        # if fan off, we must wait for the interval to expire before turning it on
        logging.info('==current millis: %s' % (current_millis))
        logging.info('==current fan state: %s' % (self.state))
        if self.state == OFF:
            # if time is up, so change the state to ON
            if current_millis - self.prev_fan_millis >= self.fan_off_delta:
                self.state = ON
                logging.info("..FAN ON")
                self.prev_fan_millis = current_millis
        # else if fanState is ON
        else:
            # time is up, so change the state to LOW
            if (current_millis - self.prev_fan_millis) >= self.fan_on_delta:
                self.state = OFF
                logging.info("..FAN OFF")
                self.prev_fan_millis = current_millis
        #self.state = ON
        return
        
    def send(self, subject, message):
        logging.info('==try to send email==')
        
        #check if email has been sent in previous emailSendTimeGap secs
        if (selfcurrentTime - self.prevEmailSendTime) > self.emailSendTimeGap):
            self.sendmail(subject, message)
            #update time of last email send
            self.prevEmailSendTime = currentTime
            
        
        
        return
        
    def updateClocks(self):
        self.current_time = datetime.datetime.now()  # get current time
        # calc elapsed delta ms since program began
        self.delta = self.current_time - self.start_millis
        self.current_millis = int(self.delta.total_seconds() * 1000)
        return        
   

    def sendemail(subject, message):
        #3 params below held in secureFile.py - not uploaded to github
        #USERNAME = "cn@gmail.com"
        #PASSWORD = "in"
        #MAILTO  = "c@gmail.com"
        
        emailEnabled = cfg.getItemValueFromConfig('emailEnabled')  # email Enabled T orF
        if emailEnabled:
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
        return
    


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   #test for sending email
   temp=23.3
   humi=45.1
   
   message = 'readings, Temp='+ str(temp) + '  Humi='+ str(humi)
   sendemail('Test email from Zone', message)
   #sendEmail( 'Pi Subject test', 'this is the test message im sending')
   
   
