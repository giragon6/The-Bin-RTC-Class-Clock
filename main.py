import time
from machine import I2C, Pin
time.sleep(0.1)

def bcd_to_decimal(bcd):
  return (bcd >> 4) * 10 + (bcd & 0x0F)

register = 0x00
address = 0x68

rtc_i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

rtc_i2c.writeto_mem(address, register, b"\x00\x23\x12\x28\x14\x07\x21")

print(bcd_to_decimal(rtc_i2c.readfrom_mem(address, register, 1)[0]))