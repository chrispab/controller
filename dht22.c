/*
* DHT22 driver for Python access
* c.battisson
* 13 april 2016
*/
#include "core.h"
#include "dht22.h"

int led_pin0 = 0; //gpio0
int led_pin1 = 1;   //gpio1
int dhtdatapin = 7; //dht data pin
float humidity = 99; //for h value
float temperature = 100; //for temp value
int t_low = 1000;   //u secs
int t_hi = 30;      //us
int result;
int totalAquisitions=0;
int good=0;
float sp = 22; //setpoint
int heaterpin = 3;  //op pin to control heater relay set low=on, hi= off

unsigned long currentMillis = 0;    // stores the value of millis() in each iteration of loop()

unsigned long lastAquisitionMillis = 0; // time when last succesful data aquisition time

void setup() {
    init();  //initialise low level io etc -
    pinMode(led_pin0, OUTPUT);
    pinMode(led_pin1, OUTPUT);
    pinMode(dhtdatapin, OUTPUT);
    digitalWrite(dhtdatapin, LOW);
    return;
}

void loop() {
    printf("t_low us:%i, t_hi us:%i ",t_low,t_hi);
   	printf("...sampling... ");
	result = getth(); //get data and return ok or not
    totalAquisitions+=1;
    if ( result == DHTLIB_ERROR_CHECKSUM)  
		printf("===bad CRC===\n");
    else if ( result == DHTLIB_ERROR_TIMEOUT)
        printf("===timeout===\n");
    else {  //result must be good
		printf("===good crc===\n");
		printf("temp:%2.1f, ", temperature);
        printf("humi:%2.1f\n", humidity);

		good += 1;	//inc good count
		printf("good :%4i, ", good);
		printf("total:%4i, ", totalAquisitions);
		printf("good%%:%3.2f \n\n", ((double)good/(double)totalAquisitions)*100);
    }
}

int getth() {
	// BUFFER TO RECEIVE
	uint8_t bits[5];
	uint8_t cnt = 7;
	uint8_t idx = 0;

    unsigned int loopCntDown;   //loop count down var
    unsigned long t;    // holds cuurent micros
    
    int i;
	for (i=0; i< 5; i++)// EMPTY BUFFER
        bits[i] = 0;
	    
    // check if delay required to ensure 2sec delay between sensor reads
    while ( (lastAquisitionMillis + 2000) >= millis() ) ;   //wait for 2 secs since last aqui
    lastAquisitionMillis = millis();    //update last aqu time
	// REQUEST SAMPLE
	pinMode(dhtdatapin, OUTPUT);	//set pin as op to start conversion
    digitalWrite(dhtdatapin, HIGH);
	digitalWrite(dhtdatapin, LOW);	//take pin lo to initiate conv
	delayMicroseconds(t_low);	//wait us
	digitalWrite(dhtdatapin, HIGH);	//take hi to trigger
	delayMicroseconds(t_hi);	//wait us
	pinMode(dhtdatapin, INPUT);	//make pin ip to read data

    //begin reading in the data stream from dht22
	// rx ACKNOWLEDGE or TIMEOUT
	loopCntDown = 10000;
	while(digitalRead(dhtdatapin) == LOW)   //wait for pin to go high before cont
		if (loopCntDown-- == 0) return DHTLIB_ERROR_TIMEOUT;
	
	loopCntDown = 10000;
	while(digitalRead(dhtdatapin) == HIGH)  //wait for pin to go low before cont
		if (loopCntDown-- == 0) return DHTLIB_ERROR_TIMEOUT;

	// READ OUTPUT - 40 BITS => 5 BYTES or TIMEOUT
	for (i=0; i<40; i++) {
		loopCntDown = 10000;
		while(digitalRead(dhtdatapin) == LOW)
			if (loopCntDown-- == 0)
                return DHTLIB_ERROR_TIMEOUT;

		t = micros();   //take current micros count

		loopCntDown = 10000;
		while(digitalRead(dhtdatapin) == HIGH)
			if (loopCntDown-- == 0)
                return DHTLIB_ERROR_TIMEOUT;

		if ((micros() - t) > 40)
            bits[idx] |= (1 << cnt);
		if (cnt == 0) { // next byte?
			cnt = 7;    // restart at MSB
			idx++;      // next byte!
		}
		else cnt--;
	}   //aquisition done
    
    // check data validity
	uint8_t sum = bits[0] + bits[1] + bits[2] + bits[3];  
	if (bits[4] != sum)
        return DHTLIB_ERROR_CHECKSUM;
	// else OK so WRITE data TO RIGHT VARS
	humidity = bits[0];
    humidity *= 256;
    humidity += bits[1];
    humidity *= 0.1;
	temperature = bits[2] & 0x7F;
    temperature *= 256;
    temperature += bits[3];
    temperature *= 0.1;
    if (bits[2] & 0x80)
		temperature *= -1;
    
    //must be good data if gets here
    return DHTLIB_OK;//aq done and temp and humi vars updated
}
