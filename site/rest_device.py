"""Module docstring.

 Device restAPI module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__ = "Production"

#
# Dump 2 JSON              
#
def dump_db(aDict):
 import sdcp.core.GenLib as GL
 db = GL.DB()
 db.connect()
 res = db.do("SELECT * FROM devices")
 db.close()
 if res > 0:
  return db.get_all_rows()
 else:
  return []

#
# new
#
def new(aDict):
 # args = { 'ip':ip, 'mac':mac, 'hostname':hostname, 'dns_a_dom_id':a_dom, 'dns_ptr_dom_id':ptr_dom, 'ipam_dom_id':ipam_dom }
 res = "Nothing to be done"
 if not (ip == '127.0.0.1' or hostname == 'unknown'):
  ipint = sys_ip2int(ip)
  db = DB()
  db.connect()
  # 
  # Check ipam_dom as well
  #
  xist = db.do("SELECT id,hostname, dns_a_dom_id, dns_a_ptr_id, ipam_dom_id FROM devices WHERE ip ='{}'".format(ipint))
  if xist == 0:
   mac = mac.replace(":","")
   if not sys_is_mac(mac):
    mac = "000000000000"
   # dbres = db.do("INSERT INTO devices (ip,mac,domain_id,domain,hostname,snmp,model,type,fqdn,rack_size) VALUES({},x'{}',{},'unknown','unknown','unknown','unknown','unknown'$
   # db.commit()
   res = "Added ({})".format(dbres)
  else:
   xist = db.get_row()
   res = "Existing ({}.{} - {})".format(xist['hostname'],xist['dns_a_dom_id'],xist['id'])
  db.close()
 from json import dumps
 print dumps(res)
