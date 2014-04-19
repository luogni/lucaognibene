#include <JeeLib.h>

PortI2C eport (4);
DeviceI2C expander (eport, 0x20); // also works with output plug if 0x26/0x27

enum {
  MCP_IODIR, MCP_IPOL, MCP_GPINTEN, MCP_DEFVAL, MCP_INTCON, MCP_IOCON,
  MCP_GPPU, MCP_INTF, MCP_INTCAP, MCP_GPIO, MCP_OLAT
};

Port one (3);
Port two (2);
static byte myNodeID = 20;
byte one_value = 0;
byte two_value = 0;
byte reverse_value = 0;

#define EP_REVERSE1 0
#define EP_REVERSE2 1

//#define DEBUG


static void exp_setup () {
    expander.send();
    expander.write(MCP_IODIR);
    expander.write(0); // all outputs
    expander.stop();
}

static void exp_write (byte value) {
    expander.send();
    expander.write(MCP_GPIO);
    expander.write(value);
    expander.stop();
}

void setup() {
  one.mode(OUTPUT);
  two.mode(OUTPUT);
  one.anaWrite(one_value);
  two.anaWrite(two_value);
  exp_setup();
  rf12_initialize(myNodeID, RF12_868MHZ);
  //rf12_control(0xC647);
#ifdef DEBUG
  Serial.begin(57600);
  Serial.println("\n[crazybot]");
#endif
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

void loop() {
  int change = 0;
  change = try_to_receive_cmd(); 
  if (change > 0) {
    one.anaWrite(one_value);
    two.anaWrite(two_value);
    exp_write((reverse_value << EP_REVERSE1) | (reverse_value << EP_REVERSE2));
  }
}
