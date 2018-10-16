"""SLACK API module. Provides a serviceinterface towards SLACK REST API (webhooks), i.e. SaaN (Slack As A Node)
Settings under section 'slack':
- service
- channel

"""
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__type__ = "NOTIFY"

#
#
def status(aDict, aCTX):
 """Function returns status of slack connection... somehow (TBD)

 Args:

 Output:
 """
 return None
#
#
def sync(aDict, aCTX):
 """Function synchornizes connection to Slack, TBD as is..

 Args:
  - id (required). Server id on master node

 Output:
 """
 return None
#
#
def restart(aDict, aCTX):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'code':None, 'output':None, 'result':'OK'}
