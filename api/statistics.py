"""Statistics API module. Implements device statistics methods for influxDB """
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def query_interface(aCTX, aArgs):
 """ Function retrieves/queries database for interface statistics, formatted to Xbps

 Args:
  - device_id (required)
  - interface_id (required)
  - range (optional). hours, default: 1

 Output:
  - header, list of column names as flux doesn't respect ordering
  - data, list of rows according to 'header' layout.
 """
 ret = {}
 query = f'from(bucket: "rims") |> range(start: -{aArgs.get("range",1)}h) |> filter(fn: (r) => r.host_id == "{aArgs["device_id"]}" and r.if_id == "{aArgs["interface_id"]}") |> derivative(nonNegative: true, unit: 1s) |> group(columns: ["_field"]) |> keep(columns: ["_time","_field","_value"])'
 try:
  dialect = {'annotations': ['default'], 'comment_prefix': '#', 'date_time_format': 'RFC3339', 'delimiter': ',', 'header': True}
  res = aCTX.influxdb_client.query_api().query_csv(dialect=dialect, query = query)
  if any(res):
   ret['header'] = next(res)[3:]
   ret['data'] = [r[3:] for r in res]
   ret['data'].pop()
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'empty'
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  return ret


#
#
def query_device(aCTX, aArgs):
 """ Function retrieves/queries database for device (DDP) statistics

 Args:
  - device_id (required)
  - measurement (required)
  - name (required)
  - range (optional). hours, default: 1

 Output:
  - header, list of column names as flux doesn't respect ordering
  - data, list of rows according to 'header' layout.
 """
 ret = {}
 query = f'from(bucket: "rims") |> range(start: -{aArgs.get("range",1)}h) |> filter(fn: (r) => r.host_id == "{aArgs["device_id"]}" and r._measurement == "{aArgs["measurement"]}" and r._field == "{aArgs["name"]}") |> group(columns: ["_field"]) |> keep(columns: ["_time","_field","_value"])'
 try:
  dialect = {'annotations': ['default'], 'comment_prefix': '#', 'date_time_format': 'RFC3339', 'delimiter': ',', 'header': True}
  res = aCTX.influxdb_client.query_api().query_csv(dialect=dialect, query = query)
  if any(res):
   ret['header'] = next(res)[3:]
   ret['data'] = [r[3:] for r in res]
   ret['data'].pop()
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'empty'
 except Exception as e:
  return {'status':'NOT_OK','info':str(e)}
 else:
  return ret

################################## Device Statistics ###################################
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
   # Reset OID to NULL if not set, treat as externally data
   aArgs['oid'] = None if not aArgs['oid'] else aArgs['oid']
   if id != 'new':
    ret['update'] = (db.update_dict('device_statistics',aArgs,f'id={id}') > 0)
   else:
    ret['update'] = (db.insert_dict('device_statistics',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'

  if id != 'new':
   ret['found'] = (db.query(f'SELECT * FROM device_statistics WHERE id = {id}') > 0)
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
  ret['deleted'] = (db.execute(f'DELETE FROM device_statistics WHERE id = {aArgs["id"]}') == 1)
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
  if db.query(f'SELECT INET6_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = {id}'):
   info = db.get_row()
   try:
    module = import_module(f'rims.devices.{info["type"]}')
    device = getattr(module,'Device',None)(aCTX, id, info['ip'])
    for ddp in device.get_data_points():
     ret['inserts'] += db.execute("INSERT INTO device_statistics (device_id,measurement,tags,name,oid) VALUES(%i,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = id"%(int(id),ddp[0],ddp[1],ddp[2],ddp[3]))
   except Exception as e:
    ret['status'] = 'NOT_OK'
    ret['info'] = str(e)
   else:
    ret['status'] = 'OK'
    ret['result'] = f'{ret["inserts"]} data points inserted'
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'device info not found'
 return ret

#################################### Monitor #################################
#
#
def check(aCTX, aArgs):
 """ Initiate a statistics check for all or a subset of devices' interfaces and extra data points

 Args:
  - networks (optional). List of subnet_ids to check
  - repeat (optional). value of seconds between repeated occurances of statistics gatering

 Output:
  - status
 """
 devices = []

 with aCTX.db as db:
  if db.query("SELECT id FROM ipam_networks" if 'networks' not in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks']))) and db.query("SELECT devices.id AS device_id, INET6_NTOA(ia.ip) AS ip, devices.hostname FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.network_id IN (%s) AND ia.state = 'up' AND devices.class IN ('infrastructure','vm','out-of-band') ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows()))):
   for dev in db.get_rows():
    if db.query("SELECT measurement,tags,name,oid FROM device_statistics WHERE device_id = %s AND oid IS NOT NULL"%dev['device_id']):
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
      dev['data_points'].extend([{'measurement':m,'tags':t,'values':values} for t,values in tags.items()])
    if db.query("SELECT snmp_index,interface_id,name FROM interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']):
     dev['interfaces'] = db.get_rows()
    if any(i in dev for i in ['data_points','interfaces']):
     devices.append(dev)

 if devices:
  if 'repeat' in aArgs:
   # INTERNAL from rims.api.statistics import process
   aCTX.schedule_api_periodic(process,'statistics_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debug)
   return {'status':'OK','function':'statistics_check','detach_frequency':aArgs['repeat']}
  else:
   # INTERNAL from rims.api.statistics import process
   return process(aCTX,{'devices':devices})
 else:
  return {'status':'OK','function':'statistics_check','info':'no devices'}

#
#
def process(aCTX, aArgs):
 """ Function processes a list of devices with datapoints and their interfaces

 Args:
  - devices (required), each device object has a list of interface objects and optionally data points objects

 Output:
 """
 from rims.devices.generic import Device
 nodes = [x['node'] for x in aCTX.services.values() if x['type'] == 'TSDB']
 report = aCTX.node_function(nodes[0],'statistics','report', aHeader= {'X-Log':'false'})
 ret = {'status':'OK','function':'statistics_process','reported':0}
 def __check_SP(aDev):
  try:
   device = Device(aCTX, aDev['device_id'], aDev['ip'])
   res = device.data_points(aDev.get('data_points',[]), aDev.get('interfaces',[]))
   if res['status'] == 'OK':
    report(aArgs = aDev)
    ret['reported'] += 1
   else:
    aCTX.log(f"statistics_process_collection_failed for device: {aDev['device_id']} => {res['info']}")
  except Exception as e:
   aCTX.log(f"statistics_process_report_failed for device: {aDev['device_id']} => {str(e)}")
   return False
  else:
   return True

 aCTX.queue_block(__check_SP,aArgs['devices'])
 return ret

#
#
def report(aCTX, aArgs):
 """Function updates statistics for a particular devices to influxdb - service must be running on this node.
 Line protocol uses nanosecond precision so we add 9 zeros for each write

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
  tmpl = 'interface,host_id={0},host_ip={1},if_id=%i,if_name=%s in8s=%iu,inUPs=%iu,out8s=%iu,outUPs=%iu {2}'.format(aArgs['device_id'],aArgs['ip'],ts)
  args.extend(tmpl%(x['interface_id'], x['name'][:20].replace(' ','\ '), x['in8s'], x['inUPs'], x['out8s'], x['outUPs']) for x in aArgs['interfaces'])
 if 'data_points' in aArgs:
  tmpl = '%s,host_id={0},host_ip={1},%s %s {2}'.format(aArgs['device_id'],aArgs['ip'],ts)
  args.extend(tmpl%(m['measurement'], m['tags'].replace(' ','\ '), ','.join('%s=%s'%(x['name'][:20].replace(' ','\ '), x['value']) for x in m['values'] if x['value'] ) ) for m in aArgs['data_points'] if any(x['value'] for x in m['values']) )
 try:
  with aCTX.influxdb_client.write_api(write_options=aCTX.influxdb_synchronous) as write_api:
   write_api.write(bucket='rims', write_precision = aCTX.influxdb_seconds, record = args)
 except Exception as e:
  ret['info'] = str(e)
  aCTX.log(f'statistics_report_tsdb_error: {str(e)}')
 else:
  ret['status'] = 'OK'
 return ret
