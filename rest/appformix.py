"""Module docstring.

 Appformix restAPI module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
def alarm(aDict):
 from sdcp import PackageContainer as PC
 PC.log_msg("appformix_alarm({})".format(str(aDict)))
 return { 'res':'OK', 'info':got alarm', 'data':'waiting to find out what to do with it :-)'}
