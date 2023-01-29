import gc
import socket
import ssl
import re
import sys
MICROPY = sys.implementation.name == "micropython"
del sys

def get_conn():
  sock = socket.socket()
  sock.connect(("zaiseki.jp", 443))
  try:
    sock = ssl.create_default_context().wrap_socket(sock, server_hostname="zaiseki.jp")
  except:
    sock = ssl.wrap_socket(sock, server_hostname="zaiseki.jp")
  return sock

def execute(client_id, authentication, isPresence):
  #######
  conn = get_conn()
  f = conn if MICROPY else conn.makefile("rwb")
  f.write(b"GET /client/%s/login HTTP/1.1\r\n" % client_id.encode())
  f.write(b"Host: zaiseki.jp\r\n")
  f.write(b"\r\n")
  if not MICROPY:
    f.flush()
  r = f.read()
  print(r.decode())
  session_id = re.search(rb"PHPSESSID=[^;]+;", r).group(0)[:-1]
  token = re.search(rb"token\" value=\"[^\"]*\"", r).group(0)[14:-1]
  del conn, f, r
  gc.collect()

  #######
  conn = get_conn()
  f = conn if MICROPY else conn.makefile("rwb")
  d = b"email=%s&pc_login_pass=%s&token=%s" % (authentication["email"].encode(), authentication["pc_login_pass"].encode(), token)
  f.write(b"POST /client/%s/login HTTP/1.1\r\n" % client_id.encode())
  f.write(b"Host: zaiseki.jp\r\n")
  f.write(b"Cookie: %s\r\n" % session_id)
  f.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
  f.write(b"Content-Length: %d\r\n" % len(d))
  f.write(b"\r\n")
  f.write(d)
  if not MICROPY:
    f.flush()
  r = f.read()
  session_id = re.search(rb"PHPSESSID=[^;]+;", r).group(0)[:-1]
  del conn, f, r
  gc.collect()

  #######
  conn = get_conn()
  f = conn if MICROPY else conn.makefile("rwb")
  f.write(b"GET /client/%s HTTP/1.1\r\n" % client_id.encode())
  f.write(b"Host: zaiseki.jp\r\n")
  f.write(b"Cookie: %s\r\n" % session_id)
  f.write(b"\r\n")
  if not MICROPY:
    f.flush()
  r = f.read()
  conn.close()
  token = re.search(rb"token\" value=\"[^\"]*\"", r).group(0)[14:-1]
  del conn, f, r
  gc.collect()

  #######
  conn = get_conn()
  f = conn if MICROPY else conn.makefile("rwb")
  d = b"status_id=%d&destination=&back_date=&back_time=&back_flg=0&member=&token=%s" % (60180 if isPresence else 60182, token)
  f.write(b"POST /client/%s/zaiseki/update HTTP/1.1\r\n" % client_id.encode())
  f.write(b"Host: zaiseki.jp\r\n")
  f.write(b"Cookie: %s\r\n" % session_id)
  f.write(b"Content-Type: application/x-www-form-urlencoded\r\n")
  f.write(b"Content-Length: %d\r\n" % len(d))
  f.write(b"\r\n")
  f.write(d)
  if not MICROPY:
    f.flush()
  else:
    f.readline()
  del conn, f
  gc.collect()