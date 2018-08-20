"""Vera API module. Provides nested REST management for a VERA z-wave controller through a node"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import rest_call
from zdcp.SettingsContainer import SC

#
#
def status(aDict):
 """Function docstring for status TBD

 Args:
  - node (required)

 Output:
 """
 try:
  node = SC['nodes'][aDict['node']]
  ret = rest_call("%s?id=sdata"%node)['data']
 except Exception as e:
  ret = e[0] 
 return ret

#
#
def infra(aDict):
 """Function docstring for infra TBD

 Args:
  - node (required)

 Output:
 """
 try:
  ret = {}
  node = SC['nodes'][aDict['node']]
  info = rest_call("%s?id=sdata"%node)['data']
  ret['sections'] = { d['id']: d['name'] for d in info['sections'] }
  ret['rooms']    = { d['id']: d for d in info['rooms'] }
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['scenes']   = { d['id']: d for d in info['scenes'] }
 except Exception as e:
  ret = e[0]         
 return ret        

#
#
def scene(aDict):
 """Function docstring for scene TBD

 Args:
  - node (required)
  - scene (required)
  - op (optional) - 'run'/'off'
  - status (optional)

 Output:
 """                
 try:      
  ret = {}
  node = SC['nodes'][aDict['node']]
  if aDict.get('op'):
   ret['op'] = "RunScene" if aDict.get('op')== "run" else "SceneOff"
   res = rest_call("%s?id=action&serviceId=urn:micasaverde-com:serviceId:HomeAutomationGateway1&action=%s&SceneNum=%s"%(node,ret['op'],aDict['scene']))
   ret['info'] = "OK" if (res['code'] == 200) else "FAILED"
  elif aDict.get('status'):
   scenes = rest_call("%s?id=sdata"%node)['data']['scenes']
   for scene in scenes:
    if scene['id'] == aDict['scene']:
     ret['info']= scene
     break
  else:
   ret = rest_call("%s?id=scene&action=list&scene=%s"%(node,aDict['scene']))['data']
 except Exception as e:
  ret = e[0]         
 return ret     

#
#
def devices(aDict):
 """Function docstring for devices TBD

 Args:
  - node (required)
  - room (optional)

 Output:
 """
 try:
  ret = {}
  node = SC['nodes'][aDict['node']]
  info = rest_call("%s?id=sdata"%node)['data']
  ret['devices'] = info['devices'] if not aDict.get('room') else [ x for x in info['devices'] if x['room'] == int(aDict.get('room')) ]
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['rooms']   = { d['id']:d['name'] for d in info['rooms'] }
 except Exception as e:
  ret = e[0] 
 return ret

#
#
def device_info(aDict):      
 """Function docstring for device_info TBD

 Args:
  - node (required)
  - id (required)
  - op (optional)
  - category (optional)
  - service (optional)
  - variable (optional)
  - value (optional)

 Output:
 """
 ret = {'op':None}
 op = aDict.pop("op",None)
 try:
  node = SC['nodes'][aDict['node']]
  if op == 'update':
   ret['op'] = {}
   if aDict['category'] == '2' and aDict['service'] == 'urn:upnp-org:serviceId:Dimming1' and aDict['variable'] == 'LoadLevelTarget':
    ret['op']['response'] = rest_call("%s?id=action&output_format=json&DeviceNum=%s&serviceId=urn:upnp-org:serviceId:Dimming1&action=SetLoadLevelTarget&newLoadlevelTarget=%s"%(node,aDict['id'],aDict['value']))['data']
    response = ret['op']['response'].get('u:SetLoadLevelTargetResponse')
    if response:
     from time import sleep
     sleep(1)
     ret['op']['job'] = response.get('JobID')
     ret['op']['result'] = rest_call("%s?id=jobstatus&job=%s&plugin=zwave"%(node,response.get('JobID')))['data']
 
  res  = rest_call("%s?id=status&DeviceNum=%s"%(node,aDict['id']))['data']
  info = res['Device_Num_%s'%aDict['id']]['states']
  for x in info:
   try:
    service = x['service'].split(':')
    if service[1] <> 'micasaverde-com':
     entry = ret.get(x['service'],{})
     entry[x['variable']] = x['value']
     ret[x['service']] = entry
   except: pass
 except Exception as e:
  ret = e[0] 
 return ret
