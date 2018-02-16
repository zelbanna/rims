"""Module docstring.

ISC DHCP API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "18.02.09GA"
__status__ = "Production"

#
#
#
def leases(aDict):
 """Function description for leases TBD

 Args:
  - type (required)

 Extra:
 """
 from ..core.logger import log
 from ..core import genlib as GL
 from .. import SettingsContainer as SC
 result = []
 lease  = {}
 with open(SC.dhcp['active'],'r') as leasefile: 
  for line in leasefile:
   if line == '\n':
    continue
   parts = line.split()
   if   parts[0] == 'lease' and parts[2] == '{':
    lease['ip'] = parts[1]
   elif parts[0] == '}':
    if lease.pop('binding') == aDict['type']:
     result.append(lease)
    lease = {}
   elif parts[0] == 'hardware' and parts[1] == 'ethernet':
    lease['mac'] = parts[2][:-1] 
   elif parts[0] == 'binding':
    lease['binding'] = parts[2][:-1] 
   elif parts[0] == 'starts' or parts[0] == 'ends':
    lease[parts[0]] = " ".join(parts[2:])[:-1]
   elif parts[0] == 'client-hostname':
    lease['hostname'] = parts[1][:-1]
  result.sort(key=lambda d: GL.ip2int(d['ip']))
  return {'data':result }

#
def update_server(aDict):
 """Function description for update_server:  reload the DHCP server to use new info

 Args:
  - entries (required). entries is a list of dict objects containing hostname, mac, ip etc

 Extra:
 """
 from .. import SettingsContainer as SC
 entries = aDict['entries']
 # Create new file
 with open(SC.dhcp['static'],'w') as leasefile:
  for entry in entries:
   leasefile.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Subnet {3}, Id: {4}\n".format(entry['fqdn'],entry['mac'],entry['ip'],entry['subnet_id'],entry['id'])) 

 # Reload
 from subprocess import check_output, CalledProcessError
 commands = SC.dhcp['reload'].split()
 ret = {}
 try:
  ret['output'] = check_output(commands)
 except CalledProcessError, c:
  ret['code'] = c.returncode
  ret['output'] = c.output
 return ret
