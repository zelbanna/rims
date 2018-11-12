"""SLACK API module. Provides a serviceinterface towards SLACK REST API (webhooks), i.e. SaaN (Slack As A Node)
Settings under section 'slack':
- api (base API - typically: https://hooks.slack.com/services)
- service (Access info - Like T000xxxxx/B000xxxx/abcdy and so on)

https://api.slack.com/incoming-webhooks

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "NOTIFY"

#
#
def status(aCTX, aDict):
 """Function returns status of slack connection... somehow (TBD)

 Args:

 Output:
 """
 return {'settings':aCTX.settings.get('slack',{})}

#
#
def sync(aCTX, aDict):
 """Function synchornizes connection to Slack, TBD as is..

 Args:
  - id (required). Server id on master node

 Output:
 """
 return None

#
#
def restart(aCTX, aDict):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'code':None, 'output':None, 'status':'OK'}

#
#
def notify(aCTX, aDict):
 """Function provides notification service, basic at the moment for development purposes

 Args:
  - message (required)
  - user (optional)
  - channel (optional)

 Output:
  - result ('OK'/'NOT_OK')
  - info (slack response text/data)

 """
 url = "%s/%s"%(aCTX.nodes[aCTX.settings['slack']['node']]['url'],aCTX.settings['slack']['service'])
 args = {'text':aDict['message']} 
 if aDict.get('user'):
  args['channel'] = "@%s"%aDict['user']
 elif aDict.get('channel'):
  args['channel'] = "#%s"%aDict['channel']
 elif aCTX.settings['slack'].get('channel'):
  args['channel'] = aCTX.settings['slack'].get('channel')
 res = aCTX.rest_call(url,aArgs = args)
 return {'status':'OK' if res['code']== 200 else 'NOT_OK', 'info':res['data']}
