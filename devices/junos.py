"""Junos Router Base Class"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__oid__     = 2636

from rims.devices.generic import Device as GenericDevice

################################ JUNOS Object #####################################
#

class Junos(GenericDevice):

 @classmethod
 def get_data_points(cls):
  return [
   ('chassis','cpu=RE','temp','.1.3.6.1.4.1.2636.3.1.13.1.7.9.1.0.0'),
   ('chassis','cpu=RE','load','.1.3.6.1.4.1.2636.3.1.13.1.8.9.1.0.0')
  ]

 def interfaces(self):
  return {k:v for k,v in super(Junos,self).interfaces().items() if v['name'][:3] in [ 'ge-', 'fe-', 'xe-', 'et-','st0','ae-','irb','vla','fxp','em0','vme']}

 def configuration(self,argdict):
  base  = "set groups default_system"
  ret = ['delete groups default_system','set apply-groups default_system',"set system host-name %s"%(argdict['hostname'])]
  if self._rt.config['netconf']['username'] == 'root':
   ret.append('set system root-authentication encrypted-password "%s"'%(self._rt.config['netconf']['encrypted']))
  else:
   ret.append('%s system login user %s class super-user'%(base,self._rt.config['netconf']['username']))
   ret.append('%s system login user %s authentication encrypted-password "%s"'%(base,self._rt.config['netconf']['username'],self._rt.config['netconf']['encrypted']))
  ret.extend(['set system services netconf ssh',
              'set system services ssh root-login allow',
              '%s system domain-name %s'%(base,argdict['domain']),
              '%s system domain-search %s'%(base,argdict['domain']),
              '%s system login message \"Welcome, this is device %s\"'%(base,argdict['hostname']),
              '%s system services rest http'%base,
              '%s system syslog user * any emergency'%base,
              '%s system syslog file messages any notice'%base,
              '%s system syslog file messages authorization info'%base,
              '%s system syslog file interactive-commands interactive-commands any'%base,
              '%s system archival configuration transfer-on-commit'%base,
              '%s system commit persist-groups-inheritance'%base,
              '%s system management-instance'%base,
              '%s snmp community %s clients %s/%s'%(base,self._rt.config['snmp']['read'],argdict['network'],argdict['mask']),
              '%s snmp community %s clients %s'%(base,self._rt.config['snmp']['read'],self._rt.config['snmp']['network']),
              '%s snmp community pejlro21 routing-instance mgmt_junos'%base,
              '%s snmp routing-instance-access'%base,
              '%s protocols lldp port-description-type interface-description'%base,
              '%s protocols lldp port-id-subtype interface-name'%base,
              '%s protocols lldp neighbour-port-info-display port-id'%base,
              '%s protocols lldp interface all'%base])

  ret.append('%s routing instances mgmt_junos routing-options static route 0.0.0.0/0 next-hop %s'%(base,argdict['gateway']))
  ret.append('%s routing instances mgmt_junos routing-options static route 0.0.0.0/0 no-readvertise'%base)
  if self._rt.config['netconf'].get('anonftp'):
   ret.append('%s system archival configuration archive-sites ftp://%s'%(base,self._rt.config['netconf']['anonftp']))
  if self._rt.config['netconf'].get('dns'):
   ret.append('%s system name-server %s routing-instance mgmt_junos'%(base,self._rt.config['netconf']['dns']))
  if self._rt.config['netconf'].get('ntp'):
   ret.append('%s system ntp server %s routing-instance mgmt_junos'%(base,self._rt.config['netconf']['ntp']))
  if self._rt.config.get('tacplus'):
   pass

  return ret

