import asyncio
from m5stack import *
import network
import _zaiseki

def connect_wifi(*SSID_PASSs):
  sta_if = network.WLAN(network.STA_IF)
  sta_if.active(True)

  SSIDs = [i[0].decode() for i in sta_if.scan()]

  for SSID_PASS in SSID_PASSs:
    if SSID_PASS[0] not in SSIDs:
      continue
    lcd.clear(lcd.BLACK)
    lcd.text(lcd.CENTER, lcd.CENTER, "Connecting\n" + SSID_PASS[0])
    sta_if.connect(*SSID_PASS)
    while not sta_if.isconnected():
      pass
    lcd.clear(lcd.BLACK)
    lcd.text(lcd.CENTER, lcd.CENTER, "Connected")
    break
  else:
    raise

connect_wifi(
  ('iPhone', 'nekoneko'),
  ('aterm-2d3596-g', '36816a76be0c5'),
  ('Buffalo-G-F048', 's7vyvmhb8jcrj'),
  ("aterm-b28299-g", "60898de9a1578"),
)

"4yew5dxbp443egaxc9smbu3xnpygvud9x66rw243yq2tm9c3ruqq35u7bu1bq7gp", "22im0082@i-u.ac.jp", "DLkkiqCijot"
client_id = "4yew5dxbp443egaxc9smbu3xnpygvud9x66rw243yq2tm9c3ruqq35u7bu1bq7gp"
authentication = {
    "email": "22im0082@i-u.ac.jp",
    "pc_login_pass":"DLkkiqCijot",
}

def attendance(isPresence):
  lcd.clear(lcd.BLACK)
  lcd.text(lcd.CENTER, lcd.CENTER, 'change...')
  _zaiseki.execute(client_id, authentication, isPresence)
  lcd.clear(lcd.BLACK)
  lcd.text(lcd.CENTER, lcd.CENTER, 'Attendance' if isPresence else "Absence")


isPresence = True
attendance(isPresence)

while True:
  if btnA.isPressed():
    isPresence = not isPresence
    attendance(isPresence)