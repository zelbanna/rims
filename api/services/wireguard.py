"""WireGuard Service API module. Implements wireguard operational command functionality"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "VPN"

from subprocess import check_output, CalledProcessError
from time import sleep

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
def status(aRT, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - status
 """
 ret = {}
 try:
  command = aRT.config['services']['wireguard']['status']
  output = check_output(command.split())
  ret['code'] = 0
 except CalledProcessError as c:
  output = c.output
  ret['code'] = c.returncode
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'

 if not (output):
  ret['state'] = 'INACTIVE'
 else:
  ret['state'] = 'ACTIVE'
  parts = output.decode().split()
  ret['extra'] = {'send':0,'received':0,'info':parts}
 return ret

#
#
def sync(aRT, aArgs):
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
def restart(aRT, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 ret = {}
 ret['stop'] = __op(aRT.config['services']['wireguard']['stop'])['status']
 sleep(2)
 ret.update(__op(aRT.config['services']['wireguard']['start']))
 return ret

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('wireguard',{})
 params = ['start','stop','status']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return __op(aRT.config['services']['wireguard']['start'])

#
#
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return __op(aRT.config['services']['wireguard']['stop'])

#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
