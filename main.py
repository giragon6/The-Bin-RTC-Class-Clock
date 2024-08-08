from machine import I2C, Pin
from micropython import const
from ds3231 import DS3231 # Driver by cfpwastaken on Github
from ssd1306 import SSD1306_I2C # Driver forked by stlehmann on Github from Micropython package
from time import sleep
import network
import urequests
import re
import json

with open("schedule.json") as f:
  schedule = json.load(f)
sleep(0.1)

# print("Connecting to WiFi", end="")
# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# wlan.connect("Wokwi-GUEST", "")
# while not wlan.isconnected():
#   print(".", end="")
#   sleep(0.1)
# print(" Connected!")

time_split_re = re.compile("[-:T.]") # To be used to split time strings as given by worldtimeapi

MIDNIGHT_SECS: int = const(86400)

fetch_json_from_URL: str = lambda URL : urequests.get(URL).json()

def get_time(timezone: str = "America/New_York") -> tuple[int]:
  print("Fetching time...", end="")
  datetime_json = fetch_json_from_URL("http://worldtimeapi.org/api/timezone/" + timezone)
  split_datetime = time_split_re.split(datetime_json["datetime"]) # (year, month, day, hour, minute, second)
  day_of_week = datetime_json["day_of_week"]
  datetime = [int(i) for i in split_datetime[0:6]] 
  datetime.append(day_of_week)
  print(" Fetched!")
  return tuple(datetime)

def format_time(hours: int, minutes: int, seconds: int) -> str:
  return "{h}:{m:02}:{s:02}".format(h=hours, m=minutes, s=seconds)

def to_seconds(time: str | tuple[int]) -> int:
  if type(time) == str:
    split_time: list[str] = time_split_re.split(time)
    hours: int = int(split_time[0])
    minutes: int = int(split_time[1])
    seconds: int = int(split_time[2])
  elif type(time) == tuple:
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

def get_time_between(now_secs: int, then_secs: int) -> int:
  if then_secs > now_secs: 
    return then_secs - now_secs
  if now_secs > then_secs:
    return MIDNIGHT_SECS - (now_secs - then_secs)
  return 0

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
rtc.datetime((2024, 8, 7, 7, 30, 30, 1))
print("Time synced!")

def get_next_block():
  # day = rtc.datetime()[6]
  day = 1
  now_secs = to_seconds(rtc.datetime()[4:7])
  blocks_secs = [get_time_between(now_secs, to_seconds(schedule[str(day)]["blocks"][block]["start_time"])) for block in schedule[str(day)]["blocks"]]
  nearest_block = list(schedule[str(day)]["blocks"])[blocks_secs.index(min(blocks_secs))] # Finds index of block with least seconds until and accesses that index in blocks keys to get block name
  return nearest_block

next_block = get_next_block()

while True:
  oled.fill(0)
  now_time = format_time(*rtc.datetime()[4:7])
  now_secs = to_seconds(now_time)
  next_block_secs = to_seconds(schedule["1"]["blocks"][next_block]["start_time"])
  oled.text(now_time, 0, 0) # Get hours, minutes, and seconds and format them for screen
  oled.text(str(to_time_string(get_time_between(now_secs, next_block_secs))), 0, 10)
  oled.show()
  sleep(1)
