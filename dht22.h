#ifndef dht22_h
#define dht22_h

#define DHTLIB_OK				0
#define DHTLIB_ERROR_CHECKSUM	-1
#define DHTLIB_ERROR_TIMEOUT	-2


void setup(void);
void loop(void);
int getth(void);

#endif

