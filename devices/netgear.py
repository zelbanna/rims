"""Module docstring.

Netgear module

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-ex.png"

from generic import Device as GenericDevice

######################################## Netgear ########################################

class Device(GenericDevice):

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID)

 def __str__(self):
  return "NetGear - {}".format(GenericDevice.__str__(self))

 def interfaces(self):
  from zdcp.Settings import Settings
  from netsnmp import VarList, Varbind, Session
  interfaces = {}
  try:
   objs = VarList(Varbind('.1.3.6.1.2.1.2.2.1.2'),Varbind('.1.3.6.1.2.1.31.1.1.1.18'),Varbind('.1.3.6.1.2.1.2.2.1.8'))
   session = Session(Version = 2, DestHost = self._ip, Community = Settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(objs)
   for entry in objs:
    intf = interfaces.get(int(entry.iid),{'name':"None",'description':"None"})
    if entry.tag == '.1.3.6.1.2.1.2.2.1.8':
     intf['state'] = 'up' if entry.val == '1' else 'down'
    if entry.tag == '.1.3.6.1.2.1.2.2.1.2':
     intf['name'] = "g%s"%entry.iid
    if entry.tag == '.1.3.6.1.2.1.31.1.1.1.18':
     intf['description'] = entry.val if entry.val != "" else "None"
    interfaces[int(entry.iid)] = intf
  except Exception as exception_error:
   self.log_msg("Generic : error traversing interfaces: " + str(exception_error))
  return interfaces

