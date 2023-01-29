import gc
import socket
import sys
import json
MICROPY = sys.implementation.name == "micropython"
del sys

def _():
  sock = socket.socket()
  sock.bind(("0.0.0.0", 8080))
  sock.listen(1)
  while True:
    conn, _ = sock.accept()
    f = conn if MICROPY else conn.makefile("rwb")
    request = f.readline()
    if b"GET / " in request:
      try:
        with open("config.json", mode='r') as config:
          data = json.load(config)
      except:
        data = {}
      f.write(b"HTTP/1.1 200 OK\r\n")
      f.write(b"Content-Type: text/html; charset=UTF-8\r\n")
      f.write(b"\r\n")
      f.write(b"<h1>Setting update</h1>")
      f.write(b"<form action=\"/\" method=\"post\">")
      f.write(b"<h3>Wifi</h3>")
      f.write(b"<label for=\"wifi_ssid\">ssid:</label>")
      f.write(b"<input type=\"text\" name=\"wifi_ssid\" value=\"%s\" required>" % data.get("wifi_ssid", "").encode())
      f.write(b"<br>")
      f.write(b"<label for=\"wifi_password\">password:</label>")
      f.write(b"<input type=\"password\" name=\"wifi_password\" value=\"%s\" required>" % data.get("wifi_password", "").encode())
      f.write(b"<br>")
      f.write(b"<h3>Zaiseki</h3>")
      f.write(b"<label for=\"zaiseki_client\">client:</label>")
      f.write(b"<input type=\"text\" name=\"zaiseki_client\" value=\"%s\" required>" % data.get("zaiseki_client", "").encode())
      f.write(b"<br>")
      f.write(b"<label for=\"zaiseki_email\">email:</label>")
      f.write(b"<input type=\"text\" name=\"zaiseki_email\" value=\"%s\" required>" % data.get("zaiseki_email", "").encode())
      f.write(b"<br>")
      f.write(b"<label for=\"zaiseki_password\">password:</label>")
      f.write(b"<input type=\"password\" name=\"zaiseki_password\" value=\"%s\" required>" % data.get("zaiseki_password", "").encode())
      f.write(b"<br>")
      f.write(b"<br>")
      f.write(b"<input type=\"submit\" value=\"update\">")
      f.write(b"</form>")
    elif b"POST / " in request:
      while True: 
        temp = f.readline()
        if temp == b"\r\n":
          break
        elif b"Content-Length: " in temp:
          d = int(temp[15:])
      try:
        data = dict(i.split("=") for i in f.read(d).decode().split("&")) 
        with open("config.json", mode='w') as config:
          json.dump(data, config)
      except:
        pass
      f.write(b"HTTP/1.1 301 Moved Permanently\r\n")
      f.write(b"Location: /\r\n")
      f.write(b"\r\n")
    else:
      f.write(b"HTTP/1.1 404 NotFound\r\n")
      f.write(b"\r\n")
    f.flush()
_()