
/*
* Getting Started example sketch for nRF24L01+ radios
* This is a very basic example of how to send data from one node to another
* Updated: Dec 2014 by TMRh20
*/

#include <SPI.h>
#include "RF24.h"

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(7, 8);
/**********************************************************/

void setup() {
  Serial.begin(57600);
  Serial.println(F("RF24/examples/GettingStarted"));
  
  radio.begin();

  radio.setPALevel(RF24_PA_LOW);
  radio.setAutoAck(1);
  
  radio.openWritingPipe(0xF0F0F0F0BB);
  radio.openReadingPipe(1, 0xF0F0F0F0AA);

  radio.startListening();
}

void loop() {
 byte data[30];
 byte senddata[30] = {43, 44, 45, 46}; 
 if( radio.available()){
    while (radio.available()) {                                   // While there is data ready
      radio.read(&data, 20);
    }
    for (int i=0; i<30; i++) {
      Serial.print(data[i]); Serial.print(" ");
    }
    Serial.println();
    radio.stopListening();
    radio.write(&senddata, 5);
    radio.startListening();
 }
}

