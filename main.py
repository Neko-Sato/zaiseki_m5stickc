import uasyncio as asyncio
from m5stickc import M5StickC
from machine import Pin, ADC
import zaiseki
from time import localtime

class _(M5StickC):
  def __init__(self):
    super().__init__()
    # self.wifi_ssid = 'Buffalo-G-F048'
    # self.wifi_password = 's7vyvmhb8jcrj'
    self.wifi_ssid = "ius-iotcl"
    self.wifi_password = "!U1ot_rose"
    self.zaiseki_client_id = "20e2771ftq1k2awbhek2mnn7utwu5ygg9hx9nsutpu92xcu2pq7bqqsd9mqekbzy"
    self.zaiseki_email = "masato-y@i-u.ac.jp"
    self.zaiseki_password = "6Go8bZqrK1n"
    self.status = ["52110", "52111"]
  async def zaiseki_execute(self, status, task=None):
    if task:
      try:
        await task
      except:
        pass
    print(status)
    with open("zaiseki.log", mode='a') as f:
      f.write(str(localtime()) + str(0 if status<0 else 1))
    while True:
      try:
        await zaiseki.execute(
        self.zaiseki_client_id,
        self.zaiseki_email,
        self.zaiseki_password,
        self.status[0 if status<0 else 1],   
        )
        break
      except Exception:
        pass
  async def main(self):
    self.connection.connect_wifi(self.wifi_ssid, self.wifi_password)
    await self.connection.wait_connection()
    pin32 = Pin(32, Pin.IN, Pin.PULL_UP)
    pin33 = Pin(33, Pin.IN, Pin.PULL_UP)
    sensor = ADC(pin33)
    value, prevalue = sensor.read(), None
    state = -1
    task = asyncio.create_task(self.zaiseki_execute(state))
    while True:
      value, prevalue = sensor.read(), value
      diff = prevalue-value
      if 100 < diff*state:
        state = -state
        task.cancel()
        task = asyncio.create_task(self.zaiseki_execute(state, task))
      await asyncio.sleep(2)

_().run()