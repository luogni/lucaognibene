const int mpowPin = 3;
const int mrevPin = 2;
const int battPin = A0;
const int ledPin = 13;
char mode = -1;
typedef enum ReportMode{MOTOR, NOPOWER, STANDBY};
#define DEBUG
//#define BATTERYMIN (0)     // nimh
#define BATTERYMIN (7200)  // lipo 2s

void setup() {
  pinMode(mpowPin, OUTPUT);
  pinMode(mrevPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(battPin, INPUT);
#ifdef DEBUG
  Serial.begin(57600);
  Serial.println("\n[yellow]");
#endif
}

void singleReportLed(int wait) {
  digitalWrite(ledPin, HIGH); 
  delay(wait);
  digitalWrite(ledPin, LOW);
}

void reportLed(int mode) {
#ifdef DEBUG
  Serial.print(millis()); Serial.print(" Mode "); Serial.println(mode);
#endif
  if (mode == MOTOR) {
    singleReportLed(100);
    singleReportLed(100);
  }else if (mode == NOPOWER) {
    singleReportLed(1000);
  }else if (mode == STANDBY) {
    singleReportLed(500);  
  }  
}

void setMotor(char rev, unsigned char mspeed, int wait) {
  if (mspeed == 0) reportLed(STANDBY);
  else reportLed(MOTOR);
  digitalWrite(mrevPin, rev);
  analogWrite(mpowPin, mspeed);
  if (wait > 0) delay(wait);
}

int getBattery() {
  int bv;
  int data = analogRead(battPin);
  // 27 and 68 are voltage divider resistors, 11.33 is (3.3 / 1024) * ((27 + 68.0) / 27.0) * 1000    
  bv = data * 11.33;
#ifdef DEBUG
    Serial.print("battery "); Serial.print(data); Serial.print(" "); Serial.println(bv);
#endif
  return bv;
}

void doBattery() {
  int bv;
  bv = getBattery();
  if (bv < BATTERYMIN) {
    reportLed(NOPOWER);
    while (true) {delay(6000);};
  }  
}

void loop() {
  setMotor(0, 200, 10000);
  setMotor(0, 0, 1000);
  doBattery();
  setMotor(1, 200, 10000);
  setMotor(0, 0, 1000);
}  

