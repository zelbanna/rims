"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

import sdcp.core.GenLib as GL

#
# lookup_info(id)
#
#
def alarm(aDict): 
 GL.log_msg("appformix_alarm: [{}]".format(str(aDict)))
 return { 'res':'got alarm', 'data':aDict}
