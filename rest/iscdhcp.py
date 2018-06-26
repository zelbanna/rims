"""ISCDHCP API module. The specific ISCDHCP REST interface to reload and fetch info from ISCDHCP server.
Settings:
 - reload (argument from CLI)
 - active (file storing current leases)
 - static (file storing configuration for ISCDHCP

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
#
def leases(aDict):
 """Function docstring for leases TBD

 Args:
  - type (required)

 Output:
 """
 def GL_ip2int(addr):
  from struct import unpack
  from socket import inet_aton
  return unpack("!I", inet_aton(addr))[0]

 from zdcp.SettingsContainer import SC
 result = []
 lease  = {}
 with open(SC['iscdhcp']['active'],'r') as leasefile:
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
  result.sort(key=lambda d: GL_ip2int(d['ip']))
  return {'data':result }

#
def update_server(aDict):
 """Function docstring for update_server:  reload the DHCP server to use updated info

 Args:
  - entries (required). entries is a list of dict objects containing hostname, mac, ip etc

 Output:
 """
 from zdcp.SettingsContainer import SC
 from zdcp.core.common import node_call
 entries = node_call('master','device','device_list',{'field':'mac','search':'all','extra':['mac']})
 # Create file
 with open(SC['iscdhcp']['static'],'w') as leasefile:
  for entry in entries:
   leasefile.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Id: {3}\n".format("%(hostname)s.%(domain)s"%entry,entry['mac'],entry['ip'],entry['id']))

 # Reload
 from subprocess import check_output, CalledProcessError
 ret = {}
 try:
  ret['output'] = check_output(SC['iscdhcp']['reload'].split())
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output

 ret['result'] = 'NOT_OK' if ret['output'] else 'OK'
 return ret
