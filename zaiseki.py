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
    try:
      reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
      writer.write(b"GET /client/%s/login HTTP/1.1\r\n" % client)
      writer.write(b"Host: zaiseki.jp\r\n")
      writer.write(b"\r\n")
      await writer.drain()
      if b"HTTP/1.1 404" in await reader.readline():
        raise ZaisekiError("client_id error")
      self.client = client
      while True:
        temp = await reader.readline()
        if temp == b"\r\n":
          break
        elif b"Set-Cookie: " in temp:
          self.session_id = re.search(rb"PHPSESSID=(.+?);", temp).group(0)[:-1]
      while True:
        try:
          temp = await reader.readline()
        except TypeError:
          continue
        m = re.search(rb"token\" value=\"(.+?)\"", temp)
        if m:
          self.token = m.group(0)[14:-1]
          break
      del m, temp
    finally:
      writer.close()
      await writer.wait_closed()
      del reader, writer
    gc.collect()

  async def __login(self, email, password):
    try:
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
      if b"HTTP/1.1 200" in await reader.readline():
        raise ZaisekiError("login error")
      while True:
        temp = await reader.readline()
        if b"Set-Cookie: " in temp:
          self.session_id = re.search(rb"PHPSESSID=(.+?);", temp).group(0)[:-1]
          break
      del d, temp
    finally:
      writer.close()
      await writer.wait_closed()
      del reader, writer
    gc.collect()

    try:
      reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
      writer.write(b"GET /client/%s HTTP/1.1\r\n" % self.client)
      writer.write(b"Host: zaiseki.jp\r\n")
      writer.write(b"Cookie: %s\r\n" % self.session_id)
      writer.write(b"\r\n")
      await writer.drain()
      while True:
        temp = await reader.readline()
        if temp == b"\r\n":
          break
      while True:
        try:
          temp = await reader.readline()
        except TypeError:
          continue
        m = re.search(rb"token\" value=\"(.+?)\"", temp)
        if m:
          self.token = m.group(0)[14:-1]
          break
      del m, temp
    finally:
      writer.close()
      await writer.wait_closed()
      del reader, writer
    gc.collect()

  async def execute(self, status):
    try:
      reader, writer = await asyncio.open_connection("zaiseki.jp", 443, ssl=True)
      d = b"status_id=%s&destination=&back_date=&back_time=&back_flg=0&member=&token=%s" % (status.encode(), self.token)
      writer.write(b"POST /client/%s/zaiseki/update HTTP/1.1\r\n" % self.client)
      writer.write(b"Host: zaiseki.jp\r\n")
      writer.write(b"Cookie: %s\r\n" % self.session_id)
      writer.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
      writer.write(b"Content-Length: %d\r\n" % len(d))
      writer.write(b"\r\n")
      writer.write(d)
      await writer.drain()
      while True:
        temp = await reader.readline()
        if b"Location: " in temp:
          if re.search(rb"Location: (.+?)(\?csrf=err|/login)", temp):
            raise ZaisekiError
          else:
            break
      del d
    finally:
      writer.close()
      await writer.wait_closed()
      del reader, writer
    gc.collect()

class ZaisekiError(Exception):
  pass

async def get_zaiseki(client, email, password):
  zaiseki = Zaiseki()
  await zaiseki.init(client, email, password)
  return zaiseki

async def execute(client, email, password, status):
  z = await get_zaiseki(client, email, password)
  await z.execute(status)