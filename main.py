from machine import I2C, Pin
from micropython import const
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

fetch_json_from_URL: str = lambda URL : urequests.get(URL).json()

def get_time(timezone: str = "America/New_York") -> tuple[int]:
  print("Fetching time...", end="")
  datetime_json = fetch_json_from_URL("http://worldtimeapi.org/api/timezone/" + timezone)
  split_datetime = time_split_re.split(datetime_json["datetime"]) # (year, month, day, hour, minute, second)
  datetime = tuple([int(i) for i in split_datetime[0:6]]) # Formats for datetime function
  print(" Fetched!")
  return datetime

def get_day_of_week(timezone: str = "America/New_York") -> tuple[int]:
  print("Fetching day of week...", end="")
  datetime_json = fetch_json_from_URL("http://worldtimeapi.org/api/timezone/" + timezone)
  print(" Fetched!")
  return datetime_json["day_of_week"]

def format_time(hours: int, minutes: int, seconds: int) -> str:
  return "{h}:{m:02}:{s:02}".format(h=hours, m=minutes, s=seconds)

def to_seconds(time: str | tuple[int]) -> int:
  if type(time) == str:
    split_time: list[str] = time_split_re.split(time)
    hours: int = int(split_time[0])
    minutes: int = int(split_time[1])
    seconds: int = int(split_time[2])
  elif type(time) == tuple[int]:
    hours: int = time[0]
    minutes: int = time[1]
    seconds: int = time[2]
  total_seconds: int = hours*3600 + minutes*60 + seconds
  return total_seconds

def to_time_string(seconds: int) -> str:
  hours: int = int(seconds / 3600)
  minutes: int =  int((seconds - hours * 3600) / 60)
  seconds: int = seconds % 60
  return format_time(hours, minutes, seconds)

def get_time_between(now: str, then: str) -> str:
  now_secs = to_seconds(now)
  then_secs = to_seconds(then)
  if then_secs > now_secs: 
    return to_time_string(then_secs - now_secs)
  if now_secs > then_secs:
    _MIDNIGHT_SECS: int = const(86400)
    return to_time_string(_MIDNIGHT_SECS - (now_secs - then_secs))
  return to_time_string(0)

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
rtc.datetime((2024, 8, 7, 8, 30, 30))
print("Time synced!")

while True:
  oled.fill(0)
  now_time = format_time(*rtc.datetime()[4:7])
  oled.text(now_time, 0, 0) # Get hours, minutes, and seconds and format them for screen
  oled.text(get_time_between(now_time, schedule["1"]["blocks"][0]["start_time"]), 0, 10)
  oled.show()
  time.sleep(1)
