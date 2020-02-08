"""Monitor API module. Provides generic device monitoring"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#################################### IP Address #################################
#
#
def ipam_init(aCTX, aArgs = None):
 """ Initiate a status check for all or a subset of IP:s that belongs to proper interfaces

 Args:
  - networks (optional). List of network ids to check
  - repeat (optional). If declared, it's an integer with frequency.. This is the way to keep status checks 'in-memory'

 """
 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  networks = db.get_rows()
  db.do("SELECT ia.id, INET_NTOA(ia.ip) AS ip, ia.state FROM ipam_addresses AS ia LEFT JOIN device_interfaces AS di ON di.ipam_id = ia.id WHERE network_id IN (%s) AND di.class IN ('wired','optical','virtual') ORDER BY ip"%(','.join(str(x['id']) for x in networks)))
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

 aCTX.workers.block_map(__check_ip,aArgs['addresses'])

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
    ret[chg] = db.do("UPDATE ipam_addresses SET state = '%s' WHERE id IN (%s)"%(chg,",".join(str(x) for x in change)))
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

def interface_init(aCTX, aArgs = None):
 """ Initiate a status check for devices' interfaces.

 Args:
  - networks (optional). List of subnet_ids to check
  - repeat (optional). In-memory repetition of state check

 """
 ret = {}
 devices = []

 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  db.do("SELECT devices.id AS device_id, INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE ia.network_id IN (%s) ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows())))
  for dev in db.get_rows():
   if (db.do("SELECT snmp_index,interface_id,state FROM device_interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']) > 0):
    dev['interfaces'] = db.get_rows()
    devices.append(dev)

 if 'repeat' in aArgs:
  aCTX.workers.add_task('monitor','interface_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debugging())
  return {'status':'OK','info':'MONITOR_CONTINUOUS_INITIATED_F%s'%aArgs['repeat']}
 else:
  interface_process(aCTX,{'devices':devices})
  return {'status':'OK'}

#
#
def interface_process(aCTX, aArgs = None):
 """ Function processes a list of devices and their interfaces

 Args:
  - devices (required)

 Output:
 """
 from rims.devices.generic import Device
 report   = aCTX.node_function('master','monitor','interface_report', aHeader= {'X-Log':'false'})

 def __check_if(aDev):
  try:
   if len(aDev['interfaces']) > 0:
    device = Device(aCTX, aDev['device_id'], aDev['ip'])
    probe  = device.interfaces_state()
    for intf in aDev['interfaces']:
     intf['old'] = intf['state']
     intf['state'] = probe.get(intf['snmp_index'],'unknown')
    changed = [intf for intf in aDev['interfaces'] if intf['state'] != intf['old']]
    if changed:
     report(aArgs = {'device_id':aDev['device_id'],'up':[x['interface_id'] for x in changed if x['state'] == 'up'], 'down':[x['interface_id'] for x in changed if x['state'] == 'down']})

  except Exception as e:
   aCTX.log("monitor_interface_process issue for device %s: %s"%(aDev['device_id'],str(e)))
   return True

 aCTX.workers.block_map(__check_if,aArgs['devices'])

 return True

#
#
def interface_report(aCTX, aArgs = None):
 """Function updates interface status

 Args:
  - device_id (required)
  - up (optional).   List of id that changed to up
  - down (optional). List of id that changed to down

 Output:
 """
 ret = {'status':'OK','update':0}
 with aCTX.db as db:
  for chg in ['up','down']:
   if aArgs.get(chg):
    ret[chg] = db.do("UPDATE device_interfaces SET state = '%s' WHERE interface_id IN (%s)"%(chg,",".join(str(x) for x in aArgs[chg])))
 return ret

############################## Statistics ###############################

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
   if (db.do("SELECT measurement,tags,name,oid FROM device_data_points WHERE device_id = %s"%dev['device_id']) > 0):
    dev['data_points'] = []
    measurements = {}
    for ddp in db.get_rows():
     tobj = measurements.get(ddp['measurement'],{})
     if len(tobj) == 0:
      measurements[ddp['measurement']] = tobj
     vobj = tobj.get(ddp['tags'],[])
     if len(vobj) == 0:
      tobj[ddp['tags']] = vobj
     vobj.append({'name':ddp['name'],'oid':ddp['oid'],'value':None})
    for m,tags in measurements.items():
     dev['data_points'].extend([{'measurement':m,'tags':t,'snmp':values} for t,values in tags.items()])
   if (db.do("SELECT snmp_index,interface_id,name FROM device_interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']) > 0):
    dev['interfaces'] = db.get_rows()
   if any(i in dev for i in ['data_points','interfaces']):
    devices.append(dev)

 if 'repeat' in aArgs:
  aCTX.workers.add_task('monitor','statistics_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debugging())
  return {'status':'OK','info':'MONITOR_CONTINUOUS_INITIATED_F%s'%aArgs['repeat']}
 else:
  return statistics_process(aCTX,{'devices':devices})

#
#
def statistics_process(aCTX, aArgs = None):
 """ Function processes a list of devices with  datapoints and their interfaces

 Args:
  - devices (required), each device object has a list of interface objects and optionally data points objects

 Output:
 """
 from rims.devices.generic import Device
 report = aCTX.node_function('master','monitor','statistics_report', aHeader= {'X-Log':'false'})

 def __check_sp(aDev):
  try:
   device = Device(aCTX, aDev['device_id'], aDev['ip'])
   if device.data_points(aDev.get('data_points',[]), aDev['interfaces'])['status'] == 'OK':
    report(aArgs = aDev)
  except Exception as e:
   aCTX.log("statistics_process_failed for device: %s =>%s"%(aDev['device_id'],str(e)))
   return False
  else:
   return True

 aCTX.workers.block_map(__check_sp,aArgs['devices'])

 return {'status':'OK'}

#
#
def statistics_report(aCTX, aArgs = None):
 """Function updates statistics for a particular devices to influxdb

 Args:
  - device_id (required). Device id
  - interfaces (required). list of interface objects
  - data_points (optional). list of objects like {'measurement':<measurement>,'tags':'<tag-name>=<tag_value>,...', 'values':[{'name':<name>,'value':<value1>},...]}

 Output:
 """
 ret = {'status':'NOT_OK'}
 if ('influxdb' in [x['service'] for x in aCTX.services.values() if x['node'] == aCTX.node]):
  from datetime import datetime
  args = []
  db = aCTX.config['influxdb']
  ts = int(datetime.now().timestamp())
  if 'interfaces' in aArgs:
   tmpl = ('interface,host_id={0},host_ip={1},if_id=%i,if_name=%b in8s=%ii,inUPs=%ii,out8s=%ii,outUPs=%ii {2}'.format(aArgs['device_id'],aArgs['ip'],ts)).encode()
   args.extend([tmpl%(x['interface_id'],x['name'].replace(' ','\ ').encode(),x['in8s'],x['inUPs'],x['out8s'],x['outUPs']) for x in aArgs['interfaces']])
  if 'data_points' in aArgs:
   tmpl = ('%b,host_id={0},host_ip={1},%b %b {2}'.format(aArgs['device_id'],aArgs['ip'],ts)).encode()
   args.extend([tmpl%(m['measurement'].encode(),m['tags'].replace(' ','\ ').encode(),(','.join(["%(name)s=%(value)s"%x for x in m['snmp']])).encode()) for m in aArgs['data_points']])
  try:   aCTX.rest_call("%s/write?db=%s&precision=s"%(db['url'],db['database']), aApplication = 'octet-stream', aArgs = b'\n'.join(args))
  except Exception as e:
   ret['info'] = str(e)
   aCTX.log("statistics_report_error: %s"%str(e))
  else:  ret['status'] = 'OK'
 else:
  ret['info'] = 'No InfluxDB configured and initialized on local node'
 return ret
