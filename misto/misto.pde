#include <ModbusSlave.h>

#include <Ports.h>
#include <PortsLCD.h>
#include <RF12.h>
#include <avr/sleep.h>
#include <util/atomic.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define LCD_PORT 2
#define RTC_PORT 2
#define BUTTONS_PORT 3
#define MEM_PORT 2
#define ONEWIRE_PIN 4//PORT 1 DIGITAL
#define SOUND_PIN 0 //PORT 1 ANALOG

DeviceAddress ow_t1 = { 0x28, 0x54, 0xFC, 0xBA, 0x2, 0x0, 0x0, 0xAE };
DeviceAddress ow_t2 = { 0x28, 0xCE, 0xEE, 0x7D, 0x2, 0x0, 0x0, 0x90 };
DeviceAddress ow_t3 = { 0x28, 0x46, 0x57, 0x7E, 0x2, 0x0, 0x0, 0xEF };
DeviceAddress ow_t4 = { 0xaa, 0xaa, 0xE7, 0x7D, 0x2, 0x0, 0x0, 0xEA };

PortI2C lcdI2C (LCD_PORT);
LiquidCrystalI2C lcd (lcdI2C);
PortI2C rtcI2C (RTC_PORT);
DeviceI2C rtc (rtcI2C, 0x68);
BlinkPlug buttons (BUTTONS_PORT);
MilliTimer intimer, soundtimer, irrigatimer, modbustimer, irrigapingtimer;
PortI2C membus (MEM_PORT);
MemoryPlug mem (membus);
OneWire oneWire(ONEWIRE_PIN);
DallasTemperature ow_sensors(&oneWire);
ModbusSlave mbs;

#define RETRY_PERIOD    10  // how soon to retry if ACK didn't come in
#define RETRY_LIMIT     30   // maximum number of times to retry
#define ACK_TIME        100  // number of milliseconds to wait for an ack
#define SMOOTH          3   // smoothing factor used for running averages
#define SMOOTH_SOUND    5
#define LCD_OFF_AFTER   10000 //set LCD backlight off after N ms
#define DSPAGE_SIZE     20  // keep some bytes so i can have free space for later
#define DSPAGE_START    5  
#define DS_IN_PAGE      (256 / DSPAGE_SIZE) //if DSPAGE_SIZE is 10 there are 25 ds in a page
#define WRITE_TIME      180 //write after N MEASURE_TIME times
#define MEASURE_TIME    5000
#define IRRIGA_PING_TIMER 5000
#define IRRIGA_CHECK_TIMER 10000
#define MEASURE_SOUND_TIME 500
#define SOUND_CHECK_CHANGE 5
#define SOUND_THRE 30
#define IRRIGA_PING_OK 40000
//#define MODBUS_TIME 5000

static byte myNodeID = 1;   // node ID used for this unit

byte page = 0;
byte lcd_off = 0;
uint32_t lcd_last_ping = 0;
int mem_counter = 0;
int write_counter = 0;
int sound_change = 0;
int sound_oldval = 0;
byte sound_check_change = 0;
uint32_t irriga_last_ping = 0;
byte irriga_last_status = 0;
byte irriga_sent = 0;

enum {        
        MB_T1,
        MB_T2,
        MB_T3,
        MB_T4,          // irriga
        MB_IRRIGA_STATUS, //0 -> ko, 1 -> ok, 2 -> doing something
        MB_IRRIGA_DATE1, //day of month
        MB_IRRIGA_DATE2, //hour
        MB_IRRIGA_DATE3, //minute
        MB_IRRIGA_V1, //giardino
        MB_IRRIGA_V2, //orto
        MB_IRRIGA_CMD_V1, //cmd to water now.. V1&V2
        MB_IRRIGA_CMD_V2,
        MB_IRRIGA_CMD, // 0 -> no cmd, 1 -> water now, 2 -> stop
        MB_REGS	 	/* total number of registers on slave */
};

int regs[MB_REGS];

// has to be defined because we're using the watchdog for low-power waiting
ISR(WDT_vect) { Sleepy::watchdogEvent(); }

//        mem.save(100, "abc", 123, 3);
//        mem.load(100, buf, 122, 5);

/* REPLY */
struct data_status {
  byte date[6];
  byte cmd;
  int t1;
  int t2;
  int t3;
  int t4;
  byte lobat :1;
  byte sound_alarm :1;
};
struct data_status ds;

struct irriga_cmd {
  byte date[3]; //day of month multiple of N, hour, minutes
  byte cmd;  //1,2,3,4,5
  byte v1;   //giardino
  byte v2;   //orto
};
struct irriga_cmd ic;

/* */

/* ************************************ */
/* ************************************ */
/* ************************************ */
/* MEMORY functions */
/* memory pages are 256bytes, offset is 0..255 in that page, count number of bytes to read/write. 512 pages.*/
/* ************************************ */
static void get_page_offset (int c, int *page, byte *offset) {
  *page = DSPAGE_START + c / DS_IN_PAGE;
  *offset = c % DS_IN_PAGE;
}

static void save_ds () {
  int page;
  byte offset;
  byte cc[2];
  
  get_page_offset(mem_counter, &page, &offset);
  mem.save(page, &ds, offset*DSPAGE_SIZE, sizeof ds);
  cc[0] = mem_counter / 256;
  cc[1] = mem_counter % 256;
  mem.save(0, cc, 0, sizeof cc);
  mem_counter ++;
  //check mem overflow and stay safe..
  if (mem_counter >= DS_IN_PAGE * (512 - DSPAGE_START)) {
    mem_counter = 0;
  }
}

static void clear_mem() {
  int p;
  byte o;
  byte d[256];
  memset(d, 0, sizeof d);
  for (p=0; p<512; p++)
    mem.save(p, d, 0, sizeof d);
  mem_counter = 0;
}

static int load_counter () {
  byte cc[2];
  int r;
  mem.load(0, cc, 0, sizeof cc);  
  r = cc[0]*256 + cc[1];
  return r;
}

static void load_irriga_cmd () {
  mem.load(1, &ic, 0, sizeof ic);  
}

static void save_irriga_cmd() {
  mem.save(1, &ic, 0, sizeof ic);  
}

static void setIrrigaCmd (byte d, byte h, byte m, byte cmd, byte v1, byte v2) {
  ic.date[0] = d;
  ic.date[1] = h;
  ic.date[2] = m;
  ic.cmd = cmd;
  ic.v1 = v1;
  ic.v2 = v2;
  save_irriga_cmd();
}

static struct data_status load_ds (int c) {
  struct data_status dsg;
  int page;
  byte offset;
  
  get_page_offset(c, &page, &offset);
  mem.load(page, &dsg, offset*DSPAGE_SIZE, sizeof dsg);
  return dsg;
}

/* ************************************ */
/* ************************************ */
/* ************************************ */
/* RTC functions */
/* ************************************ */
static byte bin2bcd (byte val) {
  return val + 6 * (val / 10);
}

static byte bcd2bin (byte val) {
  return val - 6 * (val >> 4);
}

static void setDate (byte yy, byte mm, byte dd, byte h, byte m, byte s) {
  rtc.send();
  rtc.write(0);
  rtc.write(bin2bcd(s));
  rtc.write(bin2bcd(m));
  rtc.write(bin2bcd(h));
  rtc.write(bin2bcd(0));
  rtc.write(bin2bcd(dd));
  rtc.write(bin2bcd(mm));
  rtc.write(bin2bcd(yy));
  rtc.write(0);
  rtc.stop();
}

static void getDate (byte* buf) {
  rtc.send();
  rtc.write(0);	
  rtc.stop();
  rtc.receive();
  buf[5] = bcd2bin(rtc.read(0));
  buf[4] = bcd2bin(rtc.read(0));
  buf[3] = bcd2bin(rtc.read(0));
  rtc.read(0);
  buf[2] = bcd2bin(rtc.read(0));
  buf[1] = bcd2bin(rtc.read(0));
  buf[0] = bcd2bin(rtc.read(1));
  rtc.stop();
}
/*
void printDate() {
  byte now[6];
  getDate(now);

  Serial.print("rtc");
  for (byte i = 0; i < 6; ++i) {
    Serial.print(' ');
    Serial.print((int) now[i]);
  }
  Serial.println();
}
*/
/* */

void setup() {
  //Serial.begin(57600);
  //Serial.println("\n[misto]");
  mbs.configure(1,9600,'n',0);
  lcd.begin(16, 2);
  lcd.print("Starting!");
  ow_sensors.begin();
  intimer.set(MEASURE_TIME);
  soundtimer.set(MEASURE_SOUND_TIME);
  irrigatimer.set(IRRIGA_CHECK_TIMER);
  irrigapingtimer.set(IRRIGA_PING_TIMER);
  rf12_initialize(myNodeID, RF12_868MHZ);
  //less bandwidth more range!
  rf12_control(0xC647);  
  //use this line to set/correct time  
  //setDate(111, 03, 28, 12, 37, 0);
  ds.t1 = 0;
  ds.t2 = 0;
  ds.t3 = 0;
  ds.t4 = 0;
  lcd_off = 0;
  lcd_last_ping = millis();
  mem_counter = load_counter();
  load_irriga_cmd();
}

//FIXME: send driin cmd when there is sound alarm        

// utility code to perform simple smoothing as a running average
static int smoothedAverage(int prev, int next, byte firstTime, int smooth) {
    if (firstTime)
        return next;
    return ((smooth - 1) * prev + next + smooth / 2) / smooth;
}

static void doReport() {
  ds.cmd = 1;
  while (!rf12_canSend())
      rf12_recvDone();
  rf12_sendStart(0, &ds, sizeof ds);
  rf12_sendWait(0);  
}

static void doLoad(byte s1, byte s2, byte e1, byte e2) {
  int ms = s1 * 256 + s2;
  int me = e1 * 256 + e2;
  int i;
  for (i=ms; i<me; i++) {
    struct data_status dsg = load_ds(i);
    dsg.cmd = 2;
    while (!rf12_canSend())
      rf12_recvDone();
    rf12_sendStart(0, &dsg, sizeof dsg);
    rf12_sendWait(0);    
    delay(10);
  }
}
/*
static void doSoundMeasure() {
  int val = analogRead(SOUND_PIN); 
  sound_oldval = smoothedAverage(sound_oldval, val, sound_check_change == 0, SMOOTH_SOUND);    
  //Serial.print(val); Serial.print(" "); Serial.println(sound_oldval);
  if ((val == sound_oldval)&&(val != sound_change)&&(sound_check_change == 1)) {
    sound_change = sound_oldval;
    Serial.print("new sound change "); Serial.println(sound_change);    
  }
  if (sound_check_change == 0)
    sound_check_change = SOUND_CHECK_CHANGE;
  if ((val > sound_change + SOUND_THRE)&&(sound_change > 0)) {
    Serial.print("sound alarm "); Serial.println(val);
    ds.sound_alarm = 1;
    buttons.ledOn(1);
  }else 
    buttons.ledOff(1);
  sound_check_change --;
}
*/

static void doMeasure() {
  byte firstTime = ds.t1 == 0; // special case to init running avg

  ow_sensors.requestTemperatures(); // Send the command to get temperatures
  //it seems sensors are 1C off
  ds.t1 = smoothedAverage(ds.t1, (int) (ow_sensors.getTempC(ow_t1) * 10 + 10), firstTime, SMOOTH);
  ds.t2 = smoothedAverage(ds.t2, (int) (ow_sensors.getTempC(ow_t2) * 10 + 10), firstTime, SMOOTH);
  ds.t3 = smoothedAverage(ds.t3, (int) (ow_sensors.getTempC(ow_t3) * 10 + 10), firstTime, SMOOTH);
  //ds.t4 = smoothedAverage(ds.t4, (int) (ow_sensors.getTempC(ow_t4) * 10 + 10), firstTime, SMOOTH);
  
  getDate(ds.date);
  ds.lobat = rf12_lowbat();
  
  write_counter ++;
  if (write_counter > WRITE_TIME) {
    write_counter = 0;
    //don't save right now.. i'm not using it and it seems to make modbus hang
    //save_ds();
    //set to 0.. i want to report sound_alarm if it was high in last report_time
    ds.sound_alarm = 0;
  }  
}

static byte waitForAck() {
  MilliTimer ackTimer;
  while (!ackTimer.poll(ACK_TIME)) {
    if (rf12_recvDone() && rf12_crc == 0)
      return 1;
  }
  return 0;
}

void sendIrrigaCmd(int cmd, int v1, int v2) {
  byte payload[5];
  byte len=0;
  if (cmd == 5) {       //water everything
    payload[0] = 'i';
    payload[1] = 5;
    payload[2] = v1;
    payload[3] = v2;
    len = 4;  
  }else if (cmd == 0) {  //stop
    payload[0] = 'i';
    payload[1] = 0;
    len = 2;
  }else if (cmd == 7) {  //ping
    payload[0] = 'i';
    payload[1] = 7;
    len = 2;    
  }else
    return ;
  for (byte i = 0; i < RETRY_LIMIT; ++i) {
    while (!rf12_canSend())
      rf12_recvDone();
    rf12_sendStart(RF12_HDR_ACK | RF12_HDR_DST | 2, &payload, len);
    rf12_sendWait(0);
    byte acked = waitForAck();
    if (acked) {
      return;
    }
  }
}

void checkIrriga() {
  byte now[6];
  byte is_date;

  getDate(now);
  is_date = (((now[2] % ic.date[0]) == 0)&&(now[3] == ic.date[1])&&(now[4] == ic.date[2]));
  //some debug
  ds.date[0] = now[2];
  ds.date[1] = ic.date[0];
  ds.date[2] = now[3];
  ds.date[3] = ic.date[1];
  ds.date[4] = now[4];
  ds.date[5] = ic.date[2];
  doReport();
  if ((irriga_sent == 0)&&(is_date == 1)) {
    //send cmd but only a single time!  
    sendIrrigaCmd(ic.cmd, ic.v1, ic.v2);
    //do report to debug
    doReport();
    irriga_sent = 1;
  }
  if ((irriga_sent == 1)&&(is_date == 0)) {
    //reset irriga sent if i've already sent it
    irriga_sent = 0;
  }
}

void afterModbus() {
  if ((ic.date[0] != regs[MB_IRRIGA_DATE1])||(ic.date[1] != regs[MB_IRRIGA_DATE2])||(ic.date[2] != regs[MB_IRRIGA_DATE3])||\
      (ic.v1 != regs[MB_IRRIGA_V1])||(ic.v2 != regs[MB_IRRIGA_V2])) {
    setIrrigaCmd(regs[MB_IRRIGA_DATE1], regs[MB_IRRIGA_DATE2], regs[MB_IRRIGA_DATE3], 5, regs[MB_IRRIGA_V1], regs[MB_IRRIGA_V2]);  
    //do report as debug to know when i've saved data..
    doReport();
  }
  if (regs[MB_IRRIGA_CMD] == 1) {
    sendIrrigaCmd(5, regs[MB_IRRIGA_CMD_V1], regs[MB_IRRIGA_CMD_V2]);
  }
  if (regs[MB_IRRIGA_CMD] == 2) {
    sendIrrigaCmd(0, 0, 0);
  }
}

void beforeModbus() {
  regs[MB_T1] = ds.t1;
  regs[MB_T2] = ds.t2;
  regs[MB_T3] = ds.t3;
  regs[MB_T4] = ds.t4;
  if ((millis() - irriga_last_ping > IRRIGA_PING_OK)||(irriga_last_ping == 0))
    regs[MB_IRRIGA_STATUS] = 0;
  else if (irriga_last_status == 0)
    regs[MB_IRRIGA_STATUS] = 1;
  else
    regs[MB_IRRIGA_STATUS] = irriga_last_status;
  regs[MB_IRRIGA_DATE1] = ic.date[0];
  regs[MB_IRRIGA_DATE2] = ic.date[1];
  regs[MB_IRRIGA_DATE3] = ic.date[2];
  regs[MB_IRRIGA_V1] = ic.v1;
  regs[MB_IRRIGA_V2] = ic.v2;
  regs[MB_IRRIGA_CMD] = 0;
}

void loop() {
  byte btnCheck, ret;
  if (rf12_recvDone() && rf12_crc == 0) {
    if (rf12_len >= 1) {
      if (rf12_data[0] == 'd')  //100 ascii
        doReport();
      else if (rf12_data[0] == 'l') //108 ascii
        doLoad(rf12_data[1], rf12_data[2], rf12_data[3], rf12_data[4]);
      else if (rf12_data[0] == 't') //116 ascii
        setDate(rf12_data[1], rf12_data[2], rf12_data[3], rf12_data[4], rf12_data[5], rf12_data[6]);
      else if (rf12_data[0] == 'c') //99 ascii
        clear_mem();
      else if (rf12_data[0] == 'z') { //122 ascii
        ds.t4 = rf12_data[3] + rf12_data[4]*255; //sent from irriga
        irriga_last_ping = millis();
        irriga_last_status = rf12_data[1];
      }else if (rf12_data[0] == 'k') {
        setIrrigaCmd(rf12_data[1], rf12_data[2], rf12_data[3], rf12_data[4], rf12_data[5], rf12_data[6]);
      }
    }
  }
/*  
  if (soundtimer.poll()) {
    doSoundMeasure();
    soundtimer.set(MEASURE_SOUND_TIME);
  }
*/  
  beforeModbus();
  ret = mbs.update(regs, MB_REGS);
  if (ret > 4) 
    afterModbus();

  if (intimer.poll()) {
    doMeasure();
    intimer.set(MEASURE_TIME);
  }

  if (irrigatimer.poll()) {
    checkIrriga();
    irrigatimer.set(IRRIGA_CHECK_TIMER);
  }
  
  if (irrigapingtimer.poll()) {
    sendIrrigaCmd(7, 0, 0);
    irrigapingtimer.set(IRRIGA_PING_TIMER);  
  }

  lcd.setCursor(0, 0);
  if (page == 0){
    if (ds.t1 >= 0) {
      char tt[16];
      sprintf(tt, "Temp %02d.%d       ", 
                (int)ds.t4/10, (int)(((float)(ds.t4/10.0) - (int)ds.t4/10)*10));
      lcd.print(tt);
      
      sprintf(tt, "%02d.%d %02d.%d %02d.%d ", 
                (int)ds.t1/10, (int)(((float)(ds.t1/10.0) - (int)ds.t1/10)*10),
                (int)ds.t2/10, (int)(((float)(ds.t2/10.0) - (int)ds.t2/10)*10),
                (int)ds.t3/10, (int)(((float)(ds.t3/10.0) - (int)ds.t3/10)*10));
      lcd.setCursor(0, 1);
      lcd.print(tt);
    }

  }else if (page == 1){
    byte now[6];
    char tt[16];
    getDate(now);
    sprintf(tt, "%02d/%02d %02d:%02d:%02d  ", now[2], now[1], now[3], now[4], now[5]);
    lcd.print(tt);
    lcd.setCursor(0, 1);
    sprintf(tt, "%d            ", sound_oldval);
    lcd.print(tt);
    
  }else if (page == 2){
    if ((millis() - irriga_last_ping > IRRIGA_PING_OK)||(irriga_last_ping == 0)) {
      lcd.print("Irriga no ping   ");                  
    }else {
      lcd.print("Irriga OK       ");
    }
  }else 
    page = 0;

  if ((lcd_off == 0)&&((millis() - lcd_last_ping) > LCD_OFF_AFTER)) {
    lcd_off = 1;
    lcd.noBacklight();
  }

  btnCheck = buttons.buttonCheck();
  if (btnCheck == buttons.OFF2) {
    if (lcd_off == 0) { //if lcd is OFF just wake it up and don't accept command
      page ++;
    } else {
      lcd_off = 0;
      lcd.backlight();
    }
    lcd_last_ping = millis();
  }
}

