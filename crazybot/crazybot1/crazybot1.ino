#include <JeeLib.h>

Port reverse (1);
Port one (3);
Port two (2);
static byte myNodeID = 20;
byte one_value = 0;
byte two_value = 0;
byte reverse_value = 0;

int startBit   = 2000;   // This pulse sets the threshold for a transmission start bit
int senderPin  = 7;      // Infrared LED on Pin 3
int waitTime = 300;     // The amount of time to wait between pulses
int endBit     = 3000;  // This pulse sets the threshold for an end bit
int vOne        = 1000;   // This pulse sets the threshold for a transmission that 
                         // represents a 1
int vZero       = 400;    // This pulse sets the threshold for a transmission that 
                         // represents a 0
unsigned long time;

//#define DEBUG

void setup() {
  reverse.mode(OUTPUT);
  one.mode(OUTPUT);
  two.mode(OUTPUT);
  one.anaWrite(one_value);
  two.anaWrite(two_value);
  reverse.digiWrite(reverse_value);
  rf12_initialize(myNodeID, RF12_868MHZ);
  //rf12_control(0xC647);
#ifdef DEBUG
  Serial.begin(57600);
  Serial.println("\n[crazybot]");
#endif
  pinMode(senderPin, OUTPUT);
  time = 0;
}

byte parse_cmd(byte dlen, byte *ddata) {
  if ((dlen == 5)&&(ddata[1] == 'M')) {
    one_value = ddata[2];
    two_value = ddata[3];
    reverse_value = ddata[4];
    return 1;
  }
  return 0;
}

// C M ONEVALUE TWOVALUE   (67 77 ascii)
byte try_to_receive_cmd() {
  unsigned long t;
  //if there's something and it's for me
  if (rf12_recvDone() && rf12_crc == 0) {
    if (((RF12_HDR_MASK & rf12_hdr) == myNodeID)) {
#ifdef DEBUG
        Serial.print("cmd"); Serial.print(" "); Serial.print((int)rf12_len); Serial.print(" "); Serial.println(rf12_data[0]);
        delay(10);
#endif
      if (rf12_len >= 2) {
        if (rf12_data[0] == 'C')
          return parse_cmd(rf12_len, (byte *)rf12_data);
        /* while (!rf12_canSend())
          rf12_recvDone();
        rf12_sendStart(RF12_HDR_ACK, 0, 0);
        rf12_sendWait(0); */
      }
    }
  }
}

void fireShot(int player, int level) {
  Serial.println("fire!");
  int encoded[8];
  for (int i=0; i<4; i++) {
    encoded[i] = bitRead(player, i);
  }
  for (int i=4; i<8; i++) {
    encoded[i] = bitRead(level, i - 4);
  }
  // send startbit
  oscillationWrite(senderPin, startBit);
  // send separation bit
  digitalWrite(senderPin, HIGH);
  delayMicroseconds(waitTime);
  // send the whole string of data
  for (int i=7; i>=0; i--) {
    if (encoded[i] == 0) {
      oscillationWrite(senderPin, vZero);
    } else {
      oscillationWrite(senderPin, vOne);
    }
    // send separation bit
    digitalWrite(senderPin, HIGH);
    delayMicroseconds(waitTime);
  }
  oscillationWrite(senderPin, endBit);
}

void oscillationWrite(int pin, int time) {
  for(int i = 0; i <= time/26; i++) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(13);
    digitalWrite(pin, LOW);
    delayMicroseconds(13);
  }
}

void loop() {
  int change = 0;
  change = try_to_receive_cmd(); 
  if (change > 0) {
    one.anaWrite(one_value);
    two.anaWrite(two_value);
    reverse.digiWrite(reverse_value);
  }
  if (millis() - time > 1000) {
     time = millis();
     fireShot(3, 7); 
  }
}
