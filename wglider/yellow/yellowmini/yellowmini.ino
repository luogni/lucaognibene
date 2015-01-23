const int mpowPin = 3;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   const int mpowPin = 3;
const int mrevPin = 4;
const int battPin = A0;
const int ledPin = 13;

typedef enum ReportMode{MOTOR1FW, MOTOR1REV, NOPOWER, STANDBY};
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
  if (mode == MOTOR1FW) {
    singleReportLed(100);
    singleReportLed(100);
  }else if (mode == MOTOR1REV) {
    singleReportLed(100);
    singleReportLed(100);
    singleReportLed(100);
  }else if (mode == NOPOWER) {
    singleReportLed(1000);
  }else if (mode == STANDBY) {
    singleReportLed(500);  
  }
}

void setMotor(char rev, unsigned char mspeed, long wait) {
  int st = 1000;
  if (mspeed == 0) {
    reportLed(STANDBY);
  } else if (rev == 0) {
    reportLed(MOTOR1FW);    
  } else if (rev == 1) {
    reportLed(MOTOR1REV);
  }
  digitalWrite(mrevPin, rev);
  analogWrite(mpowPin, mspeed);
  if (wait > 0) {
    while (wait > 0) {
      delay(st);
      wait -= st;
    }
  }
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
#if 1  
  setMotor(1, 200, 40000);
  setMotor(0, 0, 10000);
  doBattery();
  setMotor(0, 200, 40000);
  setMotor(0, 0, 10000);
#else
  setMotor(1, 255, 5000);
  setMotor(0, 0, 1000);
  doBattery();
  setMotor(0, 255, 5000);
  setMotor(0, 0, 1000);
#endif
}

