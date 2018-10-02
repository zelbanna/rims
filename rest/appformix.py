"""Appformix API module. Provides calls for appformix interaction"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.devices.appformix import Device

#
def alarm(aDict, aCTX):
 """Function docstring for alarm TBD

 Args:

 Output:
 """
 from zdcp.core.common import log
 log("appformix_alarm({})".format(str(aDict)))
 return { 'result':'OK', 'info':'got alarm', 'data':'waiting to find out what to do with it :-)'}

#
#
def authenticate(aDict, aCTX):
 """Function docstring for authenticate TBD

 Args:
  - host (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.settings['nodes'][aDict['node']])
 try:
  res = controller.auth({'username':aCTX.settings['appformix']['username'], 'password':aCTX.settings['appformix']['password'] })
  ret['auth'] = res['auth']
  ret['token'] = controller.get_token()
  ret['expires'] = controller.get_cookie_expire()
 except Exception as e: ret = e[0]
 return ret

#
#
def report_projects(aDict, aCTX):
 """Function docstring for report_projects TBD

 Args:
  - node (required)
  - token (required)
  - project (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.settings['nodes'][aDict['node']],aDict['token'])
 reports = controller.call('reports/project/metadata')['data']['Metadata']
 ret['reports'] = [rep for rep in reports if rep['ProjectId'] == aDict['project']]
 return ret

#
#
def project_reports(aDict, aCTX):
 """Function docstring for project_reports TBD

 Args:
  - report (required)
  - node (required)
  - token (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.settings['nodes'][aDict['node']],aDict['token'])
 ret = controller.call("reports/project/%(report)s"%aDict)['data']['UsageReport']
 return ret
