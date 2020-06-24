"""Statistics API module. Implements device statistics methods"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def query_interface(aCTX, aArgs):
 """ Function retrieves/queries database for interface_statistics, formatted to Xbps

 Args:
  - device_id (required)
  - interface_id (required)
  - range (optional). hours, default: 1
  - unit (optional). 'b','k','m', default: 'k' as kbps

 Output:
 """
 db = aCTX.config['influxdb']
 unit = {'b':1,'k':1024,'m':1048576}.get(aArgs.get('unit','k'))
 args = {'q':"SELECT non_negative_derivative(mean(in8s), 1s)*8/{0}, non_negative_derivative(mean(out8s), 1s)*8/{0}, non_negative_derivative(mean(inUPs), 1s), non_negative_derivative(mean(outUPs), 1s) FROM interface WHERE host_id = '{1}' AND if_id = '{2}' AND time >= now() - {3}h GROUP BY time(1m) fill(null)".format(unit,aArgs['device_id'],aArgs['interface_id'],aArgs.get('range','1'))}
 try: res = aCTX.rest_call("%s/query?db=%s&epoch=s"%(db['url'],db['database']), aMethod = 'POST', aApplication = 'x-www-form-urlencoded', aArgs = args)['results'][0]
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  return {'data':[{'time':x[0],'in8s':x[1],'out8s':x[2],'inUPs':x[3],'outUPs':x[4]} for x in res['series'][0]['values']] if 'series' in res else []}

################################## Device Data Points ###################################
#
#
def list(aCTX, aArgs):
 """ Function provides stats for a device

 Args:
  - device_id (required)
  - lookup (optional) bool

 Output:
  - data
 """
 ret = {}
 id = aArgs['device_id']
 select = ['ds.*']
 tables = ['device_statistics AS ds']
 with aCTX.db as db:
  db.query("SELECT %s FROM %s WHERE device_id = %s"%(', '.join(select),' LEFT JOIN '.join(tables),id))
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aCTX, aArgs):
 """ Function provides data point management for a device

 Args:
  - id (required)
  - device_id (optional required). Used when entering a new data point
  - op (optional)
  - <data>

 Output:
  - <data>
  - update (optional)
 """
 ret = {}
 id = aArgs.pop('id',None)
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if id != 'new':
    ret['update'] = (db.update_dict('device_statistics',aArgs,'id=%s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('device_statistics',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'

  if id != 'new':
   ret['found'] = (db.query("SELECT * FROM device_statistics WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','device_id':aArgs['device_id'], 'measurement':"",'tags':"",'name':"",'oid':""}
 return ret

#
#
def delete(aCTX, aArgs):
 """ Function deletes a data point

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = (db.execute("DELETE FROM device_statistics WHERE id = %s"%aArgs['id']) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret

#
#
def lookup(aCTX, aArgs):
 """ Function looks up device type based data points

 Args:
 - device_id

 Output:
 """
 id = aArgs['device_id']
 ret = {'inserts':0}
 from importlib import import_module
 with aCTX.db as db:
  if db.query("SELECT INET6_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = %s"%id):
   info = db.get_row()
   try:
    module = import_module("rims.devices.%s"%info['type'])
    device = getattr(module,'Device',None)(aCTX, id, info['ip'])
    for ddp in device.get_data_points():
     ret['inserts'] += db.execute("INSERT INTO device_statistics (device_id,measurement,tags,name,oid) VALUES(%i,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = id"%(int(id),ddp[0],ddp[1],ddp[2],ddp[3]))
   except Exception as e:
    ret['status'] = 'NOT_OK'
    ret['info'] = str(e)
   else:
    ret['status'] = 'OK'
    ret['result'] = '%s data points inserted'%ret['inserts']
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'device info not found'
 return ret

#################################### Monitor #################################
#
#
def check(aCTX, aArgs):
 """ Initiate a status check for all or a subset of devices' interfaces

 Args:
  - networks (optional). List of subnet_ids to check
  - repeat (optional). value of seconds between repeated occurances of statistics gatering

 Output:
  - status
 """
 devices = []

 with aCTX.db as db:
  db.query("SELECT id FROM ipam_networks" if 'networks' not in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  db.query("SELECT devices.id AS device_id, INET6_NTOA(ia.ip) AS ip, devices.hostname FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.network_id IN (%s) AND ia.state = 'up' AND devices.class IN ('infrastructure','vm','out-of-band') ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows())))
  for dev in db.get_rows():
   if db.query("SELECT measurement,tags,name,oid FROM device_statistics WHERE device_id = %s"%dev['device_id']):
    dev['data_points'] = []
    measurements = {}
    for ddp in db.get_rows():
     try:
      tobj = measurements[ddp['measurement']]
     except:
      measurements[ddp['measurement']] = tobj = {}
     vobj = tobj.get(ddp['tags'],[])
     if not vobj:
      tobj[ddp['tags']] = vobj
     vobj.append({'name':ddp['name'],'oid':ddp['oid'],'value':None})
    for m,tags in measurements.items():
     dev['data_points'].extend([{'measurement':m,'tags':t,'snmp':values} for t,values in tags.items()])
   if db.query("SELECT snmp_index,interface_id,name FROM interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']):
    dev['interfaces'] = db.get_rows()
   if any(i in dev for i in ['data_points','interfaces']):
    devices.append(dev)

 if not devices:
  return {'status':'OK','function':'statistics_check','info':'no devices'}
 if 'repeat' in aArgs:
  # INTERNAL from rims.api.statistics import process
  aCTX.schedule_api_periodic(process,'statistics_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debugging())
  return {'status':'OK','function':'statistics_check','detach_frequency':aArgs['repeat']}
 else:
  # INTERNAL from rims.api.statistics import process
  return process(aCTX,{'devices':devices})

#
#
def process(aCTX, aArgs):
 """ Function processes a list of devices with datapoints and their interfaces

 Args:
  - devices (required), each device object has a list of interface objects and optionally data points objects

 Output:
 """
 from rims.devices.generic import Device
 nodes = [x['node'] for x in aCTX.services.values() if x['service'] == 'influxdb']
 report = aCTX.node_function(nodes[0],'statistics','report', aHeader= {'X-Log':'false'})
 ret = {'status':'OK','function':'statistics_process','reported':0}
 def __check_sp(aDev):
  try:
   device = Device(aCTX, aDev['device_id'], aDev['ip'])
   if device.data_points(aDev.get('data_points',[]), aDev['interfaces'])['status'] == 'OK':
    report(aArgs = aDev)
    ret['reported'] += 1
  except Exception as e:
   aCTX.log("statistics_process_failed for device: %s =>%s"%(aDev['device_id'],str(e)))
   return False
  else:
   return True

 aCTX.queue_block(__check_sp,aArgs['devices'])
 return ret

#
#
def report(aCTX, aArgs):
 """Function updates statistics for a particular devices to influxdb - service must be running on this node

 Args:
  - device_id (required). Device id
  - interfaces (required). list of interface objects
  - data_points (optional). list of objects like {'measurement':<measurement>,'tags':'<tag-name>=<tag_value>,...', 'values':[{'name':<name>,'value':<value1>},...]}

 Output:
 """
 from datetime import datetime
 ret = {'status':'NOT_OK','function':'statistics_report'}
 args = []
 db = aCTX.config['influxdb']
 ts = int(datetime.now().timestamp())
 if 'interfaces' in aArgs:
  tmpl = ('interface,host_id={0},host_ip={1},if_id=%i,if_name=%b in8s=%ii,inUPs=%ii,out8s=%ii,outUPs=%ii {2}'.format(aArgs['device_id'],aArgs['ip'],ts)).encode()
  args.extend([tmpl%(x['interface_id'],x['name'].replace(' ','\ ').encode(),x['in8s'],x['inUPs'],x['out8s'],x['outUPs']) for x in aArgs['interfaces']])
 if 'data_points' in aArgs:
  tmpl = ('%b,host_id={0},host_ip={1},%b %b {2}'.format(aArgs['device_id'],aArgs['ip'],ts)).encode()
  args.extend([tmpl%(m['measurement'].encode(),m['tags'].replace(' ','\ ').encode(),(','.join(["%(name)s=%(value)s"%x for x in m['snmp']])).encode()) for m in aArgs['data_points']])
 try:   aCTX.rest_call("%s/write?db=%s&precision=s"%(db['url'],db['database']), aMethod = 'POST', aApplication = 'octet-stream', aArgs = b'\n'.join(args))
 except Exception as e:
  ret['info'] = str(e)
  aCTX.log("statistics_report_error: %s"%str(e))
 else:  ret['status'] = 'OK'
 return ret
