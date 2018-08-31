/*
=================================================================================
 Name        : wdt_test.c
 Version     : 0.1

 Copyright (C) 2012 by Andre Wussow, 2012, desk@binerry.de

 Description :
     A simple test for working with the Raspberry Pi BCM2835 Watchdog.
	 
 References  :
 http://binerry.de/post/28263824530/raspberry-pi-watchdog-timer

================================================================================
This sample is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This sample is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.
================================================================================
 */
#include <stdio.h>
#include <fcntl.h>
#include <linux/watchdog.h> 
 
int main (int argc, char *argv[])
{
	// print infos
	printf("Raspberry Pi BCM2835 my_watchdog Sample\n");
	printf("========================================\n");
  
	int deviceHandle;
	int disableWatchdog = 1;
    int runForever = 0;
	
	// test watchdog reset via t-param
	if (argc > 1) {
		if (!strncasecmp(argv[1], "-t", 2)) {
			disableWatchdog = 0;
		}
		if (!strncasecmp(argv[1], "-r", 2)) {
			runForever = 1;
		}
	}
	
	printf("Disabling my_watchdog before closing device: %d\n", disableWatchdog);

	// open watchdog device on /dev/watchdog
	if ((deviceHandle = open("/dev/watchdog", O_RDWR | O_NOCTTY)) < 0) {
		printf("Error: Couldn't open my_watchdog device! %d\n", deviceHandle);
		return 1;
	} 
	
	// get timeout info of watchdog (try to set it to 15s before)
	int timeout = 15;
	ioctl(deviceHandle, WDIOC_SETTIMEOUT, &timeout);
	ioctl(deviceHandle, WDIOC_GETTIMEOUT, &timeout);
	printf("The my_watchdog timeout is %d seconds.\n\n", timeout);
  
    int runTime = 0;
	int pat_interval = 10;  
    //if run forver
    if (runForever == 1) {
        while (1) {
            printf("Watchdog Run time : %d seconds.\n", runTime );
            runTime = runTime + pat_interval;
            ioctl(deviceHandle, WDIOC_KEEPALIVE, 0);
            sleep(pat_interval);
        }
    }
    
        
	// feed watchdog n times with heartbeats
    int n = 18;

    int prot_time = pat_interval*n;
	printf("Total protection time = %d seconds.\n", prot_time );

    int i;
	for (i = 0; i < n; i++) {
		printf("Patting my_watchdog every %d seconds.\n", pat_interval);
		

		ioctl(deviceHandle, WDIOC_KEEPALIVE, 0);
		sleep(pat_interval);
        prot_time=prot_time - pat_interval;
        printf("Protection left : %d seconds.\n", prot_time );
	}
	
	if (disableWatchdog)
	{
		printf("Disabling my_watchdog.\n");
		write(deviceHandle, "V", 1);
	}
	
	// close connection and return
	close(deviceHandle);
	return 0;
}
