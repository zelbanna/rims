"""Module docstring.

Avocent PDU module

"""
__author__  = "Zacharias El Banna"
__type__    = "pdu"

from rims.devices.generic import Device as GenericDevice
from easysnmp import Session
from time import sleep

######################################## PDU ########################################

class Device(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['manage']

 @classmethod
 def get_outlet_state(cls,state):
  return { '1':'off', '2':'on' }.get(state,'unknown')

 @classmethod
 def set_outlet_state(cls,state):
  return { 'off':b'3', 'on':b'2', 'reboot':b'4' }.get(state,b'1')

 def __init__(self, aRT, aID, aIP = None):
  GenericDevice.__init__(self, aRT, aID, aIP)

 #
 def set_state(self,slot,unit,state):
  try:
   ret = {}
   tag = ".1.3.6.1.4.1.10418.17.2.5.5.1.6.1.%s.%s"%(slot,unit)
   op  = Device.set_outlet_state(state)
   # snmpset -v2c -c %s %s %s i %s"%(self._rt.config['snmp']['write'], self._ip, oid, op))
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['write'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   ret['info'] = session.set(tag , op ,"INTEGER")
   sleep(0.5)
   ret['status'] = 'OK'
  except Exception as e:
   ret['status'] = 'NOT_OK_ERROR'
   ret['info'] = repr(e)
  self.log("Set state: %s on %s.%s - %s (%s)"%(state,slot,unit,ret['status'],ret.get('info','')))
  return ret

 #
 def get_state(self,slot,unit):
  ret = {'state':'unknown' }
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   stateobj = session.get('.1.3.6.1.4.1.10418.17.2.5.5.1.5.1.%s.%s'%(slot,unit))
   ret['status'] = 'OK'
   ret['state'] = Device.get_outlet_state(stateobj.val)
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
   tag = '.1.3.6.1.4.1.10418.17.2.5.5.1.4.1.%s.%s'%(slot,unit)
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['write'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   ret['info'] = session.set(tag , name, "OPAQUE"))
   ret['status'] = 'OK'
  except Exception as e:
   ret['info'] = repr(e)
   ret['status']  = 'NOT_OK_ERROR'
  return ret

 #
 def get_slot_names(self):
  # Slots are for multi slot PDUs which has several slots and ports in each slot. i.e. an outlet is numbered X.Y
  slots = []
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   slotobjs = session.walk('.1.3.6.1.4.1.10418.17.2.5.3.1.3')
   for slot in slotobjs:
    slots.append([slot.oid_index, slot.value])
  except Exception as e:
   self.log("Error loading pdu member names: %s"%(str(e)))
  return slots

 #
 def get_inventory(self):
  result = []
  try:
   session = Session(version = 2, hostname = self._ip, community = self._rt.config['snmp']['read'], use_numeric = True, timeout = int(self._rt.config['snmp'].get('timeout',3)), retries = 2)
   outletobjs = session.walk('.1.3.6.1.4.1.10418.17.2.5.5.1.4')
   stateobjs  = session.walk('.1.3.6.1.4.1.10418.17.2.5.5.1.5')
   slotobjs   = session.walk('.1.3.6.1.4.1.10418.17.2.5.3.1.3')
   slotdict  = dict([(var.oid_index, var.value) for var in slotobjs])
   for indx,outlet in enumerate(outletobjs,0):
    result.append({'slot':outlet.oid[34:],'unit':outlet.oid_index,'name':outlet.value,'state':Device.get_outlet_state(stateobjs[indx].value),'slotname':slotdict.get(outlet.oid[34:],"unknown")})
  except Exception as e:
   self.log("Error loading conf: %s"%(str(e)))
  return result
