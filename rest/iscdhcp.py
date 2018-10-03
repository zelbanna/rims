"""ISCDHCP API module. The specific ISCDHCP REST interface to reload and fetch info from ISCDHCP server.
Settings under section 'iscdhcp':
 - reload (argument from CLI)
 - active (file storing current leases)
 - static (file storing configuration for ISCDHCP

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aDict, aCTX):
 """Function docstring for leases TBD

 Args:
  - binding (optional). default "active"

 Output:
 """
 def GL_ip2int(addr):
  from struct import unpack
  from socket import inet_aton
  return unpack("!I", inet_aton(addr))[0]

 result = []
 lease  = {}
 with open(aCTX.settings['iscdhcp']['active'],'r') as leasefile:
  for line in leasefile:
   if line == '\n':
    continue
   parts = line.split()
   if   parts[0] == 'lease' and parts[2] == '{':
    lease['ip'] = parts[1]
   elif parts[0] == '}':
    if aDict.get('binding','active') == lease['binding']:
     result.append(lease)
    lease = {}
   elif parts[0] == 'hardware' and parts[1] == 'ethernet':
    lease['mac'] = parts[2][:-1]
   elif parts[0] == 'binding':
    lease['binding'] = parts[2][:-1]
   elif parts[0] == 'starts' or parts[0] == 'ends':
    lease[parts[0]] = " ".join(parts[2:])[:-1]
   elif parts[0] == 'client-hostname':
    lease['hostname'] = parts[1][1:-2]
  result.sort(key=lambda d: GL_ip2int(d['ip']))
  return {'data':result }

#
#
def sync(aDict, aCTX):
 """Function docstring for sync:  reload the DHCP server to use updated info

 Args:
  - id (required). Server id on master node

 Output:
 """
 from time import localtime, strftime
 entries = aCTX.node_call('master','device','server_macs',{'id':aDict['id']})
 # Create file
 with open(aCTX.settings['iscdhcp']['static'],'w') as config_file:
  config_file.write("# Created: %s\n"%( strftime('%Y-%m-%d %H:%M:%S', localtime()) ))
  for entry in entries['data']:
   config_file.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Id: {3}, Network: {4}\n".format("%(hostname)s.%(domain)s"%entry,entry['mac'],entry['ip'],entry['id'],entry['network']))

 # Reload
 from subprocess import check_output, CalledProcessError
 ret = {}
 try:
  ret['output'] = check_output(aCTX.settings['iscdhcp']['reload'].split())
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output

 ret['result'] = 'NOT_OK' if ret['output'] else 'OK'
 return ret

#
#
def update(aDict, aCTX):
 """Function docstring for check: update specific entry

 Args:
  - id (optional)
  - hostname (optional required)
  - domain (optional required)
  - mac (optional required)
  - ip (optional required)
  - network (optional required)

 Output:
 """
 devices = {}
 ret = {}

 with open(aCTX.settings['iscdhcp']['static'],'r') as config_file:
  for line in config_file:
   if line[0] == '#':
    continue
   parts = line.split()
   id = int(parts[11][:-1])
   devices[id] = {'id':id,'fqdn':parts[1],'mac':parts[5],'ip':parts[7],'network':parts[3]}
 if aDict.get('id'):
  devices[aDict['id']] = {'id':aDict['id'],'fqdn':"%(hostname)s.%(domain)s"%aDict,'mac':aDict['mac'],'ip':aDict['ip'],'network':aDict['network']}
  # Create file
  with open(aCTX.settings['iscdhcp']['static'],'w') as config_file:
   for entry in devices:
    config_file.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Id: {3}, Network: {4}\n".format("%(hostname)s.%(domain)s"%entry,entry['mac'],entry['ip'],entry['id'],entry['network']))
  # Reload
  from subprocess import check_output, CalledProcessError
  ret = {}
  try:
   ret['output'] = check_output(aCTX.settings['iscdhcp']['reload'].split())
  except CalledProcessError as c:
   ret['code'] = c.returncode
   ret['output'] = c.output

  ret['result'] = 'NOT_OK' if ret['output'] else 'OK'
 else:
  ret['result'] = 'OK'
  ret['devices'] = devices
 return ret

#
#
def restart(aDict, aCTX):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 from subprocess import check_output, CalledProcessError
 ret = {}
 try:
  ret['output'] = check_output(aCTX.settings['iscdhcp']['reload'].split())
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output
 ret['result'] = 'NOT_OK' if ret['output'] else 'OK'
 return ret
