import network
import socket
import ujson as json

def init_ap():
  ap = network.WLAN(network.AP_IF)
  ap.config(essid="esp32", authmode=3, password="01234567")
  ap.ifconfig(('192.168.0.1', '255.255.255.0', '192.168.0.1', '192.168.0.1'))
  ap.active(True)

def init_sta():
  sta = network.WLAN(network.STA_IF)
  sta.active(True)
  with open("config.json", mode="r") as f:
    wifi = json.load(f)["wifi"]
    scan = [i[0].decode() for i in sta.scan()]
    for ssid in wifi:
      if wifi["SSID"] not in scan:
        continue
      sta.connect(wifi["SSID"], wifi["password"])
      while not sta_if.isconnected():
        pass
      break
    else:
      raise

