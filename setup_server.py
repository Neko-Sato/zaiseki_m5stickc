import gc
import binascii
import uasyncio as asyncio

class SetupServer:
  def __init__(self, forms):
    self.config = {}
    self.forms = forms #[("title":[("name", "type"),]),]

  async def run(self, init_config={}):
    self.config = init_config
    server = await asyncio.start_server(
      self.__callback, 
      "0.0.0.0", 
      80, 
      backlog=1
      )
    while not hasattr(server, "task"):
      await asyncio.sleep(0)
    await server.wait_closed()
    return self.config

  async def __callback(self, reader, writer):
    request = await reader.readline()
    if b"GET / " in request:
      await self.__get(reader, writer)
    elif b"POST / " in request:
      await self.__set(reader, writer)
    else:
      writer.write(b"HTTP/1.1 404 NotFound\r\n")
      writer.write(b"\r\n")
    await writer.drain()
    # writer.close()
    # await writer.wait_closed()
    del reader, writer
    gc.collect()

  async def __get(self, reader, writer):
    d = ""
    d += "<h1>Setting update</h1>"
    d += "<form action=\"/\" method=\"post\">"
    for title, sub_forms in self.forms:
      t1 = ""
      t1 += "<h3>" + title + "</h3>"
      for name, type in sub_forms:
        t2 = ""
        t2 += "<label for=\"" + title + "_" + name + "\">" + name + ":</label>"
        t2 += "<input type=\"" + type + "\" name=\"" + title + "_" + name + "\" value=\"" + self.config.get(title + "_" + name, "") + "\" required>"
        t2 += "<br>"
        t1 += t2
        del t2
        gc.collect()
      d += t1
      del t1
      gc.collect()
    d += "<input type=\"submit\" value=\"send\">"
    d += "</form>"
    d = d.encode()
    writer.write(b"HTTP/1.1 200 OK\r\n")
    writer.write(b"Content-Length: %d\r\n" % len(d))
    writer.write(b"Content-Type: text/html; charset=UTF-8\r\n")
    writer.write(b"\r\n")
    writer.write(d)
    del d
    gc.collect()

  async def __set(self, reader, writer):
    while True: 
      temp = await reader.readline()
      if temp == b"\r\n":
        break
      elif b"Content-Length: " in temp:
        d = int(temp[15:])
      del temp
      gc.collect()
    temp = unquote(await reader.read(d)).decode()
    self.config = dict(i.split("=") for i in temp.split("&")) 
    writer.write(b"HTTP/1.1 301 Moved Permanently\r\n")
    writer.write(b"Location: /\r\n")
    writer.write(b"\r\n")

def unquote(string):
  temp = b""
  for l in string.split(b"%"):
    try:
      temp += binascii.unhexlify(l[:2]) + l[2:]
    except ValueError:
      temp += l
  return temp