"""Module docstring.

Avocent PDU module

"""
__author__  = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__  = "Production"
__type__    = "pdu"

from generic import Device as GenericDevice
from .. import SettingsContainer as SC

######################################## PDU ########################################

class Device(GenericDevice):

 _getstatemap = { '1':'off', '2':'on' }
 _setstatemap = { 'off':'3', 'on':'2', 'reboot':'4' }

 @classmethod
 def get_functions(cls):
  return ['manage']

 @classmethod
 def get_outlet_state(cls,state):
  return cls._getstatemap.get(state,'unknown')

 @classmethod
 def set_outlet_state(cls,state):
  return cls._setstatemap.get(state,'1')

 def __init__(self, aIP, aID = None):
  GenericDevice.__init__(self,aIP, aID)

 def __str__(self):
  return "Avocent[%s]: %s"%(__type__,GenericDevice.__str__(self))

 def set_state(self,slot,unit,state):
  from netsnmp import VarList, Varbind, Session
  try:
   session = Session(Version = 2, DestHost = self._ip, Community = SC.snmp['write_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind("enterprises", "10418.17.2.5.5.1.6.1.{}.{}".format(slot,unit) , Device.set_outlet_state(state) ,"INTEGER"))
   session.set(setobj)
   self.log_msg("Avocent : {0} set state to {1} on {2}.{3}".format(self._ip,state,slot,unit))
   return {'res':'OK'}
  except Exception as exception_error:
   self.log_msg("Avocent : error setting state " + str(exception_error))
   return {'res':'NOT_OK', 'info':str(exception_error) }

 def set_name(self,slot,unit,name):
  from netsnmp import VarList, Varbind, Session
  try:
   name = name[:16]
   session = Session(Version = 2, DestHost = self._ip, Community = SC.snmp['write_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind("enterprises", "10418.17.2.5.5.1.4.1.{}.{}".format(slot,unit) , name, "OPAQUE"))
   session.set(setobj)
   return "{0}.{1}:'{2}'".format(slot,unit,name)
  except Exception as exception_error:
   self.log_msg("Avocent : error setting name " + str(exception_error))
   return "Error setting name '%s'"%(name)

 def get_state(self,slot,unit):
  from netsnmp import VarList, Varbind, Session
  try:
   stateobj = VarList(Varbind(".1.3.6.1.4.1.10418.17.2.5.5.1.5.1.{}.{}".format(slot,unit)))
   session = Session(Version = 2, DestHost = self._ip, Community = SC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(stateobj)
   return {'res':'OK', 'state':Device.get_outlet_state(stateobj[0].val) }
  except Exception,e:
   self.log_msg("Avocent : error getting state:" + str(e))
   return {'res':'NOT_OK','info':str(e), 'state':'unknown' }

 #
 #
 def get_slot_names(self):
  from netsnmp import VarList, Varbind, Session
  slots = []
  try:
   slotobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(slotobjs)
   for slot in slotobjs:
    slots.append([slot.iid, slot.val])
  except Exception as exception_error:
   self.log_msg("Avocent : error loading pdu member names " + str(exception_error))
  return slots

 #
 #
 def get_inventory(self):
  from netsnmp import VarList, Varbind, Session
  result = []
  try:
   outletobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.4'))
   stateobjs  = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.5'))
   slotobjs   = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = SC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(outletobjs)
   session.walk(stateobjs)
   session.walk(slotobjs)
   slotdict  = dict(map(lambda var: (var.iid, var.val),slotobjs))
   for indx,outlet in enumerate(outletobjs,0):
    result.append({'slot':outlet.tag[34:],'unit':outlet.iid,'name':outlet.val,'state':Device.get_outlet_state(stateobjs[indx].val),'slotname':slotdict.get(outlet.tag[34:],"unknown")})
  except Exception as exception_error:
   self.log_msg("Avocent : error loading conf " + str(exception_error))
  return result
