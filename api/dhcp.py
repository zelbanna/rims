"""FDB API module. This module provides FDB interaction with network devices"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs):
 """ Function retrieves dhcp allocated ip addresses

 Args:
  - server_id (required)
  - network_id (optional)

 Output:
  - data
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT di.id, ia.network_id, INET_NTOA(ia.ip) AS ip FROM dhcp_ipam AS di LEFT JOIN ipam_addresses AS ia ON di.id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ine.server_id = %s"%aArgs['server_id'])
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
 from rims.api.ipam import address_info
 from struct import pack, unpack
 from socket import inet_aton, inet_ntoa
 def GL_ip2int(addr):
  return unpack("!I", inet_aton(addr))[0]
 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 with aCTX.db as db:
  if aArgs.get('ip'):
   try: ipint = GL_ip2int(aArgs['ip'])
   except: ret = {'status':'NOT_OK','info':'Illegal IP'}
   else:
    ret = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':aArgs['network_id'], 'ip':aArgs['ip'], 'hostname':'dhcp-%i'%ipint, 'a_domain_id':aArgs.get('a_domain_id','NULL')})
    ret['dhcp'] = (db.do("INSERT INTO dhcp_ipam (id) VALUES (%s)"%ret['id']) > 0) if ret['status'] == 'OK' else False
  else:
   ret = {'status':'NOT_OK'}
   start = GL_ip2int(aArgs['start'])
   end = GL_ip2int(aArgs['end'])
   net = aArgs['network_id']
   dom = aArgs.get('a_domain_id','NULL')
   if (db.do("SELECT network FROM ipam_networks WHERE id = %s AND %i > network AND %i < (network + POW(2,(32-mask))-1)"%(net,start,end)) == 1):
    if (db.do("SELECT id, INET_NTOA(ip) AS ip FROM ipam_addresses WHERE network_id = %s AND %i <= ip AND ip <= %i"%(net,start,end)) > 0):
     ret['info'] = 'Occupied range'
     ret['data'] = db.get_rows()
    else:
     ret['status'] = 'OK'
     ret['dhcp'] = True
     for ipint in range(start, end+1):
      res = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':net, 'ip':GL_int2ip(ipint), 'hostname':'dhcp-%i'%ipint, 'a_domain_id':dom})
      if not (res['status'] == 'OK' and (db.do("INSERT INTO dhcp_ipam (id) VALUES (%s)"%res['id']) > 0)):
        ret['dhcp'] = False
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
