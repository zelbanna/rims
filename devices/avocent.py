"""Module docstring.

Avocent PDU module

"""  
__author__  = "Zacharias El Banna"
__version__ = "17.10.4"
__status__  = "Production"

from generic import GenericDevice, ConfObject
from sdcp import PackageContainer as PC

######################################## PDU ########################################
#
# Avocent :-)
#

# Sort key function: lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])
class Device(GenericDevice, ConfObject):

 _getstatemap = { '1':'off', '2':'on' }
 _setstatemap = { 'off':'3', 'on':'2', 'reboot':'4' }

 @classmethod 
 def get_outlet_state(cls,state):
  return cls._getstatemap.get(state,'unknown')

 @classmethod
 def set_outlet_state(cls,state):
  return cls._setstatemap.get(state,'1')

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID)
  ConfObject.__init__(self)

 def get_type(self):
  return 'avocent'

 def __str__(self):
  return "Avocent - {}".format(GenericDevice.__str__(self))

 def set_state(self,slot,unit,state):
  from netsnmp import VarList, Varbind, Session
  try:
   # node = "pdu.outlet"
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['write_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind("enterprises", "10418.17.2.5.5.1.6.1.{}.{}".format(slot,unit) , Device.set_outlet_state(state) ,"INTEGER"))
   session.set(setobj)
   entry = self.get_entry("{}.{}".format(slot,unit))
   if entry:
    entry['state'] = state
   self.log_msg("Avocent : {0} set state to {1} on {2}.{3}".format(self._ip,state,slot,unit))
   return {'res':'success'}
  except Exception as exception_error:
   self.log_msg("Avocent : error setting state " + str(exception_error))
   return {'res':'failed', 'info':str(exception_error) }

 def set_name(self,slot,unit,name):
  from netsnmp import VarList, Varbind, Session
  try:
   name = name[:16]
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['write_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind("enterprises", "10418.17.2.5.5.1.4.1.{}.{}".format(slot,unit) , name, "OPAQUE"))
   session.set(setobj)
   entry = self.get_entry("{}.{}".format(slot,unit))
   if entry:
    entry['name'] = name
   return "{0}.{1}: {2}".format(slot,unit,name)
  except Exception as exception_error:
   self.log_msg("Avocent : error setting name " + str(exception_error))
   return "Error setting name {}".format(name)

 def load_snmp(self):
  from netsnmp import VarList, Varbind, Session
  try:
   outletobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.4'))
   stateobjs  = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.5'))
   slotobjs   = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(outletobjs)
   session.walk(stateobjs)
   session.walk(slotobjs)
   statedict = dict(map(lambda var: (var.tag[34:] + "." + var.iid, var.val), stateobjs))
   slotdict  = dict(map(lambda var: (var.iid, var.val),slotobjs))
   for outlet in outletobjs:
    # outlet.iid = outlet number
    slot = outlet.tag[34:]
    node = slot + "." + outlet.iid
    self._configitems[ node ] = { 'name': outlet.val, 'state':Device.get_outlet_state(statedict[node]), 'slotname':slotdict.get(slot,"unknown"), 'slot':slot, 'unit':outlet.iid }
  except Exception as exception_error:
   self.log_msg("Avocent : error loading conf " + str(exception_error))
 
 def get_slot_names(self):
  from netsnmp import VarList, Varbind, Session
  slots = []
  try:
   slotobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(slotobjs)
   for slot in slotobjs:
    slots.append([slot.iid, slot.val])
  except Exception as exception_error:
   self.log_msg("Avocent : error loading pdu member names " + str(exception_error), aPrint = True)
  return slots

 def get_slotunit(self, aSlot, aUnit):
  return self._configitems.get(aSlot +'.'+ aUnit,None)
