DIR=$(shell pwd)



INCS = -I.\
		-I$(DIR) \
		-I/home/ubuntu/c_environment/hardware/arduino/cores/arduino \
		-I/home/ubuntu/c_environment/hardware/arduino/variants/sunxi
        #-I$(DIR)/hardware \
        #-I$(DIR)/hardware/arduino \
        #-I$(DIR)/hardware/arduino/cores \
        #-I$(DIR)/hardware/arduino/cores/arduino \
        #-I$(DIR)/hardware/arduino/variants \
        #-I$(DIR)/hardware/arduino/variants/sunxi \
        #-I$(DIR)/libraries \
        #-I$(DIR)/libraries/Serial \
        #-I$(DIR)/libraries/SPI \
		#-I$(DIR)/libraries/Wire \
		#-I$(DIR)/libraries/LiquidCrystal \
		#-I$(DIR)/libraries/PN532_SPI \


LIBS=/home/ubuntu/c_environment/libarduino.a
TARGET=.

OBJS = dht22

all:
	swig -python dht22.i

	gcc -fPIC -I/usr/include/python2.7 -I/home/ubuntu/c_environment/hardware/arduino/cores/arduino -I/home/ubuntu/c_environment/hardware/arduino/variants/sunxi -c dht22.c dht22_wrap.c &&	gcc -shared /home/ubuntu/c_environment/hardware/arduino/cores/arduino/wiring_digital.o /home/ubuntu/c_environment/hardware/arduino/cores/arduino/wiring.o /home/ubuntu/c_environment/hardware/arduino/cores/arduino/platform.o libarduino.a dht22.o dht22_wrap.o -o _dht22.so ; done
	

clean:
	@for i in $(OBJS); do rm -f $(TARGET)/$$i; done
