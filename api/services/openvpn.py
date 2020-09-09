"""OpenVPN Service API module. Implements openvpn command functionality"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "VPN"

from subprocess import check_output, CalledProcessError

#
#
def __op(aOP):
 ret = {}
 try:
  ret['result'] = check_output(aOP.split()).decode().strip()
 except CalledProcessError as c:
  ret['info'] = c.output.strip()
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
#
def status(aCTX, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - status
 """
 ret = {}
 try:
  command = aCTX.config['openvpn']['status']
  output = check_output(command.split())
  ret['code'] = 0
 except CalledProcessError as c:
  output = c.output
  ret['code'] = c.returncode
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'

 for line in output.decode().split('\n'):
  line = line.lstrip()
  if (line.lstrip())[0:7] == 'Active:':
   state = line[7:].split()
   ret['state'] = state[0]
   ret['extra'] = state[1][1:-1]
   break
 return ret

#
#
def sync(aCTX, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
 """
 return {'status':'OK','output':'No OP'}

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
 ret = {}
 from time import sleep as time_sleep
 ret['stop'] = __op(aCTX.config['openvpn']['stop'])['status']
 time_sleep(2)
 ret.update(__op(aCTX.config['openvpn']['start']))
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
 settings = aCTX.config.get('openvpn',{})
 params = ['start','stop','status']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return __op(aCTX.config['openvpn']['start'])

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return __op(aCTX.config['openvpn']['stop'])
