#include <JeeLib.h>

Port one (1);
Port two (2);
static byte myNodeID = 50;
unsigned byte one_value = 0;
unsigned byte two_value = 0;

void setup() {
  one.mode(OUTPUT);
  two.mode(OUTPUT);
  one.anaWrite(one_value);
  two.anaWrite(two_value);
  rf12_initialize(myNodeID, RF12_868MHZ);
  //rf12_control(0xC647);
}

void parse_cmd(byte dlen, byte *ddata) {
  if ((dlen == 4)&&(ddata[1] == 'M')) {
    one_value = ddata[2];
    two_value = ddata[3];
    return 1;
  }
  return 0;
}

// C M ONEVALUE TWOVALUE   (67 77 ascii)
void try_to_receive_cmd() {
  unsigned long t;
  //if there's something and it's for me
  if (rf12_recvDone() && rf12_crc == 0) {
    if (((RF12_HDR_MASK & rf12_hdr) == myNodeID)) {
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

void loop() {
  int change = 0;
  change = try_to_receive_cmd(); 
  if (change > 0) {
    one.anaWrite(one_value);
    two.anaWrite(two_value);
  }
}
