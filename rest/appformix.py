"""Module docstring.

 Appformix restAPI module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"


#
# lookup_info(id)
#
#
def alarm(aDict):
 from sdcp import PackageContainer as PC
 PC.log_msg("appformix_alarm: [{}]".format(str(aDict)))
 return { 'res':'got alarm', 'data':'waiting to find out what to do with it :-)'}
