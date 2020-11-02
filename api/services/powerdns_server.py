"""PowerDNS API module. Provides powerdns specific REST interface. Essentially to create a GUI management"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "NAMESERVER"

#################################### Domains #######################################
#
#
def domain_list(aCTX, aArgs):
 """Function provides a list of all domains from this server

 Args:

 Output:
 """
 ret = {}
 settings = aCTX.config['powerdns']['server']
 try:
  ret['data'] = aCTX.rest_call(f"{settings['url']}/api/v1/servers/localhost/zones?dnssec=false", aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(e)
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
  try: output = aCTX.rest_call(f"{settings['url']}/api/v1/servers/localhost/zones?rrsets=false", aMethod = 'POST', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
  except Exception as e:
   ret = {'status':'NOT_OK','insert':False,'found':False,'info':str(e)}
  else:
   ret = {'status':'OK','insert':True,'found':True}
 else:
  if op == 'update':
   args = {}
   if 'type' in aArgs:
    args['kind'] = aArgs['type'].lower().capitalize()
   if 'master' in aArgs:
    args['masters'] = aArgs['master'].split(',')
   try:
    aCTX.rest_call(f"{settings['url']}/api/v1/servers/localhost/zones/{id}", aMethod = 'PUT', aHeader = {'X-API-Key':settings['key']}, aArgs = args, aDataOnly = False)
   except Exception as e:
    ret = {'status':'NOT_OK','update':False,'info':str(e)}
   else:
    ret = {'status':'OK','update':True}
  try:
   output = aCTX.rest_call(f"{settings['url']}/api/v1/servers/localhost/zones/{id}", aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
  except:
   ret['found'] = False
  else:
   ret['found'] = True
 # Convert to suitable data format
 ret['data'] = {'id':output.get('id','new'),'name':output.get('name','.')[:-1], 'type':output.get('kind',""),'master':','.join(output.get('masters',[])),'serial':output.get('serial',0)}
 ret['endpoint'] = settings.get('endpoint','127.0.0.1:53')
 return ret

#
#
def domain_delete(aCTX, aArgs):
 """Function deletes a zone - assumes all metadata and RRs is automatically removed

 Args:
  - id (required)

 Output:
 """
 ret = {}
 settings = aCTX.config['powerdns']['server']
 try: res = aCTX.rest_call(f"{settings['url']}/api/v1/servers/localhost/zones/{aArgs['id']}", aMethod = 'DELETE', aHeader = {'X-API-Key':settings['key']}, aDataOnly=False)
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['code'] = 0
  ret['info'] = str(e)
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
  - domain_id (required)
  - type (optional)

 Output:
 """
 settings = aCTX.config['powerdns']['server']
 try: output = aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 else:
  data = []
  for rrset in output['rrsets']:
   # Remove trailing dot, add below
   data.extend({'name':rrset['name'][:-1],'type':rrset['type'],'ttl':rrset['ttl'],'serial':output.get('edited_serial',0),'content':rec['content']} for rec in rrset['records'])
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
  try:
   output = aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
  except Exception as e:
   ret = {'status':'NOT_OK','info':str(e)}
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
  # PTR should end with .
  if aArgs['type'] == 'PTR' and aArgs['content'][-1] != '.':
   aArgs['content'] = aArgs['content'] + '.'

  args = {'rrsets':[{'name':aArgs['name'] if aArgs['name'][-1] == '.' else aArgs['name'] + '.','type':aArgs['type'],'ttl':aArgs['ttl'],'changetype':'REPLACE','records':[{'content':aArgs['content'],'disabled':False}],'comments':[]}]}
  try: aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'PATCH', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
  except Exception as e: ret = {'status':'NOT_OK','info':str(e)}
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
 try: aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],aArgs['domain_id']), aMethod = 'PATCH', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
 except Exception as e: ret = {'deleted':False,'status':'NOT_OK','info':str(e)}
 else: ret = {'deleted':True,'status':'OK'}
 return ret

############################### Tools #################################
#
#
def sync(aCTX, aArgs):
 """Function docstring for sync.

 Args:
  - id (required)

 Output:
 """
 settings = aCTX.config['powerdns']['server']
 try: domains = [x['name'] for x in aCTX.rest_call('%s/api/v1/servers/localhost/zones?dnssec=false'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})]
 except Exception as e: ret = {'status':'NOT_OK','info':str(e)}
 else:
  sync_data = aCTX.node_function('master','dns','sync_data')
  ret = {'status':'OK','records':0}
  for dom in domains:
   records = sync_data(aArgs = {'server_id':aArgs['id'],'foreign_id':dom})['data']
   args = {'rrsets':[{'name':x['name'] if x['name'][-1] == '.' else x['name'] + '.','type':x['type'],'ttl':'3600','changetype':'REPLACE','records':[{'content':x['content'],'disabled':False}],'comments':[]} for x in records]}
   try:
    aCTX.rest_call('%s/api/v1/servers/localhost/zones/%s'%(settings['url'],dom), aMethod = 'PATCH', aHeader = {'X-API-Key':settings['key']}, aArgs = args)
   except Exception as e:
    ret.update({'status':'NOT_OK',dom:str(e)})
   else:
    ret['records'] += len(records)
 return ret

#
#
def status(aCTX, aArgs):
 """Function docstring for return various status elements

 Args:

 Output:
 """
 settings = aCTX.config['powerdns']['server']
 try: output = aCTX.rest_call('%s/api/v1/servers/localhost'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e: ret = {'status':'NOT_OK','info':str(e)}
 else: ret = {'status':'OK','server':output}
 return ret

#
#
def statistics(aCTX, aArgs):
 """Function docstring for return various status elements

 Args:

 Output:
 """
 settings = aCTX.config['powerdns']['server']
 try: output = aCTX.rest_call('%s/api/v1/servers/localhost/statistics?includerings=false'%(settings['url']), aMethod = 'GET', aHeader = {'X-API-Key':settings['key']})
 except Exception as e: ret = {'status':'NOT_OK','info':str(e)}
 else: ret = {'status':'OK','statistics':{x['name']:x['type'] for x in output}}
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
 try: ret = {'output':check_output(settings.get('reload','service pdns restart').split()).decode(), 'code':0, 'status':'OK' }
 except CalledProcessError as c: ret = {'output':c.output, 'code':c.returncode, 'status':'NOT_OK'}
 return ret

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Settings:
 - url - API url (http:/x.y.z.a:<port>)
 - key - API key
 - reload - command line command to reload service
 - nameserver - For SOA records, add trailing . (dot) to be 'canonical'
 - endpoint (ip:port for nameserver, not REST API)

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config.get('powerdns',{}).get('server',{})
 params = ['url','key','reload','nameserver','endpoint']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

