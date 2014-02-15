#include "LPD8806.h"
#include "SPI.h"

int dataPin = 4;  // port 1
int clockPin = 5; // port 2

// Set the first variable to the NUMBER of pixels. 32 = 32 pixels in a row
// The LED strips are 32 LEDs per meter but you can extend/cut the strip
LPD8806 strip = LPD8806(52, dataPin, clockPin);



void setup() {
  // Start up the LED strip
  strip.begin();

  // Update the strip, to start they are all 'off'
  strip.show();
}

// function prototypes, do not remove these!
void colorChase(uint32_t c, uint8_t wait);
void colorWipe(uint32_t c, uint8_t wait);
void dither(uint32_t c, uint8_t wait);
void scanner(uint8_t r, uint8_t g, uint8_t b, uint8_t wait);
void wave(uint32_t c, int cycles, uint8_t wait);
void rainbowCycle(uint8_t wait);
uint32_t Wheel(uint16_t WheelPos);

void loop() {

  // Send a simple pixel chase in...
  //colorChase(strip.Color(127,127,127), 20); // white
  //colorChase(strip.Color(127,0,0), 20);     // red
  //colorChase(strip.Color(127,127,0), 20);   // yellow
  //colorChase(strip.Color(0,127,0), 20);     // green
  //colorChase(strip.Color(0,127,127), 20);   // cyan
  //colorChase(strip.Color(0,0,127), 20);     // blue
  //colorChase(strip.Color(0,0,127), 500);   // magenta

  for (int i=0; i < 255; i++) {
    strip.setPixelColor(30, strip.Color(i, 0, 0));
    strip.setPixelColor(31, strip.Color(i, i, i));
    strip.show();
    delay(20);
  }

  // Clear strip data before start of next effect
  for (int i=0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, 0);
  }
}

// Chase a dot down the strip
// good for testing purposes
void colorChase(uint32_t c, uint8_t wait) {
  int i;

  for (i=0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, 0);  // turn all pixels off
  }

  for (i=0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, c); // set one pixel
      strip.show();              // refresh strip display
      delay(wait);               // hold image for a moment
      strip.setPixelColor(i, 0); // erase pixel (but don't refresh yet)
  }
  strip.show(); // for last erased pixel
}

