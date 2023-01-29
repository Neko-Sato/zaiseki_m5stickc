import gc
import re
import uasyncio as asyncio

class Zaiseki:
  def __init__(self):
    self.client = None
    self.session_id = None
    self.token = None

  async def init(self, client, email, password):
    await self.__set_client(client)
    gc.collect()
    await self.__login(email, password)
    gc.collect()

  async def __set_client(self, client):
    client = client.encode()
    reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
    writer.write(b"GET /client/%s/login HTTP/1.1\r\n" % client)
    writer.write(b"Host: zaiseki.jp\r\n")
    writer.write(b"\r\n")
    await writer.drain()
    r = await reader.read(-1)
    if b"HTTP/1.1 404" in r:
      raise Exception
    self.client = client
    self.session_id = re.search(rb"PHPSESSID=(.+?);", r).group(0)[:-1]
    self.token = re.search(rb"token\" value=\"(.+?)\"", r).group(0)[14:-1]
    del reader, writer, r
    gc.collect()

  async def __login(self, email, password):
    reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
    d = b"email=%s&pc_login_pass=%s&token=%s" % (email.encode(), password.encode(), self.token)
    writer.write(b"POST /client/%s/login HTTP/1.1\r\n" % self.client)
    writer.write(b"Host: zaiseki.jp\r\n")
    writer.write(b"Cookie: %s\r\n" % self.session_id)
    writer.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
    writer.write(b"Content-Length: %d\r\n" % len(d))
    writer.write(b"\r\n")
    writer.write(d)
    await writer.drain()
    r = await reader.read(-1)
    if b"HTTP/1.1 200" in r:
      raise
    self.session_id = re.search(rb"PHPSESSID=(.+?);", r).group(0)[:-1]
    del reader, writer, r, d
    gc.collect()

    reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
    writer.write(b"GET /client/%s HTTP/1.1\r\n" % self.client)
    writer.write(b"Host: zaiseki.jp\r\n")
    writer.write(b"Cookie: %s\r\n" % self.session_id)
    writer.write(b"\r\n")
    await writer.drain()
    r = await reader.read(-1)
    self.token = re.search(rb"token\" value=\"(.+?)\"", r).group(0)[14:-1]
    del reader, writer, r
    gc.collect()

  async def execute(self, status):
    reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
    d = b"status_id=%d&destination=&back_date=&back_time=&back_flg=0&member=&token=%s" % (status, self.token)
    writer.write(b"POST /client/%s/zaiseki/update HTTP/1.1\r\n" % self.client)
    writer.write(b"Host: zaiseki.jp\r\n")
    writer.write(b"Cookie: %s\r\n" % self.session_id)
    writer.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
    writer.write(b"Content-Length: %d\r\n" % len(d))
    writer.write(b"\r\n")
    writer.write(d)
    await writer.drain()
    r = await reader.read(-1)
    del reader, writer, d
    if re.search(rb"Location: (.+?)(\?csrf=err|/login)", r):
      raise
    gc.collect()

async def get_zaiseki(client, email, password):
  zaiseki = Zaiseki()
  await zaiseki.init(client, email, password)
  return zaiseki

async def execute(client, email, password, status):
  z = await get_zaiseki(client, email, password)
  await z.execute(status)