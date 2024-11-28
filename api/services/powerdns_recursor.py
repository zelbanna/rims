"""PowerDNS Recursor API module. Provides powerdns specific REST interface for recursor functions."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "RECURSOR"

############################### Tools #################################
#
#
def sync(aRT, aArgs):
 """Function docstring for sync. Sync domain caching with recursor forwarder

 Args:
  - domains (optional)

 Output:
 """
 ret = {'added':[],'removed':[]}
 settings = aRT.config['services']['powerdns']['recursor']
 try: servers = aRT.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  forwarders = [x for x in servers if x['servers']]
  domains = aRT.node_function('master','dns','domain_forwarders')(aArgs = {})['data'] if not aArgs.get('domains') else aArgs['domains']
  for dom in domains:
   for f in forwarders:
    if f['name'] == (dom['name'] + '.'):
     f['sync'] = dom['sync'] = True
     break
   else:
    try: aRT.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = {'id':dom['foreign_id'], 'name':dom['name'] + '.', 'type':'Zone', 'servers':[dom['endpoint']], 'kind':'Forwarded', 'url':dom['name'], 'recursion_desired':False })
    except Exception as e:
     aRT.log("PowerDNS Recursor sync (add): Error => %s"%e)
     ret['status'] = 'NOT_OK'
     ret['info'] = str(e)
    else: ret['added'].append(dom)
  for f in forwarders:
   if not f.get('sync'):
    try: aRT.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],f['id']), aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']})
    except Exception as e:
     aRT.log("PowerDNS Recursor sync (rem): Error => %s"%e)
     ret['status'] = 'NOT_OK'
     ret['info'] = str(e)
    else: ret['removed'].append(f)
 return ret

#
#
def status(aRT, aArgs):
 """Function returns recursor status - the number of forwarding zones

 Args:
  - count (optional)

 Output:
  - status
 """
 ret = {}
 settings = aRT.config['services']['powerdns']['recursor']
 try: servers = aRT.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e: ret.update({'status':'NOT_OK','info':str(e)})
 else: ret.update({'status':'OK','zones':[x for x in servers if x['servers']]})
 return ret

def statistics(aRT, aArgs):
 """Function returns recursor statistics

 Args:

 Output:
  - queries
  - remotes
 """
 ret = {}
 settings = aRT.config['services']['powerdns']['recursor']
 try: entries = aRT.rest_call('%s/jsonstat?command=get-query-ring&name=queries'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})['entries']
 except Exception as e: ret.update({'queries':[],'exception':str(e)})
 else: ret['queries'] = entries

 try: entries = aRT.rest_call('%s/jsonstat?command=get-remote-ring&name=remotes'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})['entries']
 except Exception as e: ret.update({'remotes':[], 'exception':str(e)})
 else: ret['remotes'] = entries
 return ret

#
#
def restart(aRT, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return { 'output':'N/A', 'code':0, 'status':'OK' }

#
#
def parameters(aRT, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Settings:
 - url - API url (http:/x.y.z.a:<port>)
 - key - API key
 - reload - command line command to reload service

 Args:

 Output:
  - status
  - parameters
 """
 settings = aRT.config['services'].get('powerdns',{}).get('recursor',{})
 params = ['url','key']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aRT, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aRT, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def close(aRT, aArgs):
 """ Function provides closing behavior, wrapping up data and file handlers before closing

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}
