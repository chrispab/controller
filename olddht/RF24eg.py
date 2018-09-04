#!/usr/bin/env python

#
# Example using Dynamic Payloads
# 
#  This is an example of how to use payloads of a varying (dynamic) size.
# 

from __future__ import print_function
import time
from RF24 import *
import RPi.GPIO as GPIO

irq_gpio_pin = None

########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/RPi/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B
# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B+
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
#radio = RF24(RPI_BPLUS_GPIO_J8_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

# RPi Alternate, with SPIDEV - Note: Edit RF24/arch/BBB/spi.cpp and  set 'this->device = "/dev/spidev0.0";;' or as listed in /dev
radio = RF24(17, 0);


# Setup for connected IRQ pin, GPIO 24 on RPi B+; uncomment to activate
#irq_gpio_pin = RPI_BPLUS_GPIO_J8_18
#irq_gpio_pin = 24

##########################################
def try_read_data(channel=0):
    if radio.available():
        while radio.available():
            #len = radio.getDynamicPayloadSize()
            receive_payload=radio.read(1 )
            print('Got payload ',ord(receive_payload) )
            # First, stop listening so we can talk
            radio.stopListening()
            
            #receive_payload = ord(receive_payload)+1
            # Send the final one back.
            radio.write(receive_payload)
            print('Sent response.',receive_payload)

            # Now, resume listening so we catch the next packets.
            radio.startListening()
            #time.sleep(1000)

#pipes = [0xF0F0F0F0E1, 0xF0F0F0F0D2]
#pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
# conv byte addresses[][6] = {"1Node","2Node"}; to hex
# 1Node == 0x31 0x4e 0x6f 0x64 0x65 == 314e6f6465
# 2Node == 0x32 0x4e 0x6f 0x64 0x65 == 324e6f6465
pipes = [0x65646f4e31, 0x65646f4e32]

#pipes = [0x314E6F6465, 0x324E6F6465]



min_payload_size = 4
max_payload_size = 32
payload_size_increments_by = 1
next_payload_size = min_payload_size
inp_role = 'none'
send_payload = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ789012'
millis = lambda: int(round(time.time() * 1000))

print('pyRF24/examples/pingpair_dyn/')

radio.begin()


radio.setPALevel(RF24_PA_LOW)

radio.setDataRate(RF24_250KBPS)
radio.setChannel(124)
radio.setAutoAck(True)
#radio.enableDynamicPayloads()
#radio.enableAckPayload()

#radio.enableDynamicPayloads()
radio.setRetries(15,15)
radio.printDetails()

print(' ************ Role Setup *********** ')
while (inp_role !='0') and (inp_role !='1'):
    inp_role = str(input('Choose a role: Enter 0 for receiver, 1 for transmitter (CTRL+C to exit) '))

if inp_role == '0':
    print('Role: Pong Back, awaiting transmission')
    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1,pipes[1])
    radio.startListening()
else:
    print('Role: Ping Out, starting transmission')
    radio.openWritingPipe(pipes[0])
    radio.openReadingPipe(1,pipes[1])

# forever loop
while 1:
    if inp_role == '1':   # ping out
        # The payload will always be the same, what will change is how much of it we send.

        # First, stop listening so we can talk.
        radio.stopListening()

        # Take the time, and send it.  This will block until complete
        #print('Now sending length {} ... '.format(next_payload_size), end="")
        print('Now sending char "n" ... ')
        #mybuff = [0xff]
        #buf = 125
        radio.write('n')
        #radio.write(send_payload[:next_payload_size])
        
        # Now, continue listening
        radio.startListening()

        # Wait here until we get a response, or timeout
        started_waiting_at = millis()
        timeout = False
        while (not radio.available()) and (not timeout):
            if (millis() - started_waiting_at) > 500:
                timeout = True

        # Describe the results
        if timeout:
            print('failed, response timed out.')
        else:
            # Grab the response, compare, and send to debugging spew
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)

            # Spew it
            print('got response ',receive_payload)

        # Update size for next time.
        next_payload_size += payload_size_increments_by
        if next_payload_size > max_payload_size:
            next_payload_size = min_payload_size
        time.sleep(0.1)
    else:
        # Pong back role.  Receive each packet, dump it out, and send it back

        # if there is data ready
        if irq_gpio_pin is None:
            # no irq pin is set up -> poll it
            try_read_data()
        else:
            # callback routine set for irq pin takes care for reading -
            # do nothing, just sleeps in order not to burn cpu by looping
            time.sleep(1000)

