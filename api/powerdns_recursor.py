"""PowerDNS Recursor API module. Provides powerdns specific REST interface for recursor functions."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "RECURSOR"

############################### Tools #################################
#
#
def sync(aCTX, aArgs):
 """Function docstring for sync. Sync domain cache with recursor forwarder

 Args:
  - domains (optional)

 Output:
 """
 ret = {'added':[],'removed':[]}
 settings = aCTX.config['powerdns']['recursor']
 try: servers = aCTX.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e.args[0]['data'])
 else:
  ret['status'] = 'OK'
  forwarders = [x for x in servers if x['servers']]
  domains = aCTX.node_function('master','dns','domain_forwarders')(aArgs = {})['data'] if not aArgs.get('domains') else aArgs['domains']
  for dom in domains:
   for f in forwarders:
    if f['name'] == (dom['name'] + '.'):
     f['sync'] = dom['sync'] = True
     break
   else:
    try: aCTX.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = {'id':dom['foreign_id'], 'name':dom['name'] + '.', 'type':'Zone', 'servers':[dom['endpoint']], 'kind':'Forwarded', 'url':dom['name'], 'recursion_desired':False })
    except: pass
    else: ret['added'].append(dom)
  for f in forwarders:
   if not f.get('sync'):
    try: aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],f['id']), aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']})
    except: pass
    else: ret['removed'].append(f)
 return ret

#
#
def status(aCTX, aArgs):
 """Function returns recursor status - the number of forwarding zones

 Args:
  - count (optional)

 Output:
  - status
 """
 ret = {}
 settings = aCTX.config['powerdns']['recursor']
 try: servers = aCTX.rest_call('%s/api/v1/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e: ret.update({'status':'NOT_OK','info':str(e.args[0]['data'])})
 else: ret.update({'status':'OK','zones':[x for x in servers if x['servers']]})
 return ret

def statistics(aCTX, aArgs):
 """Function returns recursor statistics

 Args:

 Output:
  - queries
  - remotes
 """
 ret = {}
 settings = aCTX.config['powerdns']['recursor']
 try: entries = aCTX.rest_call('%s/jsonstat?command=get-query-ring&name=queries'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})['entries']
 except Exception as e: ret.update({'queries':[],'exception':str(e.args[0]['data'])})
 else: ret['queries'] = entries

 try: entries = aCTX.rest_call('%s/jsonstat?command=get-remote-ring&name=remotes'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})['entries']
 except Exception as e: ret.update({'remotes':[], 'exception':str(e.args[0]['data'])})
 else: ret['remotes'] = entries
 return ret

#
#
def restart(aCTX, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 from subprocess import check_output, CalledProcessError
 ret = {}
 settings = aCTX.config['powerdns']['recursor']
 try:
  ret['output'] = check_output(settings.get('reload','service pdns-recursor restart').split()).decode()
  ret['code'] = 0
  ret['output'] = 'OK'
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output.decode('utf-8')
  ret['status'] = 'NOT_OK'
 except Exception as e:
  ret['code'] = 5
  ret['output'] = str(e)
  ret['status'] = 'NOT_OK'
 return ret

#
#
def parameters(aCTX, aArgs):
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
 settings = aCTX.config.get('powerdns',{}).get('recursor',{})
 params = ['url','key','reload']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
