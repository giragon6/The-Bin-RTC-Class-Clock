import time
from machine import I2C, Pin
time.sleep(0.1)

RTC_REG     = const(0x00)
RTC_ADDR    = const(0x68)

SEC_REG     = const(RTC_REG)
MIN_REG     = const(RTC_REG + 1)
HOUR_REG    = const(RTC_REG + 2)
WKDAY_REG   = const(RTC_REG + 3)
DAY_REG     = const(RTC_REG + 4)
MONTH_REG   = const(RTC_REG + 5)
YR_REG      = const(RTC_REG + 6)

def bcd_to_decimal(bcd) -> int:
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def decimal_to_bcd(decimal) -> int:
    return (decimal // 10) << 4 | (decimal % 10)

class DS1307:
    """RTC DS1307 toolbox"""
    def __init__(self, address: int = 0x68, register: int = 0x00, sda: Pin = Pin(0), scl: Pin = Pin(1), frequency: int = 100000) -> None:
        self.address = address
        self.register = register
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=frequency)
    def datetime(self, datetime: list[int] = None): #TODO: Fix arg staying as parameter default
        if datetime is not None:
            try:
                if (len(datetime) != 7): raise ValueError 
                self.i2c.writeto_mem(self.address, RTC_REG, bytearray([decimal_to_bcd(v) for v in datetime]))
            except ValueError:
                print("Error: Datetime must be in format [seconds, minutes, hours, weekday, day, month, year]")
            return self.i2c.readfrom_mem(self.address, RTC_REG, 1)[0] #TODO: Format correctly

    def seconds(self, seconds: int = None) -> int:
        if seconds is not None:
            self.i2c.writeto_mem(self.address, SEC_REG, bytearray([decimal_to_bcd(seconds)]))
        return bcd_to_decimal(self.i2c.readfrom_mem(self.address, SEC_REG, 1)[0])

rtc = DS1307()

rtc.datetime(datetime=[1,2,3,4,5,6,7])
print(rtc.datetime())
