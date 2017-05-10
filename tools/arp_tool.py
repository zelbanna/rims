#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Arp tool

"""
__author__ = "Zacharias El Banna"
__version__ = "11.0"
__status__ = "Production"

def load_arp():
 ret = {}
 with open('/proc/net/arp') as f:
  _ = f.readline()
  for data in f:
   ( ip, _, _, mac, _, _ ) = data.split()
   if not mac == '00:00:00:00:00:00':
    ret[ip] = mac
 return ret

def update_db():
 from sys import path
 path.append('../')
 import sdcp.core.GenLib as GL
 db = GL.DB()
 db.connect()
 db.do("SELECT ip,mac FROM devices")
 rows = db.get_all_rows()
 print rows

if __name__ == "__main__":
 update_db()
