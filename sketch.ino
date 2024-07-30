#include "TM1637.h"
#include "RTClib.h"

RTC_DS3231 rtc;

const int CLK = 2;
const int DIO = 3;

TM1637 tm(CLK, DIO);

void setup() {
  // put your setup code here, to run once:
  Serial1.begin(115200);
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1) delay(10);
  }

  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  tm.init();
  tm.set(BRIGHT_TYPICAL);
}
void loop() {
  delay(1);
}