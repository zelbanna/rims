"""DHCP API module. This module provides DHCP allocation functionality, ATM only for IPv4"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs):
 """ Function retrieves dhcp allocated ip addresses for either server_id or network_id

 Args:
  - server_id (optional)
  - network_id (optional)

 Output:
  - data
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('network_id'):
   ret['count'] = db.query("SELECT di.id, INET6_NTOA(ia.ip) AS ip FROM dhcp_ipam AS di LEFT JOIN ipam_addresses AS ia ON di.id = ia.id WHERE ia.network_id = %s ORDER BY ia.ip"%aArgs['network_id'])
  else:
   ret['count'] = db.query("SELECT di.id, INET6_NTOA(ia.ip) AS ip, ia.network_id, INET6_NTOA(ine.network) AS network FROM dhcp_ipam AS di LEFT JOIN ipam_addresses AS ia ON di.id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ine.server_id = %s AND IS_IPV4(INET6_NTOA(ine.network)) ORDER BY ia.ip"%aArgs['server_id'])
  ret['data'] = db.get_rows()
 return ret

#
#
def new(aCTX, aArgs):
 """ Function inserts a new dhcp address (ip) or scope of addresses (start => end)

 aArgs:
  - network_id (required)
  - ip (optional)
  - start (optional)
  - end (optional)
  - a_domain_id (optional)

 Output:
 """
 from ipaddress import ip_address
 from rims.api.ipam import address_info

 with aCTX.db as db:
  if aArgs.get('ip'):
   try: ip = ip_address(aArgs['ip'])
   except: ret = {'status':'NOT_OK','info':'Illegal IP'}
   else:
    ret = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':aArgs['network_id'], 'ip':str(ip), 'hostname':'dhcp-%i'%int(ip), 'a_domain_id':aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL'})
    ret['dhcp'] = (db.execute("INSERT INTO dhcp_ipam (id) VALUES (%s)"%ret['id']) > 0) if ret['status'] == 'OK' else False
  else:
   ret = {'status':'NOT_OK'}
   net = aArgs['network_id']
   dom = aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL'
   # v4 DHCP
   if (db.query("SELECT ine.network FROM ipam_networks AS ine WHERE ine.id = %s AND INET6_ATON('%s') >= ine.network AND INET6_ATON('%s') <= ine.broadcast"%(net,aArgs['start'],aArgs['end'])) == 1):
    if (db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE ia.network_id = %s AND INET6_ATON('%s') <= ia.ip AND ia.ip <= INET6_ATON('%s')"%(net,aArgs['start'],aArgs['end'])) > 0):
     ret['info'] = 'Occupied range'
     ret['data'] = db.get_rows()
    else:
     ret['status'] = 'OK'
     ret['dhcp'] = True
     ip = ip_address(aArgs['start'])
     end = ip_address(aArgs['end'])
     while ip <= end:
      res = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':net, 'ip':str(ip), 'hostname':'dhcp-%i'%int(ip), 'a_domain_id':dom})
      if not (res['status'] == 'OK' and (db.execute("INSERT INTO dhcp_ipam (id) VALUES (%s)"%res['id']) > 0)):
        ret['dhcp'] = False
      ip = ip + 1
   else:
    ret['info'] = 'IP not in network range'
 return ret

#
#
def delete(aCTX, aArgs):
 """ Function deletes a dhcp address (id)

 Args:
  - id (optional)

 Output:
 """
 # Since DB constraints will delete DHCP entry with IPAM entry this is really a No OP
 from rims.api.ipam import address_delete
 return address_delete(aCTX, {'id':aArgs['id']})
