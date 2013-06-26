#include <RF12.h>
#include <Ports.h>

byte pin_adc = 3; //port 4
byte pin_led = 5;

int change = 0;
int sound_oldval = 0;
int check_change = 0;

#define SMOOTH 5
#define CHECK_CHANGE 5
#define THRE 30

struct data {  
  byte value;
};
struct data ds;

// utility code to perform simple smoothing as a running average
static int smoothedAverage(int prev, int next, byte firstTime =0) {
    if (firstTime)
        return next;
    return ((SMOOTH - 1) * prev + next + SMOOTH / 2) / SMOOTH;
}

void setup(){
  Serial.begin(57600);
  Serial.print("\n[sound]\n");
  rf12_initialize(45, RF12_868MHZ);  
}

static void doReport(byte v) {
  while (!rf12_canSend())
      rf12_recvDone();
  ds.value = v;
  rf12_sendStart(0, &ds, sizeof ds);
  rf12_sendWait(0);
}

void loop(){
  int val = analogRead(pin_adc);  
  sound_oldval = smoothedAverage(sound_oldval, val, check_change == 0);    
  Serial.print(val); Serial.print(" "); Serial.println(sound_oldval);
  if ((val == sound_oldval)&&(val != change)&&(check_change == 1)) {
    change = sound_oldval;
    Serial.print("new change "); Serial.println(change);    
  }
  if (check_change == 0)
    check_change = CHECK_CHANGE;
  if ((val > change + THRE)&&(change > 0)) {
    Serial.print("alarm "); Serial.println(val);
  }
  check_change --;
  delay(500);
} 


