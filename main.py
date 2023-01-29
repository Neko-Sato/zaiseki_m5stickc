import gc
import uasyncio as asyncio
import json
from m5stickc import M5StickC
import zaiseki
import setup_server

class Zaisekikun(M5StickC):
  config_path = "config.json"

  def set_config(self, config):
    with open(self.config_path, mode="w") as f:
      json.dump(config, f)

  def get_config(self):
    try:
      with open(self.config_path, mode="r") as f:
        config = json.load(f)
    except Exception as e:
      config = {}
    return config

  async def main(self):
    print("start")
    is_setup, task = False, asyncio.create_task(self.zaiseki_mode())
    while True:
      if not self.btnA.value():
        while True:
          if self.btnA.value():
            break
          await asyncio.sleep(0)
        print("push button")
        task.cancel()
        await task
      if task.done():
        if is_setup:
          is_setup, task = False, asyncio.create_task(self.zaiseki_mode())
        else:
          is_setup, task = True, asyncio.create_task(self.setup_mode())
      await asyncio.sleep(0)

  async def setup_mode(self):
    print("setup_mode")
    self.connection.activate_ap()
    s = setup_server.SetupServer([
      ("wifi", [
        ("ssid", "text"), 
        ("password", "password"),
        ]),
      ("zaiseki", [
        ("client", "text"), 
        ("email", "text"), 
        ("password", "password"),
        ]),
      ])
    self.set_config(await s.run(self.get_config()))
    self.connection.disactivate_ap()

  async def zaiseki_mode(self):
    print("zaiseki_mode")
    config = self.get_config()
    try:
      self.connection.connect_wifi(config["wifi_ssid"], config["wifi_password"])
      await asyncio.wait_for(self.connection.wait_connection(), 3)
      await zaiseki.get_zaiseki(config["zaiseki_client"], config["zaiseki_email"], config["zaiseki_password"])
      status = 0
      while True:
        if not self.btnC.value():
          while True:
            if self.btnC.value():
              break
            await asyncio.sleep(0)
          await zaiseki.execute(
            config["zaiseki_client"], 
            config["zaiseki_email"], 
            config["zaiseki_password"], 
            zaiseki.Zaiseki.status[status],
            )
          if status == 0:
            status = 1
          else:
            status = 0
        await asyncio.sleep(0)
    except:
      pass
    self.connection.disconnect_wifi()

class _(M5StickC):
  async def main(self):
    self.connection.connect_wifi("will-wifi305", "01234567")
    await self.connection.wait_connection()
    z = await zaiseki.get_zaiseki("4yew5dxbp443egaxc9smbu3xnpygvud9x66rw243yq2tm9c3ruqq35u7bu1bq7gp", "22im0082@i-u.ac.jp", "DLkkiqCijot")
    await z.execute(zaiseki.Zaiseki.status[0])

_().run()