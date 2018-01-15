"""Module docstring.

 Appformix API module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
def alarm(aDict):
 from sdcp.core.logger import log
 log("appformix_alarm({})".format(str(aDict)))
 return { 'result':'OK', 'info':'got alarm', 'data':'waiting to find out what to do with it :-)'}
