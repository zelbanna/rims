"""Module docstring.

Vera API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"


from ..devices.vera import Device

#
#
def rest(aDict):
 """Function docstring for rest TBD

 Args:
  - host (required)
  - api (required)
  - method (required)
  - args (required)

 Extra:
 """
 try:
  controller = Device(aDict['host'])
  ret = controller.call(3480,aDict['api'],aDict['args'],aDict['method'])
 except Exception,e:
  ret = e[0] 
 return ret

#
#
def status(aDict):
 """Function docstring for status TBD

 Args:
  - host (required)

 Extra:
 """
 try:
  controller = Device(aDict['host'])
  ret = controller.call(3480,"id=sdata")['data']
 except Exception,e:
  ret = e[0] 
 return ret

#
#
def infra(aDict):
 """Function docstring for infra TBD

 Args:
  - host (required)

 Extra:
 """
 try:
  ret = {}
  controller = Device(aDict['host'])
  info = controller.call(3480,"id=sdata")['data']
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
  - host (required)
  - scene (required)
  - op (optional) - 'run'/'off'
  - status (optional)

 Extra:
 """                
 try:      
  ret = {}
  controller = Device(aDict['host'])
  if aDict.get('op'):
   ret['op'] = "RunScene" if aDict.get('op')== "run" else "SceneOff"
   res = controller.call(3480,"id=action&serviceId=urn:micasaverde-com:serviceId:HomeAutomationGateway1&action=%s&SceneNum=%s"%(ret['op'],aDict['scene']))
   ret['info'] = "OK" if (res['code'] == 200) else "FAILED"
  elif aDict.get('status'):
   scenes = controller.call(3480,"id=sdata")['data']['scenes']
   for scene in scenes:
    if scene['id'] == aDict['scene']:
     ret['info']= scene
     break
  else:
   ret = controller.call(3480,"id=scene&action=list&scene=%s"%aDict['scene'])['data']
 except Exception,e:
  ret = e[0]         
 return ret     



#
#
def devices(aDict):
 """Function docstring for devices TBD

 Args:
  - host (required)

 Extra:
 """
 try:
  ret = {}
  controller = Device(aDict['host'])
  info = controller.call(3480,"id=sdata")['data']
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
  - host (required)
  - device (required)

 Extra:
 """
 try:
  controller = Device(aDict['host'])
  ret = controller.call(3480,"id=status&DeviceNum=%s"%aDict['device'])['data']['Device_Num_%s'%aDict['device']]
 except Exception,e:
  ret = e[0] 
 return ret
