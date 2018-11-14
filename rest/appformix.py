"""Appformix API module. Provides calls for appformix interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.appformix import Device

#
def alarm(aCTX, aArgs = None):
 """Function docstring for alarm TBD

 Args:

 Output:
 """
 aCTX.log("appformix_alarm({})".format(str(aArgs)))
 return { 'status':'OK', 'info':'got alarm', 'data':'waiting to find out what to do with it :-)'}

#
#
def authenticate(aCTX, aArgs = None):
 """Function docstring for authenticate TBD

 Args:
  - host (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.nodes[aArgs['node']]['url'])
 try:
  res = controller.auth({'username':aCTX.settings['appformix']['username'], 'password':aCTX.settings['appformix']['password'] })
  ret['auth'] = res['auth']
  ret['token'] = controller.get_token()
  ret['expires'] = controller.get_cookie_expire()
 except Exception as e: ret = e[0]
 return ret

#
#
def report_projects(aCTX, aArgs = None):
 """Function docstring for report_projects TBD

 Args:
  - node (required)
  - token (required)
  - project (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.nodes[aArgs['node']]['url'],aArgs['token'])
 reports = controller.call('reports/project/metadata')['Metadata']
 ret['reports'] = [rep for rep in reports if rep['ProjectId'] == aArgs['project']]
 return ret

#
#
def project_reports(aCTX, aArgs = None):
 """Function docstring for project_reports TBD

 Args:
  - report (required)
  - node (required)
  - token (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.nodes[aArgs['node']]['url'],aArgs['token'])
 ret = controller.call("reports/project/%(report)s"%aArgs)['UsageReport']
 return ret
