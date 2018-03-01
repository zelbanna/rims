"""Module docstring.

 Device API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - ip (optional)
  - id (optional)
  - info (optional)
  - op (optional)

 Extra:
 """
 ret = {'op':aDict.get('op')}
 search = "devices.id = '{}'".format(aDict.get('id')) if aDict.get('id') else "devices.ip = INET_ATON('{}')".format(aDict.get('ip'))
 if ret['op'] == 'lookup' and aDict.get('ip'):
  ret['result'] = detect({'ip':aDict.get('ip'),'update':True})

 with DB() as db:
  info = aDict.get('info',[])
  ret['xist'] = db.do("SELECT devices.*, base, devicetypes.name as type_name, functions, a.name as domain, INET_NTOA(ip) as ipasc, CONCAT(INET_NTOA(subnets.subnet),'/',subnets.mask) AS subnet, INET_NTOA(subnets.gateway) AS gateway FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN devicetypes ON devicetypes.id = devices.type_id LEFT JOIN subnets ON subnets.id = subnet_id WHERE {}".format(search))
  if ret['xist'] > 0:
   ret['info'] = db.get_row()
   if not ret['info']['functions']:
    ret['info']['functions'] = ""
   ret['id']   = ret['info'].pop('id',None)
   if 'basics' in info:
    ret['fqdn'] = "{}.{}".format(ret['info']['hostname'],ret['info']['domain'])
    ret['ip']   = ret['info'].pop('ipasc',None)
    ret['type'] = ret['info'].pop('base',None)
    ret['mac']  = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   if 'username' in info:
    from .. import SettingsContainer as SC
    ret['username'] = SC.netconf['username']
   if 'booking' in info:
    ret['booked'] = db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(ret['id']))
    if ret['booked'] > 0:
     ret['booking'] = db.get_row()
   if 'rackinfo' in info:
    if ret['info']['vm'] == 1:
     ret['racked'] = 0
    else:
     ret['racked'] = db.do("SELECT rackinfo.*, INET_NTOA(devices.ip) AS console_ip, devices.hostname AS console_name FROM rackinfo LEFT JOIN devices ON devices.id = rackinfo.console_id WHERE rackinfo.device_id = {}".format(ret['id']))
     if ret['racked'] > 0:
      ret['rack'] = db.get_row()
      ret['rack']['hostname'] = ret['info']['hostname']
 return ret

#
#
def basics(aDict):
 """Function docstring for basics TBD

 Args:
  - id (required)

 Extra:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT INET_NTOA(ip) as ip, hostname, domains.name AS domain FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = '%s'"%aDict['id'])
  ret.update(db.get_row())
 return ret

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - filter (optional)
  - sort (optional)
  - dict (optional)
  - rack (optional)

 Extra:
 """
 ret = {}
 if aDict.get('rack'):
  if aDict.get('rack') == 'vm':
   tune = "WHERE vm = 1"
  else:
   tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = '{}'".format(aDict.get('rack'))
  if aDict.get('filter'):
   tune += " AND type_id = {}".format(aDict.get('filter'))
 elif aDict.get('filter'):
  tune = "WHERE type_id = {}".format(aDict.get('filter'))
 else:
  tune = ""

 ret = {'sort':aDict.get('sort','devices.id')}
 with DB() as db:
  sql = "SELECT devices.id, devices.hostname, INET_NTOA(ip) as ipasc, hostname, domains.name as domain, CONCAT(devices.hostname,'.',domains.name) AS  fqdn, a_dom_id, a_id, ptr_id, model, type_id, subnets.gateway FROM devices JOIN subnets ON subnet_id = subnets.id JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,ret['sort'])
  ret['xist'] = db.do(sql)
  ret['data'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def list_type(aDict):
 """Function docstring for list_type TBD

 Args:
  - base (optional)
  - name (optional)

 Extra:
 """
 ret = {}
 with DB() as db:
  select = "devicetypes.%s ='%s'"%(('name',aDict.get('name')) if aDict.get('name') else ('base',aDict.get('base')))
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ip) AS ipasc, hostname, devicetypes.base as type_base, devicetypes.name as type_name FROM devices LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE %s ORDER BY type_name,hostname"%select)
  ret['data'] = db.get_rows()
 return ret

#
#
def list_mac(aDict):
 """Function docstring for list_mac TBD

 Args:

 Extra:
 """
 def GL_int2mac(aInt):
  return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()

 with DB() as db:
  db.do("SELECT devices.id, CONCAT(hostname,'.',domains.name) as fqdn, INET_NTOA(ip) as ip, mac, subnet_id FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT mac = 0 ORDER BY ip")
  rows = db.get_rows()
 for row in rows:
  row['mac'] = GL_int2mac(row['mac'])
 return rows

#
#
def update(aDict):
 """Function docstring for update TBD

 Args:
  - id (required)
  - rackinfo_<var>_pdu_slot' (conditionally optional)
  - rackinfo_<var>_pdu_id' (conditionally optional)
  - devices_mac (optional)
  - racked (optional)
  - rackinfo_rack_id (optional)

 Extra:
 """
 from ..core.logger import log
 log("device_update({})".format(aDict))
 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0
 id     = aDict['id']
 racked = aDict.get('racked')
 aDict.pop('id',None)
 aDict.pop('racked',None)
 try: aDict['devices_mac'] = GL_mac2int(aDict.pop('devices_mac','00:00:00:00:00:00'))
 except: pass

 ret    = {'data':{}}
 with DB() as db:

  if racked:
   if   racked == '1' and aDict.get('rackinfo_rack_id') == 'NULL':
    db.do("DELETE FROM rackinfo WHERE device_id = {}".format(id))
    aDict.pop('rackinfo_pem0_pdu_slot_id',None)
    aDict.pop('rackinfo_pem1_pdu_slot_id',None)
   elif racked == '0' and aDict.get('rackinfo_rack_id') != 'NULL':
    db.do("INSERT INTO rackinfo SET device_id = {},rack_id={} ON DUPLICATE KEY UPDATE rack_id = rack_id".format(id,aDict.get('rackinfo_rack_id')))
   elif racked == '1':
    for pem in ['pem0','pem1']:
     try:
      pem_pdu_slot_id = aDict.pop('rackinfo_%s_pdu_slot_id'%pem,None)
      (aDict['rackinfo_%s_pdu_id'%pem],aDict['rackinfo_%s_pdu_slot'%pem]) = pem_pdu_slot_id.split('.')
     except: pass

  tbl_id = { 'devices':'id', 'rackinfo':'device_id' }
  sql    = "UPDATE %s SET %s=%s WHERE %s = '%s'"
  for tkey in aDict.keys():
   (table, void, key) = tkey.partition('_')
   data = aDict[tkey]
   if db.do(sql%(table,key,"'%s'"%data if data != 'NULL' else "NULL",tbl_id[table],id)) > 0:
    ret['data'][key] = 'CHANGED'
 return ret

#
#
def update_pdu(aDict):
 """Function docstring for update_pdu TBD

 Args:
  - hostname (required)
  - pem<var>_pdu_slot (optional)
  - pem<var>_pdu_id (optional)
  - pem<var>_pdu_unit (optional)

 Extra:
 """
 ret = {}
 with DB() as db:
  for p in ['0','1']:
   ret[p] = None
   id = aDict.get('pem%s_pdu_id'%(p))
   if id:
    slot = int(aDict.get('pem%s_pdu_slot'%(p),0))
    unit = int(aDict.get('pem%s_pdu_unit'%(p),0))
    if not (slot == 0 or unit == 0):
     db.do("SELECT hostname, INET_NTOA(ip), devicetypes.name FROM devices LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = '{}'".format(id))
     data = db.get_row()
     args = {'ip':data['ip'],'unit':unit,'slot':slot,'text':aDict['hostname']+"-P%s"%(p)}
     # Redo with module import
     if data.name == 'avocent':
      from avocent import pdu_update
      ret["pem{}".format(p)] = pdu_update(args)
 return ret

#
#
def new(aDict):
 """Function docstring for new TBD

 Args:
  - a_dom_id (required)
  - hostname (required)
  - target (optional)
  - subnet_id (optional)
  - ip (optional)
  - vm (optional)
  - mac (optional)
  - arg (optional)

 Extra:
  - target is 'rack_id' or nothing
  - arg is rack_id
 """
 from ..core.logger import log
 log("device_new({})".format(aDict))
 def GL_ip2int(addr):
  from struct import unpack
  from socket import inet_aton
  return unpack("!I", inet_aton(addr))[0]
 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 ip    = aDict.get('ip')
 ipint = GL_ip2int(ip)
 subnet_id = aDict.get('subnet_id')
 ret = {'info':None}
 with DB() as db:
  in_sub = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(subnet_id,ipint))
  if in_sub == 0:
   ret['info'] = "IP not in subnet range"
  elif aDict['hostname'] == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   xist = db.do("SELECT id, hostname, INET_NTOA(ip) AS ipasc, a_dom_id FROM devices WHERE subnet_id = {} AND (ip = {} OR hostname = '{}')".format(subnet_id,ipint,aDict['hostname']))
   if xist == 0:
    mac = GL_mac2int(aDict.get('mac',0))
    ret['insert'] = db.do("INSERT INTO devices (ip,vm,mac,a_dom_id,subnet_id,hostname,snmp,model) VALUES({},{},{},{},{},'{}','unknown','unknown')".format(ipint,aDict.get('vm','0'),mac,aDict['a_dom_id'],subnet_id,aDict['hostname']))
    ret['id']   = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = {}, rack_id = {} ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1".format(ret['id'],aDict.get('arg')))
     ret['rack'] = aDict.get('arg')
     ret['info'] = "rack"
   else:
    ret['info']  = "existing"
    ret.update(db.get_row())
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Extra:
 """
 from ..core.logger import log
 log("device_remove({})".format(aDict))
 with DB() as db:
  xist = db.do("SELECT hostname, mac, a_id, ptr_id, devicetypes.* FROM devices LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = {}".format(aDict['id']))
  if xist == 0:
   ret = { 'deleted':0, 'dns':{'a':0, 'ptr':0}}
  else:
   data = db.get_row()
   ret = {'deleted':db.do("DELETE FROM devices WHERE id = '%s'"%aDict['id'])}
   from dns import record_auto_delete
   ret.update(record_auto_delete({'A':data['a_id'],'PTR':data['ptr_id']}))
   if data['base'] == 'pdu':
    ret['pem0'] = db.do("UPDATE rackinfo SET pem0_pdu_unit = 0, pem0_pdu_slot = 0 WHERE pem0_pdu_id = '%s'"%(aDict['id']))
    ret['pem1'] = db.do("UPDATE rackinfo SET pem1_pdu_unit = 0, pem1_pdu_slot = 0 WHERE pem1_pdu_id = '%s'"%(aDict['id']))
 return ret

#
#
def clear(aDict):
 """Function docstring for clear TBD

 Args:

 Extra:
 """
 with DB() as db:
  res = db.do("DELETE FROM devices")
 return { 'result':res }

############################################# Specials ###########################################
#
#
def function(aDict):
 """Function docstring for function TBD

 Args:
  - ip (required)
  - op (required)
  - type (required)

 Extra:
 """
 ret = {}
 from importlib import import_module
 try:
  module = import_module("sdcp.devices.%s"%(aDict['type']))
  dev = getattr(module,'Device',lambda x: None)(aDict['ip'])
  with dev:
   ret['data'] = getattr(dev,aDict['op'],None)()
  ret['result'] = 'OK'
 except Exception as err:
  ret = {'result':'ERROR','info':str(err)}
 return ret

#
#
def configuration_template(aDict):
 """Function docstring for configuration TBD

 Args:
  - id (required)

 Extra:
 """
 from importlib import import_module
 ret = {}
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) AS ipasc, hostname, mask, INET_NTOA(gateway) AS gateway, INET_NTOA(subnet) AS subnet, devicetypes.name AS type, domains.name AS domain FROM devices LEFT JOIN domains ON domains.id = devices.subnet_id LEFT JOIN devicetypes ON devicetypes.id = devices.type_id LEFT JOIN subnets ON subnets.id = devices.subnet_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ipasc',None)
 try:
  module = import_module("sdcp.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x: None)(ip)
  ret['data'] = dev.configuration(data)
  ret['result'] = 'OK'
 except Exception as err:
  ret = {'result':'ERROR','info':str(err)} 
 return ret

#
#
def discover(aDict):
 """Function docstring for discover TBD

 Args:
  - a_dom_id (required)
  - subnet_id (required)

 Extra:
 """
 from time import time
 from threading import Thread, BoundedSemaphore
 from struct import pack
 from socket import inet_ntoa

 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 def _tdetect(aIPint,aDB,aSema):
  res = detect({'ip':GL_int2ip(aIPint)})
  if res['result'] == 'OK':
   aDB[aIPint] = res['info']
  aSema.release()
  return True

 start_time = int(time())
 ret = {'errors':0 }

 with DB() as db:
  db.do("SELECT id,name FROM devicetypes")
  devtypes = db.get_dict('name')
  db.do("SELECT subnet,mask FROM subnets WHERE id = '%s'"%aDict['subnet_id'])
  net = db.get_row()

  ip_start = net['subnet'] + 1
  ip_end   = net['subnet'] + 2**(32 - net['mask']) - 1
  ret.update({'start':GL_int2ip(ip_start),'end':GL_int2ip(ip_end)})

  db_old, db_new = {}, {}
  ret['xist'] = db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(ip_start,ip_end))
  rows = db.get_rows()
  for item in rows:
   db_old[item['ip']] = True
  try:
   sema = BoundedSemaphore(10)
   for ipint in range(ip_start,ip_end):
    if db_old.get(ipint):
     continue
    sema.acquire()
    t = Thread(target = _tdetect, args=[ipint, db_new, sema])
    t.name = "Detect %s"%ip
    t.start()

   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()
   # We can now do inserts only (no update) as either we clear or we skip existing :-)
   sql = "INSERT INTO devices (ip, a_dom_id, subnet_id, snmp, model, type_id, hostname) VALUES ('{}',"+aDict['a_dom_id']+",{},'{}','{}','{}','{}')"
   count = 0
   for ipint,entry in db_new.iteritems():
    count += 1
    db.do(sql.format(ipint,aDict['subnet_id'],entry['snmp'],entry['model'],devtypes[entry['type']]['id'],"unknown_%i"%count))
  except Exception as err:
   ret['info']   = "Error:{}".format(str(err))
   ret['errors'] += 1

  ret['info'] = "Time spent:{}".format(int(time()) - start_time)
  ret['found']= len(db_new)
 return ret

#
#
def detect(aDict):
 """Function docstring for detect TBD

 Args:
  - ip (required)
  - update (optional)

 Extra:
 """
 from os import system
 if system("ping -c 1 -w 1 {} > /dev/null 2>&1".format(aDict['ip'])) != 0:
  return {'result':'NOT_OK'}

 from .. import SettingsContainer as SC
 from netsnmp import VarList, Varbind, Session
 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aDict['ip'], Community = SC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except:
  pass

 info = {'model':'unknown', 'type':'generic'}
 info['snmp'] = devobjs[1].val.lower() if devobjs[1].val else 'unknown'

 if devobjs[0].val:
  infolist = devobjs[0].val.split()
  if infolist[0] == "Juniper":
   if infolist[1] == "Networks,":
    info['model'] = infolist[3].lower()
    for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
     if tp in info['model']:
      info['type'] = tp
      break
   else:
    subinfolist = infolist[1].split(",")
    info['model'] = subinfolist[2]
  elif infolist[0] == "VMware":
   info['model'] = "esxi"
   info['type']  = "esxi"
  elif infolist[0] == "Linux":
   info['model'] = 'debian' if "Debian" in devobjs[0].val else 'generic'
  else:
   info['model'] = " ".join(infolist[0:4])

 ret = {'result':'OK','info':info}
 if aDict.get('update',False):
  with DB() as db:
   xist = db.do("SELECT id,name FROM devicetypes WHERE name = '{}'".format(info['type']))
   ret['type_id'] = db.get_val('id') if xist > 0 else None
   ret['update']  = db.do("UPDATE devices SET snmp = '{}', model = '{}', type_id = '{}' WHERE ip = INET_ATON('{}')".format(info['snmp'],info['model'],ret['type_id'],aDict['ip'])) > 0
 return ret

############################################# Munin ###########################################
#
#
def graph_save(aDict):
 """Function docstring for graph_save TBD

 Args:

 Extra:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT value FROM settings WHERE section='graph' AND parameter = 'file'")
  graph_file = db.get_val('value')
  ret['xist'] = db.do("SELECT hostname, INET_NTOA(graph_proxy) AS proxy, domains.name AS domain FROM devices INNER JOIN domains ON domains.id = devices.a_dom_id WHERE graph_update = 1")
  rows = db.get_rows()
 with open(graph_file,'w') as output:
  for row in rows:
   output.write("[{}.{}]\n".format(row['hostname'],row['domain']))
   output.write("address {}\n".format(row['proxy']))
   output.write("update yes\n\n")
 return ret

#
#
def graph_info(aDict):
 """Function docstring for graph_info TBD

 Args:
  - id
  - op (optional)
  - graph_proxy (optional)
  - graph_update (optional)


 Extra:
 """
 with DB() as db:
  ret = {}
  if aDict.get('op') == 'update':
   ret['changed'] = db.do("UPDATE devices SET graph_proxy = INET_ATON('%s'), graph_update = %i WHERE id = %i"%(aDict.get('graph_proxy'),int(aDict.get('graph_update',0)),int(aDict['id'])))

  db.do("SELECT INET_NTOA(ip) AS ip, graph_update, devicetypes.name AS type_name, INET_NTOA(graph_proxy) AS graph_proxy, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = '%s'"%aDict['id'])
  ret.update(db.get_row())
  db.do("SELECT value AS plugin_file FROM settings WHERE section = 'graph' AND parameter = 'plugins'")
  ret.update(db.get_row())

  if aDict.get('op') == 'detect':
   def GL_ping_os(ip):
    from os import system
    return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0
  
   if GL_ping_os(ret['ip']):
    try:
     if ret['type_name'] in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
      from ..devices.junos import Junos
      activeinterfaces = []
      if not ret['type_name'] == 'wlc':
       with Junos(ret['ip']) as jdev:
        activeinterfaces = jdev.get_up_interfaces()
       with open(ret['plugin_file'], 'a') as graphfile:
        graphfile.write('ln -s /usr/local/sbin/plugins/snmp__{0} /etc/munin/plugins/snmp_{1}_{0}\n'.format(ret['type_name'],ret['fqdn']))
        graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + ret['fqdn'] + '_uptime\n')
        graphfile.write('ln -s /usr/share/munin/plugins/snmp__users  /etc/munin/plugins/snmp_' + ret['fqdn'] + '_users\n')
        for ifd in activeinterfaces:
         graphfile.write('ln -s /usr/share/munin/plugins/snmp__if_    /etc/munin/plugins/snmp_' + ret['fqdn'] + '_if_'+ ifd['SNMP'] +'\n')
     elif ret['type_name'] == "esxi":
      with open(ret['plugin_file'], 'a') as graphfile:
       graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + ret['fqdn'] + '_uptime\n')              
       graphfile.write('ln -s /usr/local/sbin/plugins/snmp__esxi    /etc/munin/plugins/snmp_' + ret['fqdn'] + '_esxi\n')
    except Exception as err:
     ret['op'] = "Error:%s"%str(err)
    else:
     ret['op'] = 'OK'
   else:
    ret['op'] = 'NO_PING'

 return ret
