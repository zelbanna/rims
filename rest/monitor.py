"""Monitor API module. Provides generic device monitoring"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#################################### Status management #################################
#
#
#
#
def ipam_events(aCTX, aArgs = None):
 """ Function operates on events

 Args:
  - id (optional). find events for id
  - op (optional). 'clear'. clears events (all or for 'id')
  - extra (optional). list of extra fields to add (hostname,ip,ip_state)
  - limit (optional)
  - offset (optional)

 Output:
  - status
  - count (optional)
  - events (optional) list of {'time','state',<extra>} entries
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  if aArgs.get('op') == 'clear':
   if 'id' in aArgs:
    ret['count'] = db.do("DELETE FROM ipam_events WHERE ipam_id = %s"%aArgs['id'])
   else:
    db.do("TRUNCATE ipam_events")
  else:
   fields = ['DATE_FORMAT(ie.time,"%Y-%m-%d %H:%i") AS time', 'ie.state']
   tables = ['ipam_events AS ie']
   if 'id' in aArgs:
    filter = "ie.ipam_id = %s"%aArgs['id']
   else:
    filter = "TRUE"
    fields.append('ie.ipam_id AS id')
   if 'extra' in aArgs:
    tables.append('ipam_addresses AS ia')
    if 'hostname' in aArgs['extra']:
     fields.append('ia.hostname')
    if 'ip' in aArgs['extra']:
     fields.append('INET_NTOA(ia.ip) AS ip')
    if 'ip_state' in aArgs['extra']:
     fields.append('ia.state AS ip_state')
   ret['count'] = db.do("SELECT {} FROM {} WHERE {} ORDER BY time DESC LIMIT {} OFFSET {}".format(", ".join(fields), " LEFT JOIN ".join(tables), filter, aArgs.get('limit','50'), aArgs.get('offset','0')))
   ret['events']= db.get_rows()
 return ret

#
#
def ipam_status(aCTX, aArgs = None):
 """ Initiate a status check for all or a subset of IP:s that belongs to proper interfaces

 Args:
  - networks (optional). List of network ids to check
  - repeat (optional). If declared, it's an integer with frequency.. This is the way to keep status checks 'in-memory'

 """
 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  networks = db.get_rows()
  # ('wired','optical','virtual')
  db.do("SELECT ia.id, INET_NTOA(ia.ip) AS ip, ia.state FROM ipam_addresses AS ia LEFT JOIN device_interfaces AS di ON di.ipam_id = ia.id WHERE network_id IN (%s) AND di.class <= 3 ORDER BY ip"%(','.join(str(x['id']) for x in networks)))
  addresses = db.get_rows()

 if 'repeat' in aArgs:
  aCTX.workers.add_task('monitor','ipam_process',int(aArgs['repeat']),args = {'addresses':addresses}, output = aCTX.debugging())
  return {'status':'OK','info':'MONITOR_CONTINUOUS_INITIATED_F%s'%aArgs['repeat']}
 else:
  ipam_process(aCTX,{'addresses':addresses})
  return {'status':'OK'}

#
#
def ipam_process(aCTX, aArgs = None):
 """ Function checks all IP addresses

 Args:
  - addresses (required). List of addresses

 Output:
 """
 ret = {'status':'OK'}
 from os import system

 def __check_ip(aDev):
  aDev['old'] = aDev['state']
  try:    aDev['state'] = 'up' if (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aDev['ip'])) == 0) or (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aDev['ip'])) == 0) else 'down'
  except: aDev['state'] = 'unknown'
  return True

 nworkers = max(20,int(aCTX.config['workers']) - 5)
 sema = aCTX.workers.semaphore(nworkers)
 for dev in aArgs['addresses']:
  aCTX.workers.add_semaphore(__check_ip, sema, dev)
 aCTX.workers.block(sema,nworkers)
 changed = [dev for dev in aArgs['addresses'] if (dev['state'] != dev['old'])]
 if changed:
  args = {'up':[x['id'] for x in changed if x['state'] == 'up'], 'down':[x['id'] for x in changed if x['state'] == 'down']}
  ret['up'] = len(args['up'])
  ret['down'] = len(args['down'])
  ipam_report(aCTX,args)
 return ret

#
#
def ipam_report(aCTX, aArgs = None):
 """ Updates addresses' status

 Args:
  - up (optional).   List of id that changed to up
  - down (optional). List of id that changed to down

 Output:
  - up (number of updated up state)
  - down (number of updated down state)
 """
 ret = {}
 with aCTX.db as db:
  for chg in ['up','down']:
   change = aArgs.get(chg)
   if change:
    ret[chg] = db.do("UPDATE ipam_addresses SET state = '%s' WHERE ID IN (%s)"%(chg,",".join(str(x) for x in change)))
    begin = 0
    final  = len(change)
    while begin < final:
     end = min(final,begin+16)
     db.do("INSERT INTO ipam_events (ipam_id, state) VALUES %s"%(",".join("(%s,'%s')"%(x,chg) for x in change[begin:end])))
     begin = end

 return ret

################################### Interface ####################################
#
#

def interface_status(aCTX, aArgs = None):
 """ Initiate a status check for all or a subset of devices' L2 interfaces, if the device is in up state (!)

 Args:
  - networks (optional). List of subnet_ids to check

 """
 ret = {}
 devices = []
 discover = (aArgs.get('discover') in ['up','all'])

 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  db.do("SELECT devices.id AS device_id, INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id LEFT JOIN device_types AS dt ON devices.type_id = dt.id WHERE ia.network_id IN (%s) ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows())))
  for dev in db.get_rows():
   if (db.do("SELECT snmp_index,interface_id FROM device_interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']) > 0):
    dev['interfaces'] = db.get_rows()
    devices.append(dev)

 interface_process(aCTX,{'devices':devices})
 return {'status':'OK'}

#
#
def interface_process(aCTX, aArgs = None):
 """ Function processes a list of devices and their interfaces

 TODO: parse mac and name here instead of in report

 Args:
  - devices (required)
  - discover (optional). False/None/"up"/"all", defaults to false

 Output:
 """
 from importlib import import_module
 report   = aCTX.node_function('master','monitor','interface_report', aHeader= {'X-Log':'false'})

 def __check_if(aCTX, aDev):
  try:
   module = import_module("rims.devices.%s"%aDev['type'])
   device = getattr(module,'Device',None)(aCTX, aDev['device_id'], aDev['ip'])
   probe  = device.interfaces()
   exist  = aDev['interfaces']
   for intf in exist:
    intf.update( probe.pop(intf.get('snmp_index','NULL'),{}) )
   if len(exist) > 0:
    report(aArgs = aDev)
  except Exception as e:
   aCTX.log("monitor_interface_process issue for device %s: %s"%(aDev['device_id'],str(e)))
  return True

 nworkers = max(20,int(aCTX.config['workers']) - 5)
 sema = aCTX.workers.semaphore(nworkers)
 for dev in aArgs['devices']:
  aCTX.workers.add_semaphore(__check_if, sema, aCTX, dev)
 aCTX.workers.block(sema,nworkers)

 return True

#
#
def interface_report(aCTX, aArgs = None):
 """Function updates interface status for a particular device

 Args:
  - device_id (required). Device id
  - interfaces (required). list of interface objects {interface_id,snmp_index,name,state,mac,description}

 Output:
 """
 ret = {'update':0,'insert':0}
 def mac2int(aMAC):
  try:    return int(aMAC.replace(':',""),16)
  except: return 0

 with aCTX.db as db:
  for intf in aArgs['interfaces']:
   args = {'device_id':aArgs['device_id'],'snmp_index':intf['snmp_index'],'interface_id':intf.get('interface_id'), 'mac':mac2int(intf.get('mac',0)), 'name':intf.get('name','NA')[:25],'state':intf.get('state','unknown'),'description':intf.get('description','NA')}
   ret['update'] += db.do("UPDATE device_interfaces SET name = '%(name)s', mac = %(mac)s, state = '%(state)s', description = '%(description)s' WHERE interface_id = %(interface_id)s"%args)
 return ret

############################## INTERFACE STATS ###############################

def statistics_init(aCTX, aArgs = None):
 """ Initiate a status check for all or a subset of devices' interfaces

 Args:
  - networks (optional). List of subnet_ids to check
  - repeat (optional). value of seconds between repeated occurances of statistics gatering

 Output:
  - status
 """
 ret = {}
 devices = []

 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  db.do("SELECT devices.id AS device_id, INET_NTOA(ia.ip) AS ip, devices.hostname FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE ia.network_id IN (%s) AND ia.state = 'up' AND devices.class IN ('infrastructure','vm','out-of-band') ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows())))
  for dev in db.get_rows():
   if (db.do("SELECT snmp_index,interface_id,name FROM device_interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']) > 0):
    dev['interfaces'] = db.get_rows()
    devices.append(dev)

 if 'repeat' in aArgs:
  aCTX.workers.add_task('monitor','statistics_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debugging())
  return {'status':'OK','info':'MONITOR_CONTINUOUS_INITIATED_F%s'%aArgs['repeat']}
 else:
  return statistics_process(aCTX,{'devices':devices})

#
#
def statistics_process(aCTX, aArgs = None):
 """ Function processes a list of devices and their interfaces

 Args:
  - devices (required)

 Output:
 """
 from rims.devices.generic import Device
 report   = aCTX.node_function('master','monitor','statistics_report', aHeader= {'X-Log':'false'})

 def __check_sp(aCTX, aDev):
  try:
   device = Device(aCTX, aDev['device_id'], aDev['ip'])
   res = device.interface_stats(aDev['interfaces'])
   if res['status'] == 'OK':
    report(aArgs = aDev)
  except Exception as e:
   aCTX.log("monitor_statstics_process issue for device %s: %s"%(aDev['device_id'],str(e)))
  return True

 nworkers = max(20,int(aCTX.config['workers']) - 5)
 sema = aCTX.workers.semaphore(nworkers)
 for dev in aArgs['devices']:
  aCTX.workers.add_semaphore(__check_sp, sema, aCTX, dev)
 aCTX.workers.block(sema,nworkers)

 return {'status':'OK'}

#
#
def statistics_report(aCTX, aArgs = None):
 """Function updates statistics for a particular devices to influxdb

 Args:
  - device_id (required). Device id
  - interfaces (required). list of interface objects
  - monitor_items (optional). list of objects like {'measurement':<measurement>,'tags':'<tag-name>=<tag_value>,...', 'values':[<name1>:<value1>...]}

 Output:
 """
 ret = {'status':'NOT_OK'}

 if ('influxdb' in [x['service'] for x in aCTX.services.values() if x['node'] == aCTX.node]):
  from datetime import datetime
  db = aCTX.config['influxdb']
  ts = int(datetime.now().timestamp())
  tmpl  = ('interface,host_id={0},host_ip={1},if_id=%i,if_name=%b in8s=%i,inUPs=%i,out8s=%i,outUPs=%i {2}'.format(aArgs['device_id'],aArgs['ip'],ts)).encode()
  args = b'\n'.join([tmpl%(x['interface_id'],x['name'].encode(),x['in8s'],x['inUPs'],x['out8s'],x['outUPs']) for x in aArgs['interfaces']])
  try:   aCTX.rest_call("%s/write?db=%s&precision=s"%(db['url'],db['database']), aApplication = 'octet-stream', aArgs = args)
  except Exception as e: ret['info'] = str(e)
  else:  ret['status'] = 'OK'
 else:
  ret['info'] = 'No InfluxDB configured and initialized on local node'
 return ret
