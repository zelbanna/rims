"""Junos Router Base Class"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__oid__     = 2636

from rims.devices.generic import Device as GenericDevice

################################ JUNOS Object #####################################
#

class Junos(GenericDevice):

 @classmethod
 def get_functions(cls):
  return ['up_interfaces','info' ]

 @classmethod
 def get_data_points(cls):
  return [
   ('chassis','cpu=RE','temp','.1.3.6.1.4.1.2636.3.1.13.1.7.9.1.0.0'),
   ('chassis','cpu=RE','load','.1.3.6.1.4.1.2636.3.1.13.1.8.9.1.0.0')
  ]

 def __init__(self, aCTX, aID, aIP):
  GenericDevice.__init__(self, aCTX, aID, aIP)
  self._interfacesname = {}
  self._router  = None

 def __enter__(self):
  if self.connect():
   return self
  else:
   raise RuntimeError("Error connecting to host")

 def __exit__(self, *ctx_info):
  self.close()

 def connect(self):
  from jnpr.junos import Device as JunosDevice
  if not self._router:
   self._router = JunosDevice(self._ip, user=self._ctx.config['netconf']['username'], password=self._ctx.config['netconf']['password'], normalize=True)
  try:
   self._router.open()
  except Exception as err:
   self.log("Unable to connect:" + str(err)[:72])
   return False
  return True

 def close(self):
  try:
   self._router.close()
  except Exception as err:
   self.log("System Error - Unable to properly close router connection: " + str(err))

 def interfaces(self):
  return {k:v for k,v in super(Junos,self).interfaces().items() if v['name'][:3] in [ 'ge-', 'fe-', 'xe-', 'et-','st0','ae-','irb','vla','fxp','em0','vme']}

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
  return [{'Version':self._router.facts['version'],'Model':self._router.facts['model']}]

 def configuration(self,argdict):
  base  = "set groups default_system"
  ret = ["set system host-name %s"%(argdict['hostname'])]
  if self._ctx.config['netconf']['username'] == 'root':
   ret.append('set system root-authentication encrypted-password "%s"'%(self._ctx.config['netconf']['encrypted']))
  else:
   ret.append('set system login user %s class super-user'%(self._ctx.config['netconf']['username']))
   ret.append('set system login user %s authentication encrypted-password "%s"'%(self._ctx.config['netconf']['username'],self._ctx.config['netconf']['encrypted']))
  ret.extend(['%s system domain-name %s'%(base,argdict['domain']),
              '%s system domain-search %s'%(base,argdict['domain']),
              '%s system login message \"this is device %s\"'%(base,argdict['hostname']),
              '%s system services ssh root-login allow'%base,
              '%s system services rest http'%base,
              '%s system services netconf ssh'%base,
              '%s system syslog user * any emergency'%base,
              '%s system syslog file messages any notice'%base,
              '%s system syslog file messages authorization info'%base,
              '%s system syslog file interactive-commands interactive-commands any'%base,
              '%s system archival configuration transfer-on-commit'%base,
              '%s system commit persist-groups-inheritance'%base,
              '%s routing-options static route 0.0.0.0/0 next-hop %s'%(base,argdict['gateway']),
              '%s routing-options static route 0.0.0.0/0 no-readvertise'%base,
              '%s snmp community %s clients %s/%s'%(base,self._ctx.config['snmp']['read'],argdict['network'],argdict['mask']),
              '%s protocols lldp port-description-type interface-description'%base,
              '%s protocols lldp port-id-subtype interface-name'%base,
              '%s protocols lldp neighbour-port-info-display port-id'%base,
              '%s protocols lldp interface all'%base])

  if self._ctx.ip:
   ret.append('%s snmp community %s clients %s/%s'%(base,self._ctx.config['snmp']['read'],self._ctx.ip,self._ctx.ip.max_prefixlen))

  if self._ctx.config.get('tacplus'):
   pass
  if self._ctx.config['netconf'].get('dns'):
   ret.append('%s system name-server %s'%(base,self._ctx.config['netconf']['dns']))
  if self._ctx.config['netconf'].get('ntp'):
   ret.append('%s system ntp server %s'%(base,self._ctx.config['netconf']['ntp']))
  if self._ctx.config['netconf'].get('anonftp'):
   ret.append('%s system archival configuration archive-sites ftp://%s'%(base,self._ctx.config['netconf']['anonftp']))
  ret.append('set apply-groups default_system')
  return ret
