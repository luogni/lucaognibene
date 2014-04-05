int sensorPin = 4;
int startBit   = 2000;   // This pulse sets the threshold for a transmission start bit
int senderPin  = 7;      // Infrared LED on Pin 3
int waitTime = 300;     // The amount of time to wait between pulses
int endBit     = 3000;  // This pulse sets the threshold for an end bit
int one        = 1000;   // This pulse sets the threshold for a transmission that 
                         // represents a 1
int zero       = 400;    // This pulse sets the threshold for a transmission that 
                         // represents a 0
int ret[2];              // Used to hold results from IR sensing.
int endcheck;
int startcheck;
unsigned long time;


void setup() {
  Serial.begin(9600);
  pinMode(sensorPin, INPUT);
  pinMode(senderPin, OUTPUT);
  time = 0;
  Serial.println("start!");
}

int convert(int bits[]) {
  int result = 0;
  int seed   = 1;
  for(int i=3;i>=0;i--) {
    if(bits[i] == 1) {
      result += seed;
    }
    seed = seed * 2;
  }
  return result;
}

void senseIR() {
  int who[4];
  int what[4];
  startcheck = pulseIn(sensorPin, LOW);
  if (startcheck < startBit) {
    ret[0] = -1;
    return;
  }  
  what[0]  = pulseIn(sensorPin, LOW);
  what[1]  = pulseIn(sensorPin, LOW);
  what[2]  = pulseIn(sensorPin, LOW);
  what[3]  = pulseIn(sensorPin, LOW);
  who[0]   = pulseIn(sensorPin, LOW);
  who[1]   = pulseIn(sensorPin, LOW);
  who[2]   = pulseIn(sensorPin, LOW);
  who[3]   = pulseIn(sensorPin, LOW);
  endcheck = pulseIn(sensorPin, LOW);
  Serial.println("got start");
  Serial.println(startcheck);
  if (endcheck <= endBit) {
    Serial.println("bad signal");
    ret[0] = -1;
    return;
  }
  Serial.println("---who---");
  for(int i=0;i<=3;i++) {
    Serial.println(who[i]);
    if(who[i] > one) {
      who[i] = 1;
    } else if (who[i] > zero) {
      who[i] = 0;
    } else {
      // Since the data is neither zero or one, we have an error
      Serial.println("unknown player");
      ret[0] = -1;
      return;
    }
  
}
  ret[0]=convert(who);
  Serial.println(ret[0]);

  Serial.println("---what---");
  for(int i=0;i<=3;i++) {
    Serial.println(what[i]);
    if(what[i] > one) {
      what[i] = 1;
    } else if (what[i] > zero) {
      what[i] = 0;
    } else {
      // Since the data is neither zero or one, we have an error
      Serial.println("unknown action");
      ret[0] = -1;
      return;
    }
  }
  ret[1]=convert(what);
  Serial.println(ret[1]);
  Serial.println(endcheck
  );
  return;
}

void fireShot(int player, int level) {
  Serial.println("fire!");
  int encoded[8];
  for (int i=0; i<4; i++) {
    encoded[i] = player>>i & B1;   //encode data as '1' or '0'
  }
  for (int i=4; i<8; i++) {
    encoded[i] = level>>i & B1;
  }
  // send startbit
  oscillationWrite(senderPin, startBit);
  // send separation bit
  digitalWrite(senderPin, HIGH);
  delayMicroseconds(waitTime);
  // send the whole string of data
  for (int i=7; i>=0; i--) {
    if (encoded[i] == 0) {
      oscillationWrite(senderPin, zero);
    } else {
      oscillationWrite(senderPin, one);
    }
    // send separation bit
    digitalWrite(senderPin, HIGH);
    delayMicroseconds(waitTime);
  }
  oscillationWrite(senderPin, endBit);
}

void oscillationWrite(int pin, int time) {
  for(int i = 0; i <= time/26; i++) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(13);
    digitalWrite(pin, LOW);
    delayMicroseconds(13);
  }
}

void loop() {
  senseIR();
  //if (millis() - time > 1000) {
  //   time = millis();
  //   fireShot(1, 10); 
  //}
}

