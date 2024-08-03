from machine import I2C, Pin
from ds3231 import DS3231 # Driver by cfpwastaken on Github
from ssd1306 import SSD1306_I2C # Driver forked by stlehmann on Github from Micropython package
import time

RTC_I2C = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
rtc = DS3231(RTC_I2C)

SSD_I2C = I2C(1, sda=Pin(2), scl=Pin(3))
oled = SSD1306_I2C(128, 64, SSD_I2C)

rtc.datetime((24, 8, 3, 2, 42, 50))
print(rtc.datetime())

while True:
  oled.fill(0)
  oled.text(':'.join(str(i) for i in rtc.datetime()[4:7]), 0, 0)
  oled.show()
  time.sleep(1)
