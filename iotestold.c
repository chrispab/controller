/*
* LED test program
*/
#include "core.h"
#include "iotest.h"

int led_pin = 0; //default pin if run thru ide
int dht11pin = 7; //dht data pin
int humidity = 99; //for h value
int temperature = 100; //for temp value
int total=0;
int good=0;


void setup()
{
	init();  //initial;ise io pins etc
    pinMode(led_pin, OUTPUT);
    pinMode(led_pin+1, OUTPUT);
    total=0;
  return;
}

void loop()
{
  //do{
	  digitalWrite(led_pin, HIGH);  // set the LED on
	  digitalWrite(led_pin+1, LOW);       // set the LED off
	  delay(500);                                  // wait ms
	  digitalWrite(led_pin, LOW);       // set the LED off
	  digitalWrite(led_pin+1, HIGH);  // set the LED on
	  delay(950);                                  // wait ms
	  //initdht11();
	  if (getth() == DHTLIB_ERROR_TIMEOUT)  //get temp and humidity
		printf("timeout!!\n");
	  
	  if (total >= 10)
		delay(1000);
  //}while (total<11);
}

void initdht11()
{
    pinMode(dht11pin, OUTPUT);
    digitalWrite(dht11pin, LOW);
    printf("Pin %d low\n", dht11pin);  // Print info to the command line.
}

int getth()
{
	// BUFFER TO RECEIVE
	uint8_t bits[5];
	uint8_t cnt = 7;
	uint8_t idx = 0;
	
	int t_low = 18;
	int t_hi = 55;
	
	total+=1;
	printf("t_low ms = %i....t_hi us = %i ",t_low,t_hi);
	// EMPTY BUFFER
	int i;
	for (i=0; i< 5; i++)
	  bits[i] = 0;
	
	// REQUEST SAMPLE
	printf("sampling... ");

	pinMode(dht11pin, OUTPUT);	//set pin as op to stasrt conversion
	digitalWrite(dht11pin, LOW);	//take pin lo to initiate conv
	delay(t_low);	//wait ms
	digitalWrite(dht11pin, HIGH);	//take hi to trigger
	delayMicroseconds(t_hi);	//wait us
	/* 100						500		1000
	 * 0								.89	.92
	 * 1								.89	.82
	 * 10								.89	.93
	 * 20								.93	.92
	 * 30								.92	.89
	 * 40 .91 .89 .92 .98		.88		.88	.92
	 * 45 .90
	 * 50 .92 .89 .92			.9		.91	.9
	 * 55						.9		.88	.91
	 * 60 .94 .89 .92 .92		.9		.92	.88	.9	.91	.84
	 * 70 .86 .88				.89		.88
	 */
	 
	pinMode(dht11pin, INPUT);	//make pin ip to read data
	//delayMicroseconds(40);	//wait 40us

	// ACKNOWLEDGE or TIMEOUT
	unsigned int loopCnt = 10000;
	while(digitalRead(dht11pin) == LOW)
		if (loopCnt-- == 0) return DHTLIB_ERROR_TIMEOUT;
	
	loopCnt = 10000;
	while(digitalRead(dht11pin) == HIGH)
		if (loopCnt-- == 0) return DHTLIB_ERROR_TIMEOUT;

	// READ OUTPUT - 40 BITS => 5 BYTES or TIMEOUT
	for (i=0; i<40; i++)
	{
		loopCnt = 10000;
		while(digitalRead(dht11pin) == LOW)
			if (loopCnt-- == 0) return DHTLIB_ERROR_TIMEOUT;

		unsigned long t = micros();

		loopCnt = 10000;
		while(digitalRead(dht11pin) == HIGH)
			if (loopCnt-- == 0) return DHTLIB_ERROR_TIMEOUT;

		if ((micros() - t) > 40) bits[idx] |= (1 << cnt);
		if (cnt == 0)   // next byte?
		{
			cnt = 7;    // restart at MSB
			idx++;      // next byte!
		}
		else cnt--;
	}

	// WRITE TO RIGHT VARS
        // as bits[1] and bits[3] are allways zero they are omitted in formulas.
	
	humidity    = bits[0];
	temperature = bits[2]; 

	uint8_t sum = bits[0] + bits[2];  

	if (bits[4] != sum) {
		//bad +=1; //inc bad count
		printf("bad crc!\n");
		return DHTLIB_ERROR_CHECKSUM;
	}
	else
	{
		printf("good crc\n");
		printf("h: %i\n", humidity);
		printf("t: %i\n", temperature);
		good += 1;	//inc good count
		printf("good : %i\n", good);
		printf("total: %i\n", total);

		printf("good ratio: %0.2f \n\n", (double)good/(double)total);
		return DHTLIB_OK;
	}
}
