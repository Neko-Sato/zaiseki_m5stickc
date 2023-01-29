import uasyncio as asyncio
from machine import Pin
import network

class Connection:
  sta = network.WLAN(network.STA_IF)
  ap = network.WLAN(network.AP_IF)

  ###
  def connect_wifi(self, ssid, password):
    self.sta.active(True)
    self.sta.connect(ssid, password)

  async def wait_connection(self):
    while not self.sta.isconnected():
      await asyncio.sleep(0)
  
  def disconnect_wifi(self):
    self.sta.active(False)
  
  ###
  def activate_ap(self, ssid="esp32", password="01234567"):
    self.ap.active(True)
    self.ap.config(essid=ssid, authmode=3, password=password)
    self.ap.ifconfig(('192.168.0.1', '255.255.255.0', '192.168.0.1', '192.168.0.1'))
  
  def disactivate_ap(self):
    self.ap.active(False)

class M5StickC:
  btnA = Pin(39, mode=Pin.IN, pull=Pin.PULL_UP)
  btnB = Pin(38, mode=Pin.IN, pull=Pin.PULL_UP)
  btnC = Pin(37, mode=Pin.IN, pull=Pin.PULL_UP)
  connection = Connection()

  def __init__(self):
    self.loop = asyncio.new_event_loop()
  
  def run(self):
    self.loop.create_task(self.main())
    self.loop.run_forever()
  
  async def main(self):
    while True:
      asyncio.sleep(0)