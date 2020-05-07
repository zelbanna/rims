"""PowerDNS API module. Provides powerdns specific REST interface. Essentially to create a GUI management for PowerDNS.

Settings:
- url - API url
- key - API key
- nameserver - For SOA records, add trailing . (dot) to be 'canonical'
- reload - command line command to reload service
- endpoint (ip:port for DNS service, not REST API)

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DNS"

from rims.core.common import DB

#################################### Domains #######################################
#
#
def domain_list(aCTX, aArgs):
 """Function provides a list of all domains from PowerDNS server

 Args:

 Output:
 """
 ret = {}
 settings = aCTX.config['powerdns']['server']
 try: ret['data'] = aCTX.rest_call('%s/servers/localhost/zones?dnssec=false'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = e.args[0]['data'] if e.args[0]['data'] else str(e)
 else:
  ret['status'] = 'OK'
  # Remove trailing dot, automaticall add below
  for dom in ret['data']:
   dom['name'] = dom['name'][:-1]
 ret['endpoint'] = settings.get('endpoint','127.0.0.1:53')
 return ret

#
def domain_info(aCTX, aArgs):
 """Function create/update domain info

 Args:
  - type (required)
  - master (required)
  - id (required)
  - name (required)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 output = {}
 settings = aCTX.config['powerdns']['server']
 if op == 'update' and id == 'new':
  args = {'name':aArgs['name'] if aArgs['name'][-1] == '.' else aArgs['name'] + '.','kind':aArgs.get('type','Master').lower().capitalize(),'dnssec':False,'soa-edit':'INCEPTION-INCREMENT','masters':aArgs.get('master','127.0.0.1').split(','),'nameservers':settings.get('nameservers','server.local.').split(',')}
  # Fix name so that it ends with .
  try: output = aCTX.rest_call('%s/servers/localhost/zones?rrsets=false'%(settings['url']), aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
  except Exception as e:
   ret = {'status':'NOT_OK','insert':False,'found':False,'info':e.args[0]['data']['error'] if e.args[0]['data'] else str(e)}
  else:
   ret = {'status':'OK','insert':True,'found':True}
 else:
  if op == 'update':
   args = {}
   if 'type' in aArgs:
    args['kind'] = aArgs['type'].lower().capitalize()
   if 'master' in aArgs:
    args['masters'] = aArgs['master'].split(',')
   try: res = aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],id), aMethod = 'PUT', aHeader = {'X-API-Key':settings['key']}, aArgs = args, aDataOnly = False)
   except Exception as e:
    ret = {'status':'NOT_OK','update':False,'info':e.args[0]['data']['error'] if e.args[0]['data'] else str(e)}
   else:
    ret = {'status':'OK','update':True}
  try: output = aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],id), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
  except Exception as e: ret['found'] = False
  else: ret['found'] = True
 # Convert to suitable data format
 ret['data'] = {'id':output.get('id','new'),'name':output.get('name','.')[:-1], 'type':output.get('kind',""),'master':','.join(output.get('masters',[])),'serial':output.get('serial',0)}
 ret['endpoint'] = settings.get('endpoint','127.0.0.1:53')
 return ret

#
#
def domain_delete(aCTX, aArgs):
 """Function deletes a zone - assumes PowerDNS removes all metadata and RRs

 Args:
  - id (required)

 Output:
 """
 ret = {}
 settings = aCTX.config['powerdns']['server']
 try: res = aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],aArgs['id']), aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']}, aDataOnly=False)
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['code'] = e.args[0]['code']
  ret['info'] = e.args[0]['data']
 else:
  ret['status'] = 'OK' if res['code'] == 204 else 'NOT_OK'
 ret['deleted'] = (ret['status'] == 'OK')
 return ret

#################################### Records #######################################
#
#
def record_list(aCTX, aArgs):
 """Function docstring for records TBD

 Args:
  - type (optional)
  - domain_id (optional)

 Output:
 """
 settings = aCTX.config['powerdns']['server']
 try: output = aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret = {'status':'NOT_OK','info':e.args[0]['data']}
 else:
  data = []
  for rrset in output['rrsets']:
   # Remove trailing dot, add below
   data.extend({'name':rrset['name'][:-1],'type':rrset['type'],'ttl':rrset['ttl'],'change_data':output['edited_serial'],'content':rec['content']} for rec in rrset['records'])
  ret = {'status':'OK','data':data,'count':len(data)}
 return ret

#
#
def record_info(aCTX, aArgs):
 """Function docstring for record_info TBD

 Args:
  - domain_id (required)
  - name (required)
  - type (required)
  - op (optional) 'new'/'info'/'insert'/'update'
  - content (optional)
  - ttl (optional)

 Output:
 """
 op = aArgs.pop('op',None)
 settings = aCTX.config['powerdns']['server']
 if op == 'new':
  ret = { 'status':'OK','data':{ 'domain_id':aArgs['domain_id'],'name':'key','content':'value','type':'type-of-record','ttl':'3600' }}
 elif op == 'info':
  try: output = aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
  except Exception as e: ret = {'status':'NOT_OK','info':e.args[0]['data']}
  else:
   for rrset in output['rrsets']:
    if rrset['name'] == aArgs['name'] and rrset['type'] == aArgs['type']:
     ret = {'status':'OK', 'data':{ 'domain_id':aArgs['domain_id'],'name':aArgs['name'],'content':rrset['records'][0],'type':aArgs['type'],'ttl':rrset['ttl']}}
     break
    else:
     ret = {'status':'NOT_OK','data':None}
 else:
  # update and insert is the same :-)
  aArgs.update({'ttl':aArgs.get('ttl','3600'),'type':aArgs['type'].upper()})
  args = {'rrsets':[{'name':aArgs['name'] if aArgs['name'][-1] == '.' else aArgs['name'] + '.','type':aArgs['type'],'ttl':aArgs['ttl'],'changetype':'REPLACE','records':[{'content':aArgs['content'],'disabled':False}],'comments':[]}]}
  try: aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'PATCH', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
  except Exception as e: ret = {'status':'NOT_OK','info':e.args[0]['data']}
  else: ret = {'status':'OK'}
  ret['data'] = aArgs
 return ret

#
#
def record_delete(aCTX, aArgs):
 """ Function deletes records info per type

 Args:
  - domain_id (required)
  - namne (required)
  - type (required)

 Output:
  - deleted
  - status
 """
 settings = aCTX.config['powerdns']['server']
 args = {'rrsets':[{'name':aArgs['name'] if aArgs['name'][-1] == '.' else aArgs['name'] + '.','type':aArgs['type'],'changetype':'DELETE','records':[],'comments':[]}]}
 try: aCTX.rest_call('%s/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'PATCH', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
 except Exception as e: ret = {'deleted':False,'status':'NOT_OK','info':e.args[0]['data']}
 else: ret = {'deleted':True,'status':'OK'}
 return ret

############################### Tools #################################
#
#
def sync(aCTX, aArgs):
 """Function docstring for sync.

 Args:

 Output:
 """
 return {'status':'OK'}

#
# TODO: statistics
def status(aCTX, aArgs):
 """Function docstring for return various status elements

 Args:
  - count (optional)

 Output:
 """
 def GL_get_host_name(aIP):
  from socket import gethostbyaddr
  try:    return gethostbyaddr(aIP)[0].partition('.')[0]
  except: return None

 ret = {'top':[],'who':[],'status':'OK'}
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
 settings = aCTX.config['powerdns']
 try:
  ret['output'] = check_output(settings.get('reload','service pdns restart').split()).decode()
  ret['code'] = 0
  ret['output'] = 'OK'
 except CalledProcessError as c:
  ret['code'] = c.returncode
  ret['output'] = c.output
  ret['status'] = 'NOT_OK'
 return ret
