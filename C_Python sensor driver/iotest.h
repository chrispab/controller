#ifndef iotest_h
#define iotest_h

#define DHTLIB_OK				0
#define DHTLIB_ERROR_CHECKSUM	-1
#define DHTLIB_ERROR_TIMEOUT	-2


void setup(void);
//void initdht11(void);
void loop(void);
int getth(void);

#endif

