from machine import I2C, Pin
from ds3231 import DS3231 # Driver by cfpwastaken on Github
from ssd1306 import SSD1306_I2C # Driver forked by stlehmann on Github from Micropython package
import time
import network
import urequests
import re
import json

print("Connecting to WiFi", end="")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Wokwi-GUEST", "")
while not wlan.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

def get_time(timezone="America/New_York"):
  print("Fetching time...", end="")
  URL = "http://worldtimeapi.org/api/timezone/" + timezone
  res = urequests.get(URL)
  datetime_json = res.json()
  regex = re.compile("[-:T.]")
  split_datetime = regex.split(datetime_json["datetime"]) 
  datetime = tuple([int(i) for i in split_datetime[0:6]]) # (year, month, day, hour, minute, second)
  print(" Fetched!")
  return datetime

RTC_I2C = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
rtc = DS3231(RTC_I2C)

SSD_I2C = I2C(1, sda=Pin(2), scl=Pin(3))
oled = SSD1306_I2C(128, 64, SSD_I2C)

rtc.datetime(get_time())
print("Time synced!")

with open("schedule.json") as f:
  schedule = json.load(f)
  print(schedule)
  print(schedule["1_monday"][0])

while True:
  oled.fill(0)
  oled.text(':'.join(str(i) for i in rtc.datetime()[4:7]), 0, 0)
  oled.show()
  time.sleep(1)
