#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

#pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]
# conv byte addresses[][6] = {"1Node","2Node"}; to hex
# 1Node == 0x31 0x4e 0x6f 0x64 0x65 == 314e6f6465
# 2Node == 0x32 0x4e 0x6f 0x64 0x65 == 324e6f6465
pipes = [[0x31, 0x4e, 0x6f, 0x64, 0x65], [0x32, 0x4e, 0x6f, 0x64, 0x65]]
#pipes = [[0x314e6f6465], [0x324e6f6465]]

#pipes = [["1Node"], ["2Node"]]

#radio(RPI_V2_GPIO_P1_15,BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ);

radio = NRF24(GPIO, spidev.SpiDev())
#radio = NRF24(GPIO, GPIO.SpiDev())

#radio(RPI_V2_GPIO_P1_15,BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ);

radio.begin(0, 17)

radio.setPALevel(NRF24.PA_MIN)

radio.setDataRate(NRF24.BR_1MBPS)
#radio.setDataRate(NRF24.BR_2MBPS)

radio.setPayloadSize(32)

radio.setChannel(124)

#radio.powerUp()
#radio.powe

radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[1])
radio.printDetails()
#radio.startListening()
#radio.stopListening()

#radio.printDetails()
#radio.printDetails()
time.sleep(20)
radio.stopListening()
radio.startListening()

while(1):
    ackPL = [1]
    pipe = [0]
    while not radio.available(0):
        time.sleep(10000/1000000.0)
    receivedMessage = []
    # Is there any data for us to get?
    #if ( radio.available()):
        # Go and read the data and put it into that variable
        #while (radio.available()):
            #radio.read( &data, sizeof(char))
    radio.read(receivedMessage, radio.getDynamicPayloadSize())
        
    #receivedMessage = []
    #radio.read(receivedMessage, 1)
    
    #radio.stopListening()
    print("Received: ", receivedMessage)

    #time.sleep(1)
    #print("Translating the receivedMessage into unicode characters")
    #string = ""
    #for n in receivedMessage:
        ## Decode into standard unicode set
        #if (n >= 32 and n <= 126):
            #string += chr(n)
    #print("Out received message decodes to: ", receivedMessage)
    #radio.startListening()
