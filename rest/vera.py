"""Vera API module.

 Provides nested REST management for a VERA z-wave controller through a node. The node should be formatted like below:
 http(s)://x.y.z.w:abcd/data_request?

"""
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)


#
#
def status(aDict, aCTX):
 """Function docstring for status TBD

 Args:
  - node (required)

 Output:
 """
 try:
  node = aCTX.settings['nodes'][aDict['node']]
  ret  = aCTX.rest_call("%sid=sdata"%node)['data']
 except Exception as e:
  ret = e.args[0] 
 return ret

#
#
def infra(aDict, aCTX):
 """Function docstring TBD

 Args:
  - node (required)

 Output:
 """
 try:
  ret = {}
  node = aCTX.settings['nodes'][aDict['node']]
  info = aCTX.rest_call("%sid=sdata"%node)['data']
  ret['sections'] = { d['id']: d['name'] for d in info['sections'] }
  ret['rooms']    = { d['id']: d for d in info['rooms'] }
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['scenes']   = { d['id']: d for d in info['scenes'] }
 except Exception as e:
  ret = e.args[0]         
 return ret        

#
#
def scene(aDict, aCTX):
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
  node = aCTX.settings['nodes'][aDict['node']]
  if aDict.get('op'):
   ret['op'] = "RunScene" if aDict.get('op')== "run" else "SceneOff"
   res = aCTX.rest_call("%sid=action&serviceId=urn:micasaverde-com:serviceId:HomeAutomationGateway1&action=%s&SceneNum=%s"%(node,ret['op'],aDict['scene']))
   ret['info'] = "OK" if (res['code'] == 200) else "FAILED"
  elif aDict.get('status'):
   scenes = aCTX.rest_call("%sid=sdata"%node)['data']['scenes']
   for scene in scenes:
    if scene['id'] == aDict['scene']:
     ret['info']= scene
     break
  else:
   ret = aCTX.rest_call("%sid=scene&action=list&scene=%s"%(node,aDict['scene']))['data']
 except Exception as e:
  ret = e.args[0]
 return ret

#
#
def devices(aDict, aCTX):
 """Function docstring TBD

 Args:
  - node (required)
  - room (optional)

 Output:
 """
 try:
  ret = {}
  node = aCTX.settings['nodes'][aDict['node']]
  info = aCTX.rest_call("%sid=sdata"%node)['data']
  ret['devices'] = info['devices'] if not aDict.get('room') else [ x for x in info['devices'] if x['room'] == int(aDict.get('room')) ]
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['rooms']   = { d['id']:d['name'] for d in info['rooms'] }
 except Exception as e:
  ret = e.args[0] 
 return ret

#
#
def device_info(aDict, aCTX):
 """Function docstring TBD

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
  node = aCTX.settings['nodes'][aDict['node']]
  if op == 'update':
   ret['op'] = {}
   if aDict['category'] == '2' and aDict['service'] == 'urn:upnp-org:serviceId:Dimming1' and aDict['variable'] == 'LoadLevelTarget':
    ret['op']['response'] = aCTX.rest_call("%sid=action&output_format=json&DeviceNum=%s&serviceId=urn:upnp-org:serviceId:Dimming1&action=SetLoadLevelTarget&newLoadlevelTarget=%s"%(node,aDict['id'],aDict['value']))['data']
    response = ret['op']['response'].get('u:SetLoadLevelTargetResponse')
    if response:
     from time import sleep
     sleep(1)
     ret['op']['job'] = response.get('JobID')
     ret['op']['result'] = aCTX.rest_call("%sid=jobstatus&job=%s&plugin=zwave"%(node,response.get('JobID')))['data']
 
  res  = aCTX.rest_call("%sid=status&DeviceNum=%s"%(node,aDict['id']))['data']
  info = res['Device_Num_%s'%aDict['id']]['states']
  for x in info:
   try:
    service = x['service'].split(':')
    if service[1] != 'micasaverde-com':
     entry = ret.get(x['service'],{})
     entry[x['variable']] = x['value']
     ret[x['service']] = entry
   except: pass
 except Exception as e:
  ret = e.args[0] 
 return ret
