#include <Ports.h>
#include <RF12.h> 

PortI2C myport (1);
DeviceI2C expander (myport, 0x20);
#define PIN_ENABLE 5

enum {
  MCP_IODIR, MCP_IPOL, MCP_GPINTEN, MCP_DEFVAL, MCP_INTCON, MCP_IOCON,
  MCP_GPPU, MCP_INTF, MCP_INTCAP, MCP_GPIO, MCP_OLAT
};

static void exp_write (byte value) {
  expander.send();
  expander.write(MCP_GPIO);
  expander.write(value);
  expander.stop();
}

static void exp_setup () {
  expander.send();
  expander.write(MCP_IODIR);
  expander.write(0); // all outputs
  expander.stop();
}

void setup() {
  pinMode(PIN_ENABLE, OUTPUT);
  exp_setup();
}

void loop() {
  digitalWrite(PIN_ENABLE, LOW);
  delay(3000);

  digitalWrite(PIN_ENABLE, LOW);
  exp_write(1 << 0);
  digitalWrite(PIN_ENABLE, HIGH);
  delay(20);
  
  digitalWrite(PIN_ENABLE, LOW);
  delay(3000);
  
  digitalWrite(PIN_ENABLE, LOW);
  exp_write(1 << 1);
  digitalWrite(PIN_ENABLE, HIGH);
  delay(20);
}
