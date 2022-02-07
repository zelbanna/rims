"""ISCDHCP API module. The specific ISCDHCP REST interface to reload and fetch info from ISCDHCP server."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
# Writes IPv4 entries into DHCPd.conf file
#
def __write_file(aFile,aEntries):
 # Create file
 from time import strftime, localtime
 from ipaddress import ip_address
 with open(aFile,'w') as config_file:
  config_file.write("# Modified: %s\n"%( strftime('%Y-%m-%d %H:%M:%S', localtime()) ))
  for entry in aEntries:
   if ip_address(entry['ip']).version == 4:
    config_file.write("host {0: <10} {{ hardware ethernet {1}; fixed-address {2}; }} # Network: {3}\n".format(entry['id'],entry['mac'],entry['ip'],entry['network']))
 return True

#
#
def status(aCTX, aArgs):
 """Function docstring for leases TBD

 Args:
  - binding (optional). default "active"

 Output:
 """
 from ipaddress import ip_address
 result = []
 lease  = {}
 with open(aCTX.config['services']['iscdhcp']['active'],'r') as leasefile:
  for line in leasefile:
   if line == '\n':
    continue
   parts = line.split()
   if   parts[0] == 'lease' and parts[2] == '{':
    lease['ip'] = parts[1]
   elif parts[0] == '}':
    if aArgs.get('binding','active') == lease['binding']:
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
  result.sort(key=lambda d: int(ip_address(d['ip'])))
 return {'status':'OK','data':result }

#
#
def sync(aCTX, aArgs):
 """Function docstring for sync:  reload the DHCP server to use updated info

 Args:
  - id (required). Server id on master node (to match entries belonging to this instance)

 Output:
 """
 entries = aCTX.node_function('master','ipam','server_macs')(aArgs = {'server_id':aArgs['id'],'alternatives':True})
 __write_file(aCTX.config['services']['iscdhcp']['static'],entries['data'])
 # INTERNAL from rims.api.iscdhcp import restart
 return restart(aCTX, None)

#
#
def update(aCTX, aArgs):
 """Function docstring for check: update specific entry

 Args:
  - id (optional)
  - mac (optional required)
  - ip (optional required)
  - network (optional required)

 Output:
 """
 devices = {}

 with open(aCTX.config['services']['iscdhcp']['static'],'r') as config_file:
  for line in config_file:
   if line[0] == '#':
    continue
   parts = line.split()
   id = int(parts[1])
   devices[id] = {'id':id,'mac':parts[5][:-1],'ip':parts[7][:-1],'network':parts[11]}
 if 'id' in aArgs:
  devices[aArgs['id']] = {'id':aArgs['id'],'mac':aArgs['mac'],'ip':aArgs['ip'],'network':aArgs['network']}
  __write_file(aCTX.config['services']['iscdhcp']['static'],devices.values())
  # INTERNAL from rims.api.iscdhcp import restart
  ret = restart(aCTX,None)
 else:
  ret = {'status':'OK','devices':devices}
 return ret

#
#
def restart(aCTX, aArgs):
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
  ret['output'] = check_output(aCTX.config['services']['iscdhcp']['reload'].split()).decode()
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output.decode()
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('iscdhcp',{})
 params = ['reload','active','static']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

