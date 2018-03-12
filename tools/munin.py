"""Module docstring.

Module for graph interaction

Exports:
- discover
- widget_cols
- widget_rows

"""  
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"

def _print_graph_link(asource, aX = "399", aY = "224"):
 from time import time
 stop  = int(time())-300
 start = stop - 24*3600 
 print "<A TARGET=main_cont HREF='munin-cgi/munin-cgi-html/static/dynazoom.html?"
 print "cgiurl_graph=/munin-cgi/munin-cgi-graph&plugin_name={0}&size_x=800&size_y=400&start_epoch={1}&stop_epoch={2}'>".format(asource,str(start),str(stop))
 print "<IMG width={0} height={1} ALT='munin graph:{2}' SRC='/munin-cgi/munin-cgi-graph/{2}-day.png' /></A>".format(aX, aY, asource)

def widget_cols(asources):
 lwidth = 3 if len(asources) < 3 else len(asources)
 print "<DIV STYLE='padding:5px; width:{}px; height:240px; float:left;'>".format(str(lwidth * 410))
 for src in asources:
  _print_graph_link(src)
 print "</DIV>"

def widget_rows(asources):
 lheight = 3 if len(asources) < 3 else len(asources)
 print "<DIV STYLE='padding-top:10px; padding-left:5px; width:420px; height:{}px; float:left;'>".format(str(lheight * 230))
 for src in asources:         
  _print_graph_link(src)      
 print "</DIV>"

#############################################################################

#
# Writes plugin info for devices found with DeviceHandler
#
def discover():
 from ..core.logger import log
 from ..core.common import DB
 from os import chmod
 from time import time
 from threading import Lock, Thread, BoundedSemaphore

 def _detect(aentry, alock, asema,aplugfile):
  def GL_ping_os(ip):
   from os import system
   return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0

  if not GL_ping_os(aentry['ip']):
   asema.release()
   return False

  activeinterfaces = []
  type = aentry['type_name']
  fqdn = aentry['hostname'] + "." + aentry['domain']
  try:
   if type in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
    from ..devices.junos import Junos
    if not type == 'wlc':
     with Junos(aentry['ip']) as jdev:
      activeinterfaces = jdev.get_up_interfaces()
    alock.acquire()
    with open(aplugfile, 'a') as graphfile:
     graphfile.write('ln -s /usr/local/sbin/plugins/snmp__{0} /etc/munin/plugins/snmp_{1}_{0}\n'.format(type,fqdn))
     graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + fqdn + '_uptime\n')
     graphfile.write('ln -s /usr/share/munin/plugins/snmp__users  /etc/munin/plugins/snmp_' + fqdn + '_users\n')
     for ifd in activeinterfaces:
      graphfile.write('ln -s /usr/share/munin/plugins/snmp__if_    /etc/munin/plugins/snmp_' + fqdn + '_if_'+ ifd['SNMP'] +'\n')
    alock.release()
   elif type == "esxi":
    alock.acquire()
    with open(aplugfile, 'a') as graphfile:
     graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + fqdn + '_uptime\n')              
     graphfile.write('ln -s /usr/local/sbin/plugins/snmp__esxi    /etc/munin/plugins/snmp_' + fqdn + '_esxi\n')
    alock.release()
  except Exception as err:
   from ..core.logger import log
   log("Graph detect - error: [{}]".format(str(err)))

  asema.release()
  return True

 start_time = int(time())
 with DB() as db:
  db.do("SELECT value FROM settings WHERE parameter = 'plugins'")
  plug_file = db.get_val('value')
  db.do("SELECT devicetypes.name, hostname, domains.name AS domain, INET_NTOA(ip) as ip, INET_NTOA(graph_proxy) as handler FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id INNER JOIN domains ON devices.a_dom_id = domains.id WHERE graph_update = 1 AND model <> 'unknown'")
  devices = db.get_rows()
 try:
  flock = Lock()
  sema  = BoundedSemaphore(10)
  with open(plug_file, 'w') as f:
   f.write("#!/bin/bash\n")
  chmod(plug_file, 0o777)
  for item in devices:
   sema.acquire()
   t = Thread(target = _detect, args=[item, flock, sema, plug_file])
   t.start()
  for i in range(10):
   sema.acquire()       
 except Exception as err:
  log("Munin: failure in processing Device entries: [{}]".format(str(err)))
 log("Munin: Total time spent: {} seconds".format(int(time()) - start_time))
 return True
