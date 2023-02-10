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
    except:
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
        ("status_0", "text"), #60180
        ("status_1", "text"), #60182
        ("email", "text"), 
        ("password", "password"),
        ]),
      ])
    self.set_config(await s.run(self.get_config()))
    self.connection.disactivate_ap()

  async def zaiseki_mode(self):
    print("zaiseki_mode")
    try:
      config = self.get_config()
      self.connection.connect_wifi(config["wifi_ssid"], config["wifi_password"])
      await asyncio.wait_for(self.connection.wait_connection(), 10)
      await zaiseki.get_zaiseki(config["zaiseki_client"], config["zaiseki_email"], config["zaiseki_password"])
      task = asyncio.create_task(asyncio.sleep(0))
      status = 0
      while True:
        if not self.btnC.value():
          while True:
            if self.btnC.value():
              print("change status")
              status = 1 - status
              break
            await asyncio.sleep(0)
          if not task.done():
            task.cancel()
          task = asyncio.create_task(zaiseki.execute(
            config["zaiseki_client"], 
            config["zaiseki_email"], 
            config["zaiseki_password"], 
            config["zaiseki_status_" + str(status)],
            ))
        await asyncio.sleep(0)
    except zaiseki.ZaisekiError as e:
      print(e)
      pass
    except (asyncio.CancelledError, asyncio.TimeoutError):
      pass
    finally:
      self.connection.disconnect_wifi()

Zaisekikun().run()

# async def _():
#   m = M5StickC()
#   m.connection.connect_wifi('Buffalo-G-F048', 's7vyvmhb8jcrj')
#   await zaiseki.execute(
#     "4yew5dxbp443egaxc9smbu3xnpygvud9x66rw243yq2tm9c3ruqq35u7bu1bq7gp", 
#     "22im0082@i-u.ac.jp",
#     "DLkkiqCijot",
#     "60182",
#     )

# asyncio.run(_())