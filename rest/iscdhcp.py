"""Module docstring.

ISC DHCP API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC

#
#
#
def get_leases(aDict):
 import sdcp.core.genlib as GL
 active = []
 free   = []
 lease  = {}
 with open(PC.dhcp['leasefile'],'r') as leasefile: 
  for line in leasefile:
   if line == '\n':
    continue
   parts = line.split()
   if   parts[0] == 'lease' and parts[2] == '{':
    lease['ip'] = parts[1]
   elif parts[0] == '}':
    if lease.pop('binding') == "active":
     active.append(lease)
    else:
     free.append(lease)
    lease = {}
   elif parts[0] == 'hardware' and parts[1] == 'ethernet':
    lease['mac'] = parts[2][:-1] 
   elif parts[0] == 'binding':
    lease['binding'] = parts[2][:-1] 
   elif parts[0] == 'starts' or parts[0] == 'ends':
    lease[parts[0]] = " ".join(parts[2:])[:-1]
   elif parts[0] == 'client-hostname':
    lease['hostname'] = parts[1][:-1]
  active.sort(key=lambda d: GL.ip2int(d['ip']))
  free.sort(  key=lambda d: GL.ip2int(d['ip']))
  return {"active":active, "free":free }                                

#
# Update function - reload the DHCP server to use new info
# - entries is a list of dict objects containing hostname, mac, ip etc
def update_server(aDict):
 entries = aDict['entries']
 # Create new file
 with open(PC.dhcp['file'],'w') as leasefile:
  for entry in entries:
   leasefile.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Subnet {3}, Id: {4}\n".format(entry['fqdn'],entry['mac'],entry['ip'],entry['subnet_id'],entry['id'])) 

 # Reload
 from subprocess import check_output, CalledProcessError
 commands = PC.dhcp['reload'].split()
 result = {}
 try:
  status = check_output(commands)
  result['res'] = "OK"
  result['output'] = status
 except CalledProcessError, c:
  result['res'] = "Error"
  result['code'] = c.returncode
  result['output'] = c.output
 return result