#include <JeeLib.h>

PortI2C myport (1 /*, PortI2C::KHZ400 */);
DeviceI2C expander (myport, 0x20); // also works with output plug if 0x26/0x27

enum {
  MCP_IODIR, MCP_IPOL, MCP_GPINTEN, MCP_DEFVAL, MCP_INTCON, MCP_IOCON,
  MCP_GPPU, MCP_INTF, MCP_INTCAP, MCP_GPIO, MCP_OLAT
};

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
	Serial.begin(57600);
	Serial.println("\n[expander]");
    exp_setup();
}

void loop() {	
	// running light
    exp_write(1);
}

