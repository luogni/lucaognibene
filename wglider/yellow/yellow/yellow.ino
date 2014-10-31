#include <JeeLib.h>

//FIXME:
// * measure voltage only with no load
// * change minimum (3.8 per cell)

PortI2C eport (4);

Port one (3);
Port rev (2);
static byte myNodeID = 21;
byte one_value = 0;
byte reverse_value = 0;
MilliTimer autotimer, batterytimer;
byte mode = 0;
//#define DEBUG
#define BATTERYMIN (0)     // nimh
#define BATTERYMIN (7000)  // lipo 2s

struct data_status {
  byte prefix;
  int batterylevel;
};
struct data_status ds;

void setup() {
  one.mode(OUTPUT);
  one.mode2(INPUT);
  one.anaWrite(one_value);
  rev.mode(OUTPUT);
  rev.digiWrite(reverse_value);
  rf12_initialize(myNodeID, RF12_868MHZ);
  //rf12_control(0xC647);
#ifdef DEBUG
  Serial.begin(57600);
  Serial.println("\n[yellow]");
#endif
}

static void doReport(int bl) {
  ds.prefix = 'Y';
  ds.batterylevel = bl;
  while (!rf12_canSend())
      rf12_recvDone();
  rf12_sendStart(0, &ds, sizeof ds);
  rf12_sendWait(0);  
}

byte parse_cmd(byte dlen, byte *ddata) {
  if ((dlen == 5)&&(ddata[1] == 'M')) {
    one_value = ddata[2];
    reverse_value = ddata[3];
    return 1;
  }
  return 0;
}

// W M ONEVALUE TWOVALUE   (87 77 ascii)
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
        if (rf12_data[0] == 'W')
          return parse_cmd(rf12_len, (byte *)rf12_data);
      }
    }
  }
}

void loop() {
  int change = 0;
  change = try_to_receive_cmd();
  if (change > 0) {
    one.anaWrite(one_value);
    rev.digiWrite(reverse_value);
  }
  if (autotimer.poll(30000)) {
    mode ++;
    if (mode == 4) mode = 0;
    if (mode == 0) {
      reverse_value = 0;
      one_value = 255;
    }else if ((mode == 1)or(mode == 3)) {
      reverse_value = 0;
      one_value = 0;
    }else if (mode == 2) {
      reverse_value = 1;
      one_value = 255;
    }
    one.anaWrite(one_value);
    rev.digiWrite(reverse_value);
  }
  if ((one_value == 0)&&(batterytimer.poll(60000))) {
    int data = one.anaRead();
    // 27 and 68 are voltage divider resistors, 11.33 is (3.3 / 1024) * ((27 + 68.0) / 27.0) * 1000    
    int bv = data * 11.33;
#ifdef DEBUG
    Serial.print("battery "); Serial.print(data); Serial.print(" "); Serial.println(bv);
#endif
    doReport(bv);
    if (bv < BATTERYMIN) {
      while (true) {delay(60000);};
    }      
  }
}
