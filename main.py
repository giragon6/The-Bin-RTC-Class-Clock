import time
from machine import I2C, Pin
time.sleep(0.1)

RTC_REG    = const(0x00)
RTC_ADDR   = const(0x68)

SEC_REG    = const(RTC_REG)
MIN_REG    = const(RTC_REG + 1)
HOUR_REG   = const(RTC_REG + 2)
WKDAY_REG  = const(RTC_REG + 3)
DAY_REG    = const(RTC_REG + 4)
MONTH_REG  = const(RTC_REG + 5)
YR_REG     = const(RTC_REG + 6)

def bcd_to_decimal(bcd) -> int:
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def decimal_to_bcd(decimal) -> int:
    return (decimal // 10) << 4 | (decimal % 10)

#TODO: 4 is being written/read as x01 in the memory -- issue with the writing/reading itself, not conversion/arg

class DS1307:
    """RTC DS1307 toolbox"""
    def __init__(self, address: int = 0x68, register: int = 0x00, sda: Pin = Pin(0), scl: Pin = Pin(1), frequency: int = 100000) -> None:
        self.address = address
        self.register = register
        self.i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=frequency)

    def get_datetime(self) -> tuple[int]:
        print(self.i2c.readfrom_mem(self.address, RTC_REG, 10))
        return [self.i2c.readfrom_mem(self.address, RTC_REG + i, 1)[0] for i in range(7)] #TODO: Format correctly

    def set_datetime(self, datetime: tuple[int]) -> None:
        try:
            if (len(datetime) != 7): raise ValueError 
            self.i2c.writeto_mem(self.address, RTC_REG, bytes([decimal_to_bcd(v) for v in datetime]))
        except ValueError:
            print("Error: Datetime must be in format (seconds, minutes, hours, weekday, day, month, year)")

    def seconds(self, seconds: int = None) -> int:
        if seconds is not None:
            self.i2c.writeto_mem(self.address, SEC_REG, bytearray([decimal_to_bcd(seconds)]))
        return bcd_to_decimal(self.i2c.readfrom_mem(self.address, SEC_REG, 1)[0])

rtc = DS1307()

rtc.set_datetime((1,2,3,4,5,6,7))
print(rtc.get_datetime())
