"""Module docstring.

Avocent PDU module

"""
__author__  = "Zacharias El Banna"
__type__    = "pdu"

from rims.devices.generic import Device as GenericDevice
from rims.core.common import VarList, Varbind, Session

######################################## PDU ########################################

class Device(GenericDevice):

 _getstatemap = { '1':'off', '2':'on' }
 _setstatemap = { 'off':b'3', 'on':b'2', 'reboot':b'4' }

 @classmethod
 def get_functions(cls):
  return ['manage']

 @classmethod
 def get_outlet_state(cls,state):
  return cls._getstatemap.get(state,'unknown')

 @classmethod
 def set_outlet_state(cls,state):
  return cls._setstatemap.get(state,b'1')

 def __init__(self, aCTX, aIP):
  GenericDevice.__init__(self, aCTX, aIP)

 def __str__(self): return "Avocent(ip=%s)"%(self._ip)

 #
 def set_state(self,slot,unit,state):
  from time import sleep
  try:
   ret = {}
   tag = ".1.3.6.1.4.1.10418.17.2.5.5.1.6.1"
   iid = "%s.%s"%(slot,unit)
   op  = Device.set_outlet_state(state)
   # snmpset -v2c -c %s %s %s i %s"%(self._ctx.settings['snmp']['write'], self._ip, oid, op))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['write'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind(tag,iid , op ,"INTEGER"))
   res = session.set(setobj)
   sleep(0.5)
   if (session.ErrorInd == 0):
    self.log("Avocent - {0} set state: {1} on {2}.{3}".format(self._ip,state,slot,unit))
    ret['status'] = 'OK'
   else:
    self.log("Avocent - {0} failed set state: {1} on {2}.{3}".format(self._ip,state,slot,unit))
    ret['status'] = 'NOT_OK_%s'%session.ErrorInd
  except Exception as e:
   self.log("Avocent(%s) - error setting state: %s"%(self._ip,str(e)))
   ret['info'] = repr(exception_error)
   ret['status'] = 'NOT_OK'
  return ret

 #
 def get_state(self,slot,unit):
  try:
   stateobj = VarList(Varbind(".1.3.6.1.4.1.10418.17.2.5.5.1.5.1.%s.%s"%(slot,unit)))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['read'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(stateobj)
   return {'status':"OK" if (session.ErrorInd == 0) else "NOT_OK", 'state':Device.get_outlet_state(stateobj[0].val.decode()) }
  except Exception as e:
   self.log("Avocent(%s) : error getting state: %s"%(self._ip,str(e)))
   return {'status':'NOT_OK','info':str(e), 'state':'unknown' }

 #
 def set_name(self,slot,unit,name):
  try:
   name = name[:16].encode('utf-8')
   tag = ".1.3.6.1.4.1.10418.17.2.5.5.1.4.1"
   iid = "%s.%s"%(slot,unit)
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['write'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   setobj = VarList(Varbind(tag , iid , name, "OPAQUE"))
   session.set(setobj)
   return "%s.%s:'%s'"%(slot,unit,name)
  except Exception as e:
   self.log("Avocent(%s) : error setting name: %s"%(self._ip,str(e)))
   return "Error setting name '%s'"%(name)

 #
 def get_slot_names(self):
  slots = []
  try:
   slotobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['read'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(slotobjs)
   for slot in slotobjs:
    slots.append([slot.iid, slot.val.decode()])
  except Exception as e:
   self.log("Avocent(%s) : error loading pdu member names: %s"%(self._ip,str(e)))
  return slots

 #
 def get_inventory(self):
  result = []
  try:
   outletobjs = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.4'))
   stateobjs  = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.5.1.5'))
   slotobjs   = VarList(Varbind('.1.3.6.1.4.1.10418.17.2.5.3.1.3'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.settings['snmp']['read'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(outletobjs)
   session.walk(stateobjs)
   session.walk(slotobjs)
   slotdict  = dict([(var.iid, var.val.decode()) for var in slotobjs])
   for indx,outlet in enumerate(outletobjs,0):
    result.append({'slot':outlet.tag[34:],'unit':outlet.iid,'name':outlet.val.decode(),'state':Device.get_outlet_state(stateobjs[indx].val.decode()),'slotname':slotdict.get(outlet.tag[34:],"unknown")})
  except Exception as e:
   self.log("Avocent(%s) : error loading conf: %s"%(self._ip,str(e)))
  return result
