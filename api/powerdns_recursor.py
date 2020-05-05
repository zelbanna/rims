"""PowerDNS Recursor API module. Provides powerdns specific REST interface for recursor functions.
Settings:
- url
- key
- server-id

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "RECURSOR"

############################### Tools #################################
#
#
def sync(aCTX, aArgs = None):
 """Function docstring for sync. Sync domain cache with recursor forwarder

 Args:
  - domains (optional)

 Output:
 """
 ret = {'added':[],'removed':[]}
 settings = aCTX.config['powerdns']['recursor']
 try: servers = aCTX.rest_call('%s/servers/%s/zones'%(settings['url'],settings['server-id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  forwarders = [x for x in servers if x['servers']]
  domains = aCTX.node_function('master','dns','domain_forwarders')({})['data'] if not aArgs.get('domains') else aArgs['domains']
  for dom in domains:
   for f in forwarders:
    if f['name'] == (dom['name'] + '.'):
     f['sync'] = dom['sync'] = True
     break
   else:
    try: aCTX.rest_call('%s/servers/%s/zones'%(settings['url'],settings['server-id']), aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = {'id':dom['foreign_id'], 'name':dom['name'] + '.', 'type':'Zone', 'servers':[dom['endpoint']], 'kind':'Forwarded', 'url':dom['name'], 'recursion_desired':False })
    except: pass
    else: ret['added'].append(dom)
  for f in forwarders:
   if not f.get('sync'):
    try: aCTX.rest_call('%s/servers/%s/zones/%s'%(settings['url'],settings['server-id'],f['id']), aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']})
    except: pass
    else: ret['removed'].append(f)
 return ret

#
#
def status(aCTX, aArgs = None):
 """Function returns recursor status - the number of forwarding zones

 Args:
  - count (optional)

 Output:
  - status
 """
 ret = {}
 settings = aCTX.config['powerdns']['recursor']
 try: servers = aCTX.rest_call('%s/servers/%s/zones'%(settings['url'],settings['server-id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
 else:
  ret['status'] = 'OK'
  ret['data'] = [x for x in servers if x['servers']]
 return ret

#
#
def restart(aCTX, aArgs = None):
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
