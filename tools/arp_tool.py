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

if __name__ == "__main__":
 arpdict = load_arp()
 for key,arp in arpdict.iteritems():
  print "{} -> {}".format(key,arp)
