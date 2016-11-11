/* dht22.i */
%module dht22
%{
/* Put header files here or function declarations like below */
extern float humidity;
extern float temperature;
extern void setup();
extern void loop();
extern int getth();
%}
 
extern float humidity;
extern float temperature;
extern void setup();
extern void loop();
extern int getth();
