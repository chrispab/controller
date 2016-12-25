/* dht11.i */
 %module dht11
 %{
 /* Put header files here or function declarations like below */
#include "dht11.h"
 %}
 
class dht11
{
public:
    int read(int pin);
	int humidity;
	int temperature;
};