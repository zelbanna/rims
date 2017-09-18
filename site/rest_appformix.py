"""Module docstring.

 Appformix restAPI module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"


#
# lookup_info(id)
#
#
def alarm(aDict):
 import sdcp.PackageContainer as PC
 PC.log_msg("appformix_alarm: [{}]".format(str(aDict)))
 return { 'res':'got alarm', 'data':'waiting to find out what to do with it :-)'}
