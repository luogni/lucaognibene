//TEST: irriga now 105,5,time garden,time orto,2 a

#include <Ports.h>
#include <RF12.h>
#include <avr/sleep.h>
#include <util/atomic.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <avr/wdt.h>

PortI2C myport (1);
DeviceI2C expander (myport, 0x20);
#define PIN_ENABLE 5

#define PIN_H1_1 1
#define PIN_H1_2 0
#define PIN_H2_1 7
#define PIN_H2_2 6
#define PIN_H3_1 5
#define PIN_H3_2 4
#define PIN_H4_1 3
#define PIN_H4_2 2

#define DELAY_CMD 50
#define DELAY_DRIIN1 200
#define DELAY_DRIIN2 2000

#define PIN_BUTTONS 2 //analog
#define DELAY_SHORT 700
#define DELAY_LONG 10000
#define TEMP_TIMER 3000

#define ONEWIRE_PIN 6 //PORT 3 DIGITAL

#define DEBUG

enum {
  MCP_IODIR, MCP_IPOL, MCP_GPINTEN, MCP_DEFVAL, MCP_INTCON, MCP_IOCON,
  MCP_GPPU, MCP_INTF, MCP_INTCAP, MCP_GPIO, MCP_OLAT
};

struct data_status {
  byte prefix;
  byte cmd;
  byte cmd_step;
  int t1;
};
struct data_status ds;

MilliTimer rftimer;
static byte myNodeID = 2;   // node ID used for this unit

byte cmd = 0;
byte cmd_step = 0;
unsigned long cmd_stop_after = 0;
unsigned long cmd_stop_after2 = 0;
unsigned long cmd_start = 0;
MilliTimer ttimer;
int b_short = 0;
int b_long = 0;
unsigned long tb_short = 0;
unsigned long tb_long = 0;
unsigned long tb_delay = 0;
byte b1_counter = 0;
byte b2_counter = 0;
byte tb_latest = 0;
DeviceAddress ow_t1 = { 0x28, 0xA3, 0xE7, 0x7D, 0x2, 0x0, 0x0, 0xEA };
OneWire oneWire(ONEWIRE_PIN);
DallasTemperature ow_sensors(&oneWire);

void setup() {
#ifdef DEBUG
  Serial.begin(57600);
  Serial.println("\n[irriga]");
#endif
  pinMode(PIN_ENABLE, OUTPUT);
  digitalWrite(PIN_ENABLE, LOW);
  exp_setup();
  irriga_stop();
  ds.t1 = 0;
  ttimer.set(TEMP_TIMER);
  rf12_initialize(myNodeID, RF12_868MHZ);
  rf12_control(0xC647);
  ow_sensors.begin();
  //wdt seems not to reset the board.. maybe bootloader fault?
  //wdt_enable(WDTO_8S);
}

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

void irriga_stop_1(byte cmd) {
  //don't set _1_2 while ENABLE is HIGH or i'll change output..
  digitalWrite(PIN_ENABLE, LOW);
  delay(DELAY_CMD);
  exp_write(1 << cmd);
  delay(DELAY_CMD);
  digitalWrite(PIN_ENABLE, HIGH);
  delay(DELAY_CMD);
  digitalWrite(PIN_ENABLE, LOW);
  delay(DELAY_CMD);  
}

void irriga_stop() {
#ifdef DEBUG
  Serial.println("Stop all");
#endif
  //don't set _1_2 while ENABLE is HIGH or i'll change output..
  delay(DELAY_CMD);
  irriga_stop_1(PIN_H1_2);
  irriga_stop_1(PIN_H2_2);
  irriga_stop_1(PIN_H3_2);
  irriga_stop_1(PIN_H4_2);
  exp_write(0);
  delay(DELAY_CMD);
  //don't reset cmd here or it'll block when a cmd is splitted in two/three..
}

void irriga_start() {
  if (cmd == 0) return ;
  cmd_start = millis();
#ifdef DEBUG
  Serial.print("Start "); Serial.print((int)cmd); Serial.print(" "); Serial.print((int)cmd_step); Serial.print(" "); Serial.println(cmd_stop_after);
  delay(10);
#endif
  //always set enable to low while changing values..
  digitalWrite(PIN_ENABLE, LOW);
  if ((cmd == 1)||((cmd == 4)&&(cmd_step == 0))||((cmd == 5)&&(cmd_step == 0))) {
    exp_write(1 << PIN_H1_1);
  }else if ((cmd == 2)||((cmd == 4)&&(cmd_step == 1))||((cmd == 5)&&(cmd_step == 1))) {
    exp_write(1 << PIN_H2_1);
  }else if ((cmd == 3)||((cmd == 5)&&(cmd_step == 2))) {
    exp_write(1 << PIN_H3_1);
  }
  if ((cmd == 5)&&(cmd_step == 2))
    cmd_stop_after = cmd_stop_after2;
  
  //now ENABLE so values are used
  digitalWrite(PIN_ENABLE, HIGH);
  delay(DELAY_CMD);
  digitalWrite(PIN_ENABLE, LOW);  
  exp_write(0);
  delay(DELAY_CMD);
}

static void doReport() {
  ds.prefix = 'z';
  ds.cmd = cmd;
  ds.cmd_step = cmd_step;
  while (!rf12_canSend())
      rf12_recvDone();
  rf12_sendStart(0, &ds, sizeof ds);
  rf12_sendWait(0);  
}

static void doMeasure() {
  byte firstTime = ds.t1 == 0; // special case to init running avg

  //ow_sensors.requestTemperatures(); // Send the command to get temperatures
  //ds.t1 = smoothedAverage(ds.t1, (int) (ow_sensors.getTempC(ow_t1) * 10 + 10), firstTime, 5);
  ds.t1 = 0;
}

void driin(unsigned int d) {
  digitalWrite(PIN_ENABLE, LOW);
  exp_write(1 << PIN_H4_1);
  digitalWrite(PIN_ENABLE, HIGH);
  delay(d);
  digitalWrite(PIN_ENABLE, LOW);
  exp_write(0);
}

// i 0 -> STOP WATER 1/2/3
// i 1 M -> WATER 1 (stop after M minutes)
// i 2 M -> WATER 2
// i 3 M -> WATER 3
// i 4 M -> WATER 1 and WATER 2 (stop 1 after M minutes, open 2, stop 2 after M minutes)
// i 5 M N -> WATER 1&2(M minutes) and than WATER 3(N minutes)
// i 6 -> DRIIIN

void parse_cmd(byte dlen, byte *ddata) {
  if ((dlen == 2)&&(ddata[1] == 0)) {
    irriga_stop();
    cmd = 0;
  }else if (dlen == 3) {
    cmd = ddata[1];
    cmd_step = 0;
    cmd_stop_after = ddata[2];
    irriga_start();
  }else if (dlen == 4) {
    cmd = ddata[1];
    cmd_step = 0;
    cmd_stop_after = ddata[2];
    cmd_stop_after2 = ddata[3];
    irriga_start(); 
  }else if ((dlen == 2)&&(ddata[1] == 6)) {
    driin(DELAY_DRIIN2);  
  }
}

void check_stop() {
  if (cmd == 0) return ;
  //check also for overflow
  if ((millis() < cmd_start)||(millis() - cmd_start > (cmd_stop_after * 60000))) {
#ifdef DEBUG
    Serial.print(millis()); Serial.print(" ");Serial.print(cmd_start);Serial.print(" ");Serial.println(cmd_stop_after);
    //i need to stop something!
    Serial.print("Stop ");Serial.print((int)cmd); Serial.print(" "); Serial.println((int)cmd_step);
    delay(10);
#endif
    irriga_stop();    
    if ((cmd == 4)&&(cmd_step == 0)) {
      //go to next step
      cmd_step = 1;
    }else if ((cmd == 5)&&((cmd_step == 0)||(cmd_step == 1))) {
      cmd_step ++;
    }else {
      //..else i don't need to run anything
      cmd = 0;
    }
    //call irriga_start.. maybe i need to go to next step
    irriga_start();
    delay(2000);
  }
}

void try_to_receive_cmd() {
  unsigned long t;
  //if there's something and it's for me and it wants a ack
  if (rf12_recvDone() && rf12_crc == 0) {
    if ((RF12_WANTS_ACK)&&((RF12_HDR_MASK & rf12_hdr) == myNodeID)) {
      if (rf12_len >= 2) {
#ifdef DEBUG
        Serial.print("cmd"); Serial.print(" "); Serial.print((int)rf12_len); Serial.print(" "); Serial.println(rf12_data[0]);
        delay(10);
#endif
        if (rf12_data[0] == 'i')  //105 ascii
          parse_cmd(rf12_len, (byte *)rf12_data);
        while (!rf12_canSend())
          rf12_recvDone();
        rf12_sendStart(RF12_HDR_ACK, 0, 0);
        rf12_sendWait(0);
      }
    }
  }
}

// utility code to perform simple smoothing as a running average
static int smoothedAverage(int prev, int next, byte firstTime, int smooth) {
    if (firstTime)
        return next;
    return ((smooth - 1) * prev + next + smooth / 2) / smooth;
}

void loop() {
  //wdt_reset();
  check_stop();
  try_to_receive_cmd(); 

  if (ttimer.poll()) {
    doMeasure();
    doReport();//send it two times so it can be received better
    doReport();
    ttimer.set(TEMP_TIMER);
  }
}
