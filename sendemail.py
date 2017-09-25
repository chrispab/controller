#!/usr/bin/env python
import smtplib
from email.mime.text import MIMEText
import secureFile
import logging
import sys    # for stdout print


from ConfigObject import cfg # singleton global


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
            logging.error( "????? Error: %s   OLD EMAIL ROUTINE   ?????" % e )
    return
    

if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   #test for sending email
   temp=23.3
   humi=45.1
   
   message = 'readings, Temp='+ str(temp) + '  Humi='+ str(humi)
   sendemail('Test email from Zone', message)
   #sendEmail( 'Pi Subject test', 'this is the test message im sending')
   
   
