
#define FASTADC 1
// defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif

// holds temp vals
unsigned int val;
unsigned long t;
byte a;

void setup() {
  Serial.begin(115200);
  t = millis();
  val = 0;  
#if FASTADC
  // set prescale to 16
  sbi(ADCSRA,ADPS2) ;
  cbi(ADCSRA,ADPS1) ;
  cbi(ADCSRA,ADPS0) ;
#endif
  pinMode(4, OUTPUT);
}

void loop() { 
#if 0
  a = (analogRead(0) / 4);
  Serial.print(a, BYTE);
#endif
#if 1
  a = (analogRead(0) / 4); //byte resolution
  a = abs(128 - a);
  if (a > 40) {
    Serial.println((int)a);
    digitalWrite(4, 1);
    delay(1000);
    digitalWrite(4, 0);      
  }
#endif
}

