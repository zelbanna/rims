"""Vera API module. Provides nested REST management for a VERA z-wave controller through a node"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import SC,rest_call
#
#
def node_to_ui(aDict):
 """Function docstring for node_to_ui TBD

 Args:
  - node (required)

 Output:
 """
 node = SC['node'][aDict.get('node','vera')]
 parts = node.partition('//')
 host = "%s//%s/cmh/"%(parts[0],(parts[2].split('/')[0]).split(':')[0])
 return {'ui':host }

#
#
def status(aDict):
 """Function docstring for status TBD

 Args:
  - node (required)

 Output:
 """
 try:
  node = SC['node'][aDict['node']]
  ret = rest_call("%s?id=sdata"%node)['data']
 except Exception,e:
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
  node = SC['node'][aDict['node']]
  info = rest_call("%s?id=sdata"%node)['data']
  ret['sections'] = { d['id']: d['name'] for d in info['sections'] }
  ret['rooms']    = { d['id']: d for d in info['rooms'] }
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['scenes']   = { d['id']: d for d in info['scenes'] }
 except Exception,e:
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
  node = SC['node'][aDict['node']]
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
 except Exception,e:
  ret = e[0]         
 return ret     



#
#
def devices(aDict):
 """Function docstring for devices TBD

 Args:
  - node (required)

 Output:
 """
 try:
  ret = {}
  node = SC['node'][aDict['node']]
  info = rest_call("%s?id=sdata"%node)['data']
  ret['devices'] = info['devices']
  ret['categories'] = { d['id']: d['name'] for d in info['categories'] }
  ret['rooms']   = { d['id']: d['name'] for d in info['rooms'] }
 except Exception,e:
  ret = e[0] 
 return ret

#
#
def device_info(aDict):      
 """Function docstring for device_info TBD

 Args:
  - node (required)
  - device (required)

 Output:
 """
 ret = {}
 try:
  node = SC['node'][aDict['node']]
  ret['states'] = rest_call("%s?id=status&DeviceNum=%s"%(node,aDict['device']))['data']['Device_Num_%s'%aDict['device']]['states']
 except Exception,e:
  ret = e[0] 
 return ret
