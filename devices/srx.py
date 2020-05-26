"""Juniper SRX Module"""
__author__  = "Zacharias El Banna"
__type__    = "network"
__icon__    = "viz-srx.png"
__oid__     = 2636

from rims.devices.junos import Junos

################################ SRX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self, aCTX, aID, aIP = None):
  Junos.__init__(self, aCTX, aID, aIP)

 #################################### Authentication ####################################
 #
 def auth_table(self):
  try: res = self._router.rpc.get_userfw_local_auth_table_all({'format':'json'})['user-identification'][0]['local-authentication-table'][0]
  except Exception as e:
   return {'status':'NOT_OK','info':str(e)}
  else:
   table = [{'ip':auth['ip-address'][0]['data'],'alias':auth['user-name'][0]['data'],'roles':auth['role-name-list'][0]['role-name'][0]['data'].split(', ')} for auth in res.get('local-authentication-info',[])]
   return {'status':'OK','data':table}

 def auth_add(self, aAlias, aIP, aRoles):
  try: res = self._router.rpc.request_userfw_local_auth_table_add(user_name=aAlias,ip_address=aIP,roles=','.join(aRoles))
  except Exception as e:
   return {'status':'NOT_OK','info':str(e)}
  else:
   return {'status':'OK' if res else 'NOT_OK'}

 def auth_delete(self, aAlias, aIP):
  try: res = self._router.rpc.request_userfw_local_auth_table_delete_ip(ip_address=aIP)
  except Exception as e:
   return {'status':'NOT_OK','info':str(e)}
  else:
   return {'status':'OK' if res else 'NOT_OK'}

