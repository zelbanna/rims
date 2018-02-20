"""Module docstring.

 Appformix API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

#
def alarm(aDict):
 """Function docstring for alarm TBD

 Args:

 Extra:
 """
 from ..core.logger import log
 log("appformix_alarm({})".format(str(aDict)))
 return { 'result':'OK', 'info':'got alarm', 'data':'waiting to find out what to do with it :-)'}

#
#
def authenticate(aDict):
 from ..devices.appformix import Device
 from .. import SettingsContainer as SC
 controller = Device(aDict['host'])
 ret = controller.auth({'username':SC.appformix['username'], 'password':SC.appformix['password'] })
 return ret
