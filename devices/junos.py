"""Module docstring.

Junos Router Base Class

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0.1GA"
__status__  = "Production"
__type__    = "network"
__oid__     = 2636

from generic import Device as GenericDevice
from netsnmp import VarList, Varbind, Session

################################ JUNOS Object #####################################
#

class Junos(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['up_interfaces','info' ]

 def __init__(self,aIP, aSettings):
  GenericDevice.__init__(self,aIP, aSettings)
  from jnpr.junos import Device as JunosDevice
  from jnpr.junos.utils.config import Config
  self._router = JunosDevice(self._ip, user=aSettings['netconf']['username'], password=aSettings['netconf']['password'], normalize=True)
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

 def interfaces(self):
  return {k:v for k,v in super(Junos,self).interfaces().iteritems() if v['name'][:3] in [ 'ge-', 'fe-', 'xe-', 'et-','st0','ae-','irb']}

 #
 # Netconf shit
 #
 def get_rpc(self):
  return self._router.rpc

 def get_dev(self):
  return self._router

 def get_interface_name(self, aifl):
  return self._interfacesname.get(aifl.split('.')[0])

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
   entry = {'Interface':ifd[0].text, 'State':ifd[2].text, 'SNMP':ifd[4].text, 'Type':ifd[5].text }
   # Split ge-0/0/0 into ge and 0/0/0, remove extra numbers for aeX interfaces
   tp = entry['Interface'].partition('-')[0].rstrip('0123456789')
   if tp in [ 'ge', 'fe', 'xe', 'et','st0','ae' ] and entry['State'] == "up":
    ret.append(entry)
  return ret

 def info(self):
  return [{'version':self._version,'model':self._model}]

 def configuration(self,argdict):
  base  = "set groups default_system"
  ret = ["set system host-name %s"%(argdict['hostname'])]
  if self._settings['netconf']['username'] == 'root':
   ret.append("set system root-authentication encrypted-password \"%s\""%(self._settings['netconf']['encrypted']))
  else:
   ret.append('set system login user %s class super-user'%(self._settings['netconf']['username']))
   ret.append('set system login user %s authentication encrypted-password "%s"'%(self._settings['netconf']['username'],self._settings['netconf']['encrypted']))
  ret.extend(['%s system domain-name %s'%(base,argdict['domain']),
              '%s system domain-search %s'%(base,argdict['domain']),
              '%s system login message \"Login to device %s\"'%(base,argdict['hostname']),
              '%s system name-server %s'%(base,self._settings['netconf']['dnssrv']),
              '%s system services ssh root-login allow'%base,
              '%s system services rest http'%base,
              '%s system services netconf ssh'%base,
              '%s system syslog user * any emergency'%base,
              '%s system syslog file messages any notice'%base,
              '%s system syslog file messages authorization info'%base,
              '%s system syslog file interactive-commands interactive-commands any'%base,
              '%s system archival configuration transfer-on-commit'%base,
              '%s system archival configuration archive-sites ftp://%s'%(base,self._settings['netconf']['anonftp']),
              '%s system commit persist-groups-inheritance'%base,
              '%s system ntp server %s'%(base,self._settings['netconf']['ntpsrv']),
              '%s routing-options static route 0.0.0.0/0 next-hop %s'%(base,argdict['gateway']),
              '%s routing-options static route 0.0.0.0/0 no-readvertise'%base,
              '%s snmp community %s clients %s/%s'%(base,self._settings['snmp']['read_community'],argdict['network'],argdict['mask']),
              '%s protocols lldp port-description-type interface-description'%base,
              '%s protocols lldp port-id-subtype interface-name'%base,
              '%s protocols lldp neighbour-port-info-display port-id'%base,
              '%s protocols lldp interface all'%base,
              '%s class-of-service host-outbound-traffic forwarding-class network-control'%base,
              'set apply-groups default_system'])
  return ret
