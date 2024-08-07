from machine import I2C, Pin
from ds3231 import DS3231 # Driver by cfpwastaken on Github
from ssd1306 import SSD1306_I2C # Driver forked by stlehmann on Github from Micropython package
import time
import network
import urequests
import re
import json

with open("schedule.json") as f:
  schedule = json.load(f)
time.sleep(0.1)

# print("Connecting to WiFi", end="")
# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# wlan.connect("Wokwi-GUEST", "")
# while not wlan.isconnected():
#   print(".", end="")
#   time.sleep(0.1)
# print(" Connected!")

time_split_re = re.compile("[-:T.]") # To be used to split time strings as given by worldtimeapi

def get_time(timezone: str = "America/New_York") -> tuple[int]:
  print("Fetching time...", end="")
  URL = "http://worldtimeapi.org/api/timezone/" + timezone
  res = urequests.get(URL)
  datetime_json = res.json()
  split_datetime = time_split_re.split(datetime_json["datetime"]) # (year, month, day, hour, minute, second)
  datetime = tuple([int(i) for i in split_datetime[0:6]]) # Formats for datetime function
  print(" Fetched!")
  return datetime

def to_minutes(time: str | tuple[int]) -> int:
  if type(time) == str:
    split_time: list[str] = time_split_re.split(time)
    hours: int = int(split_time[0])
    minutes: int = int(split_time[1])
  elif type(time) == tuple[int]:
    hours: int = time[0]
    minutes: int = time[1]
  total_minutes: int = hours*60 + minutes
  return total_minutes

def to_time_string(minutes: int) -> str:
  hours: int = int(minutes / 60)
  minutes: int =  minutes % 60
  return (str(hours) + ":" + str(minutes))

def get_time_between(now: str, then: str) -> str:
  return to_time_string(to_minutes(then) - to_minutes(now))

# DEBUG FUNCTION -- REMOVE THIS LATER
# connectivity issues causing fetch from worldtimeapi.org to take unreasonably long

# def enter_manual_time() -> tuple[int]:
#   time = input("Enter time: ")
#   regex = re.compile("[-:T.]")
#   split_datetime = regex.split(time) 
#   datetime = tuple([int(i) for i in split_datetime[0:6]]) # (year, month, day, hour, minute, second)
#   print(datetime)
#   return datetime

RTC_I2C = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
rtc = DS3231(RTC_I2C)

SSD_I2C = I2C(1, sda=Pin(2), scl=Pin(3))
oled = SSD1306_I2C(128, 64, SSD_I2C)

# rtc.datetime(get_time())
# rtc.datetime(enter_manual_time())
rtc.datetime((2024, 8, 7, 13, 32, 40))
print("Time synced!")

while True:
  oled.fill(0)
  oled.text(":".join(str(i) for i in rtc.datetime()[4:7]), 0, 0) # Get hours, minutes, and seconds and format them for screen
  oled.text("when the", 0, 10)
  oled.show()
  time.sleep(1)
