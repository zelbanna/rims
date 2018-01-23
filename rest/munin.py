"""Module docstring.

REST Module for graph interaction


"""  
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
# ip, type_name,fqdn
#
def detect(aentry):
 from .. import PackageContainer as PC
 from ..core import genlib as GL
 ret = {'result':'NOT_OK'}
 if not GL.ping_os(aentry['ip']):
  return ret

 activeinterfaces = []
 type = aentry['type_name']
 fqdn = aentry['fqdn']
 try:
  if type in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
   from ..devices.junos import Junos
   if not type == 'wlc':
    with Junos(aentry['ip']) as jdev:
     activeinterfaces = jdev.get_up_interfaces()
   with open(PC.generic['graph']['plugins'], 'a') as graphfile:
    graphfile.write('ln -s /usr/local/sbin/plugins/snmp__{0} /etc/munin/plugins/snmp_{1}_{0}\n'.format(type,fqdn))
    graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + fqdn + '_uptime\n')
    graphfile.write('ln -s /usr/share/munin/plugins/snmp__users  /etc/munin/plugins/snmp_' + fqdn + '_users\n')
    for ifd in activeinterfaces:
     graphfile.write('ln -s /usr/share/munin/plugins/snmp__if_    /etc/munin/plugins/snmp_' + fqdn + '_if_'+ ifd['SNMP'] +'\n')
  elif type == "esxi":
   with open(PC.generic['graph']['plugins'], 'a') as graphfile:
    graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + fqdn + '_uptime\n')              
    graphfile.write('ln -s /usr/local/sbin/plugins/snmp__esxi    /etc/munin/plugins/snmp_' + fqdn + '_esxi\n')
 except Exception as err:
  from ..core.logger import log
  log("Graph detect - error: [{}]".format(str(err)))
 else:
  ret['result'] = 'OK'
 return ret
