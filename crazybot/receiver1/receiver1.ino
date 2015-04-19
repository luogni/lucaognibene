#include <SPI.h>
#include "RF24.h"

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(9, 10);
const int m1powPin = 3;
const int m1revPin = 4;
const int m2powPin = 6;
const int m2revPin = 7;
const int battPin = A0;

#define DEBUG
//#define BATTERYMIN (0)     // nimh
#define BATTERYMIN (7200)  // lipo 2s


void setup() {
  Serial.begin(57600);
  Serial.println(F("Crazybot"));

  pinMode(m1powPin, OUTPUT);
  pinMode(m1revPin, OUTPUT);
  pinMode(m2powPin, OUTPUT);
  pinMode(m2revPin, OUTPUT);
  pinMode(battPin, INPUT);
  
  radio.begin();

  radio.setPALevel(RF24_PA_LOW);
  radio.setAutoAck(1);
  
  radio.openWritingPipe(0xF0F0F0F0BB);
  radio.openReadingPipe(1, 0xF0F0F0F0AA);

  radio.startListening();
}

void setMotor(char m, unsigned char mspeed, char rev) {
  if (m == 1) {
    digitalWrite(m1revPin, rev);
    analogWrite(m1powPin, mspeed);
  }else {
    digitalWrite(m2revPin, rev);
    analogWrite(m2powPin, mspeed);    
  }
}

int getBattery() {
  int bv;
  int data = analogRead(battPin);
  // 27 and 68 are voltage divider resistors, 11.33 is (3.3 / 1024) * ((27 + 68.0) / 27.0) * 1000    
  bv = data * 11.33;
#ifdef DEBUG
    Serial.print("battery "); Serial.print(data); Serial.print(" "); Serial.println(bv);
#endif
  return bv;
}

void doBattery() {
  int bv;
  bv = getBattery();
  if (bv < BATTERYMIN) {
    while (true) {delay(6000);};
  }  
}

void loop() {
 byte data[30];
 byte senddata[30] = {43, 44, 45, 46}; 
 if( radio.available()){
    while (radio.available()) {                                   // While there is data ready
      radio.read(&data, 20);
    }
    if (data[0] == 119) {
      Serial.print(data[1]); Serial.print(" ");
      Serial.print(data[2]); Serial.print(" ");      
      Serial.print(data[3]); Serial.println(" ");
      setMotor(1, data[1], data[3]);
      setMotor(2, data[2], data[3]);
    }
    //for (int i=0; i<30; i++) {
      
      //Serial.print(data[i]); Serial.print(" ");
    //}
    //Serial.println();
    //radio.stopListening();
    //radio.write(&senddata, 5);
    //radio.startListening();
 }
}

