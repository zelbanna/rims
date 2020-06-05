"""IPMI interworking module

- https://lime-technology.com/forum/index.php?topic=39238.0
- requires ipmitool to be installed on system and "in path"
- ipmitool -H <host> -U <username> -P <password> raw 0x3a 0x01 0x00 0x00 0x28 0x28 0x2d 0x2d 0x00 0x00

"""
__author__ = "Zacharias El Banna"

from rims.devices.generic import Device as GenericDevice

################################### IPMI #######################################

class Device(GenericDevice):

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)

 def get_info(self, agrep):
  from subprocess import check_output
  result = []
  readout = check_output("ipmitool -H " + self._ip + " -U " + self._ctx.config['ipmi']['username'] + " -P " + self._ctx.config['ipmi']['password'] + " sdr | grep -E '" + agrep + "'",shell=True).decode()
  for fanline in readout.split('\n'):
   if fanline is not "":
    fan = fanline.split()
    result.append(fan[0] + ":" + fan[3] + ":" + fan[4])
  return result

 def set_fans(self, arear, afront):
  from io import open
  from os import devnull
  from subprocess import check_call
  from rims.core.genlib import strToHex
  FNULL = open(devnull, 'w')
  rear  = strToHex(arear)
  front = strToHex(afront)
  ipmistring = "ipmitool -H " + self._ip + " -U " + self._ctx.config['ipmi']['username'] + " -P " + self._ctx.config['ipmi']['password'] + " raw 0x3a 0x01 0x00 0x00 " + rear + " " + rear + " " + front + " " + front + " 0x00 0x00"
  return check_call(ipmistring,stdout=FNULL,stderr=FNULL,shell=True)
