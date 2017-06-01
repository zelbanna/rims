"""Program docstring.

MAC tools

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

def load_macs():
 arps = {}
 try:
  with open('/proc/net/arp') as f:
   _ = f.readline()
   for data in f:
    ( ip, _, _, mac, _, _ ) = data.split()
    if not mac == '00:00:00:00:00:00':
     arps[ip] = mac
 except:
  print "Problems opening /proc/net/arp"
 return arps
