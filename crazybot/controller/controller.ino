#include <SPI.h>
#include "RF24.h"

#define MAXLEN (10)

RF24 radio(7, 8);

void setup() {
  Serial.begin(57600);
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.setAutoAck(1);
  radio.setRetries(2, 15);
  radio.openWritingPipe(0xF0F0F0F0AA);
  radio.openReadingPipe(1, 0xF0F0F0F0BB);
  radio.startListening();
}

void set_writing_address(byte addr) {
    uint64_t addr2 = 0xF0F0F0F000 + addr;
    radio.stopListening();
    radio.openWritingPipe(addr2);
    radio.startListening();
}

void send_data(byte data[], int length) {
  radio.stopListening();
  //Serial.println("Sending");
  if (!radio.write(data, length)) {
    Serial.println(F("Sending failed"));
  }
  radio.startListening();
}

void loop() {  
  byte data[MAXLEN + 1];
  while (Serial.available() > 0) {
    int count = 0;
    int prefix = Serial.parseInt();
    if (prefix != 42) continue;
    int len = Serial.parseInt();
    if ((len > MAXLEN)or(len == 0)) continue;
    
    while (count < len) {
      data[count] = (byte) Serial.parseInt();
      count ++;
    }
    
    if (data[0] == 'i') { // i 105
      set_writing_address(data[1]);
    }else if (data[0] == 'w') {  // w 119
      send_data(data, len);
    }
  }

  if (radio.available()) {
    radio.read(data, MAXLEN);
    for (int i=0; i<MAXLEN; i++) {
      Serial.print(data[i]); Serial.print(",");
    }
    Serial.println("E");
  }
}

