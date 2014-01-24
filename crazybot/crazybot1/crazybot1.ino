#include <JeeLib.h>

Port one (1);
Port two (2);

void setup() {
  one.mode(OUTPUT);
  two.mode(OUTPUT);
}

void loop() {
  one.digiWrite(1);
  two.digiWrite(0);
  int i;
  for(i=0;i<255;i++) {
    two.anaWrite(i);
    delay(40);
  }
}
