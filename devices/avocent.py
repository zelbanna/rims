"""Module docstring.

Avocent PDU module

"""
__author__  = "Zacharias El Banna"
__type__    = "pdu"

from rims.devices.generic import Device as GenericDevice
from rims.core.common import VarList, Session

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

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)

 def __str__(self): return "Avocent[%s,%s]"%(self._id,self._ip)

 #
 def set_state(self,slot,unit,state):
  from time import sleep
  try:
   ret = {}
   tag = ".1.3.6.1.4.1.10418.17.2.5.5.1.6.1"
   iid = "%s.%s"%(slot,unit)
   op  = Device.set_outlet_state(state)
   # snmpset -v2c -c %s %s %s i %s"%(self._ctx.config['snmp']['write'], self._ip, oid, op))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['write'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   setobj = VarList(tag,iid , op ,"INTEGER")
   res = session.set(setobj)
   sleep(0.5)
   if (session.ErrorInd == 0):
    ret['status'] = 'OK'
   else:
    ret['status'] = 'NOT_OK_FAILED'
    ret['info'] = 'SNMP_ERROR_%s'%session.ErrorInd
  except Exception as e:
   ret['status'] = 'NOT_OK_ERROR'
   ret['info'] = repr(e)
  self.log("Set state: %s on %s.%s - %s (%s)"%(state,slot,unit,ret['status'],ret.get('info','')))
  return ret

 #
 def get_state(self,slot,unit):
  ret = {'state':'unknown' }
  try:
   stateobj = VarList('.1.3.6.1.4.1.10418.17.2.5.5.1.5.1.%s.%s'%(slot,unit))
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.get(stateobj)
   if (session.ErrorInd == 0):
    ret['status'] = 'OK'
    ret['state'] = Device.get_outlet_state(stateobj[0].val.decode())
   else:
    ret['status'] = 'NOT_OK_FAILED'
    ret['info'] = 'SNMP_ERROR_%s'%session.ErrorInd
  except Exception as e:
   ret['info'] = repr(e)
   ret['status']  = 'NOT_OK_ERROR'
  if ret['status'] != 'OK':
   self.log("Error getting state: %s"%(ret['info']))
  return ret

 #
 def set_name(self,slot,unit,name):
  ret = {}
  try:
   name = name[:16].encode('utf-8')
   tag = ".1.3.6.1.4.1.10418.17.2.5.5.1.4.1"
   iid = "%s.%s"%(slot,unit)
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['write'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   setobj = VarList(tag , iid , name, "OPAQUE")
   session.set(setobj)
   if (session.ErrorInd == 0):
    ret['status'] = 'OK'
   else:
    ret['status'] = 'NOT_OK_FAILED'
    ret['info'] = 'SNMP_ERROR_%s'%session.ErrorInd
  except Exception as e:
   ret['info'] = repr(e)
   ret['status']  = 'NOT_OK_ERROR'
  return ret

 #
 def get_slot_names(self):
  # Slots are for multi slot PDUs which has several slots and ports in each slot. i.e. an outlet is numbered X.Y
  slots = []
  try:
   slotobjs = VarList('.1.3.6.1.4.1.10418.17.2.5.3.1.3')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(slotobjs)
   for slot in slotobjs:
    slots.append([slot.iid, slot.val.decode()])
  except Exception as e:
   self.log("Error loading pdu member names: %s"%(str(e)))
  return slots

 #
 def get_inventory(self):
  result = []
  try:
   outletobjs = VarList('.1.3.6.1.4.1.10418.17.2.5.5.1.4')
   stateobjs  = VarList('.1.3.6.1.4.1.10418.17.2.5.5.1.5')
   slotobjs   = VarList('.1.3.6.1.4.1.10418.17.2.5.3.1.3')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(outletobjs)
   session.walk(stateobjs)
   session.walk(slotobjs)
   slotdict  = dict([(var.iid, var.val.decode()) for var in slotobjs])
   for indx,outlet in enumerate(outletobjs,0):
    result.append({'slot':outlet.tag[34:],'unit':outlet.iid,'name':outlet.val.decode(),'state':Device.get_outlet_state(stateobjs[indx].val.decode()),'slotname':slotdict.get(outlet.tag[34:],"unknown")})
  except Exception as e:
   self.log("Error loading conf: %s"%(str(e)))
  return result
