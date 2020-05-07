"""PowerDNS Recursor API module. Provides powerdns specific REST interface for recursor functions.

Settings:
- url - API url
- key - API key
- reload - command line command to reload service

"""
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
 try: servers = aCTX.rest_call('%s/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
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
    try: aCTX.rest_call('%s/servers/localhost/zones'%(settings['url']), aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = {'id':dom['foreign_id'], 'name':dom['name'] + '.', 'type':'Zone', 'servers':[dom['endpoint']], 'kind':'Forwarded', 'url':dom['name'], 'recursion_desired':False })
    except: pass
    else: ret['added'].append(dom)
  for f in forwarders:
   if not f.get('sync'):
    try: aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],f['id']), aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']})
    except: pass
    else: ret['removed'].append(f)
 return ret

#
# TODO: retrive statistics as well
def status(aCTX, aArgs):
 """Function returns recursor status - the number of forwarding zones

 Args:
  - count (optional)

 Output:
  - status
 """
 ret = {}
 settings = aCTX.config['powerdns']['recursor']
 try: servers = aCTX.rest_call('%s/servers/localhost/zones'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e.args[0]['data'])
 else:
  ret['status'] = 'OK'
  ret['zones'] = [x for x in servers if x['servers']]
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
