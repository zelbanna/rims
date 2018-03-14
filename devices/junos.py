"""Module docstring.

Junos Router Base Class

"""
__author__  = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__  = "Production"
__type__    = "network"

from generic import Device as GenericDevice
from netsnmp import VarList, Varbind, Session

################################ JUNOS Object #####################################
#

class Junos(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['up_interfaces','lldp' ]

 def __init__(self,aIP,aID = None):
  GenericDevice.__init__(self,aIP,aID)
  from jnpr.junos import Device as JunosDevice
  from jnpr.junos.utils.config import Config
  from .. import SettingsContainer as SC
  self._router = JunosDevice(self._ip, user=SC.netconf['username'], password=SC.netconf['password'], normalize=True)
  self._config = Config(self._router)
  self._model = ""
  self._version = ""
  self._interfacesname = {}
 
 def __str__(self):
  return "{} Model:{} Version:{}".format(str(self._router), self._model, self._version)

 def __enter__(self):
  if self.connect():
   return self
  else:
   raise RuntimeError("Error connecting to host")
 
 def __exit__(self, *ctx_info):
  self.close()

 def connect(self):
  try:
   self._router.open()
   self._model = self._router.facts['model']
   self._version = self._router.facts['version']
  except Exception as err:
   self.log_msg("System Error - Unable to connect to router: " + str(err))
   return False
  return True

 def close(self):
  try:
   self._router.close()
  except Exception as err:
   self.log_msg("System Error - Unable to properly close router connection: " + str(err))

 def get_rpc(self):
  return self._router.rpc

 def get_dev(self):
  return self._router

 def get_interface_name(self, aifl):
  return self._interfacesname.get(aifl.split('.')[0])
 
 #
 # Netconf shit
 # 
 def ping_rpc(self,ip):
  result = self._router.rpc.ping(host=ip, count='1')
  return len(result.xpath("ping-success"))

 def get_facts(self,akey):
  return self._router.facts[akey]

 def load_interfaces_name(self):
  interfaces = self._router.rpc.get_interface_information(descriptions=True)
  for interface in interfaces:
   ifd         = interface.find("name").text
   description = interface.find("description").text
   self._interfacesname[ifd] = description

 def up_interfaces(self):
  interfaces = self._router.rpc.get_interface_information()
  ret = []
  for ifd in interfaces:
   entry = {'Interface':ifd[0].text, 'State':ifd[2].text, 'SNMP':ifd[4].text, 'Description':ifd[5].text }
   # Split ge-0/0/0 into ge and 0/0/0, remove extra numbers for aeX interfaces
   tp = entry['Interface'].partition('-')[0].rstrip('0123456789')
   if tp in [ 'ge', 'fe', 'xe', 'et','st0','ae' ] and entry['State'] == "up":
    ret.append(entry)
  return ret

 def lldp(self):
  neighbors = self._router.rpc.get_lldp_neighbors_information()
  ret = []
  for neigh in neighbors:
   # Remote system always last, remote port second to last, local is always first and pos 3 (2) determines if there is a mac or not
   fields = len(neigh)-1
   ret.append({ 'Neighbor':neigh[fields].text, 'MAC':neigh[3].text if neigh[2].text == "Mac address" else '-','Local_port':neigh[0].text,'Destination_port':neigh[fields-1].text })
  return ret

 def configuration(self,argdict):
  from .. import SettingsContainer as SC
  base  = "set groups default_system"
  ret = ["set system host-name %s"%(argdict['hostname'])]
  if SC.netconf['username'] == 'root':
   ret.append("set system root-authentication encrypted-password \"%s\""%(SC.netconf['encrypted']))
  else:
   ret.append('set system login user %s class super-user'%(SC.netconf['username']))
   ret.append('set system login user %s authentication encrypted-password "%s"'%(SC.netconf['username'],SC.netconf['encrypted']))
  ret.extend(['%s system domain-name %s'%(base,argdict['domain']),
              '%s system domain-search %s'%(base,argdict['domain']),
              '%s system name-server %s'%(base,SC.netconf['dnssrv']),
              '%s system services ssh root-login allow'%base,
              '%s system services netconf ssh'%base,
              '%s system syslog user * any emergency'%base,
              '%s system syslog file messages any notice'%base,
              '%s system syslog file messages authorization info'%base,
              '%s system syslog file interactive-commands interactive-commands any'%base,
              '%s system archival configuration transfer-on-commit'%base,
              '%s system archival configuration archive-sites ftp://%s'%(base,SC.netconf['anonftp']),
              '%s system commit persist-groups-inheritance'%base,
              '%s system ntp server %s'%(base,SC.netconf['ntpsrv']),
              '%s routing-options static route 0.0.0.0/0 next-hop %s'%(base,argdict['gateway']),
              '%s routing-options static route 0.0.0.0/0 no-readvertise'%base,
              '%s snmp community %s clients %s/%s'%(base,SC.snmp['read_community'],argdict['subnet'],argdict['mask']),
              '%s protocols lldp port-id-subtype interface-name'%base,
              '%s protocols lldp interface all'%base,
              '%s class-of-service host-outbound-traffic forwarding-class network-control'%base,
              'set apply-groups default_system'])
  return ret
