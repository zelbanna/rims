"""IPMI interworking module

- https://lime-technology.com/forum/index.php?topic=39238.0
- requires ipmitool to be installed on system and "in path"
- ipmitool -H <host> -U <username> -P <password> raw 0x3a 0x01 0x00 0x00 0x28 0x28 0x2d 0x2d 0x00 0x00

"""
__author__ = "Zacharias El Banna"

from rims.core.genlib import strToHex
from rims.devices.generic import Device as GenericDevice
from subprocess import check_output, check_call
from io import open
from os import devnull

################################### IPMI #######################################

class Device(GenericDevice):

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)

 def get_info(self, agrep):
  result = []
  readout = check_output("ipmitool -H " + self._ip + " -U " + self._rt.config['ipmi']['username'] + " -P " + self._rt.config['ipmi']['password'] + " sdr | grep -E '" + agrep + "'",shell=True).decode()
  for fanline in readout.split('\n'):
   if fanline != "":
    fan = fanline.split()
    result.append(fan[0] + ":" + fan[3] + ":" + fan[4])
  return result

 def set_fans(self, arear, afront):
  FNULL = open(devnull, 'w')
  rear  = strToHex(arear)
  front = strToHex(afront)
  ipmistring = "ipmitool -H " + self._ip + " -U " + self._rt.config['ipmi']['username'] + " -P " + self._rt.config['ipmi']['password'] + " raw 0x3a 0x01 0x00 0x00 " + rear + " " + rear + " " + front + " " + front + " 0x00 0x00"
  return check_call(ipmistring,stdout=FNULL,stderr=FNULL,shell=True)
