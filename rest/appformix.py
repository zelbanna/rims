"""Appformix API module. Provides calls for appformix interaction"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..devices.appformix import Device

#
def alarm(aDict):
 """Function docstring for alarm TBD

 Args:

 Output:
 """
 from ..core.logger import log
 log("appformix_alarm({})".format(str(aDict)))
 return { 'result':'OK', 'info':'got alarm', 'data':'waiting to find out what to do with it :-)'}

#
#
def authenticate(aDict):
 """Function docstring for authenticate TBD

 Args:
  - host (required)

 Output:
 """
 from .. import SettingsContainer as SC
 ret = {}
 controller = Device(aDict['host'])
 ret['auth'] = controller.auth({'username':SC.appformix['username'], 'password':SC.appformix['password'] })['auth']
 ret['token'] = controller.get_token()
 ret['expires'] = controller.get_cookie_expire()
 return ret

#
#
def report_projects(aDict):
 """Function docstring for report_projects TBD

 Args:
  - host (required)
  - token (required)
  - project (required)

 Output:
 """
 ret = {}
 controller = Device(aDict['host'],aDict['token'])
 reports = controller.call('reports/project/metadata')['data']['Metadata']
 ret['reports'] = [rep for rep in reports if rep['ProjectId'] == aDict['project']]
 return ret

#
#
def project_reports(aDict):
 """Function docstring for project_reports TBD

 Args:
  - report (required)
  - host (required)
  - token (required)

 Output:
 """
 ret = {}
 controller = Device(aDict['host'],aDict['token'])
 ret = controller.call("reports/project/%s"%aDict['report'])['data']['UsageReport']
 return ret
