"""Module docstring.

The ESXi interworking module

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "hypervisor"
__icon__    = "../images/viz-server.png"
__oid__     = 6876

from generic import Device as GenericDevice

########################################### ESXi ############################################
#

class Device(GenericDevice):

 _vmstatemap  = { "1" : "powered on", "2" : "powered off", "3" : "suspended", "powered on" : "1", "powered off" : "2", "suspended" : "3" }

 @classmethod
 def get_state_str(cls,astate):
  return cls._vmstatemap[astate]

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self,aIP, aSettings):
  GenericDevice.__init__(self,aIP, aSettings)
  # Override log file
  def GL_get_host_name(aIP):
   from socket import gethostbyaddr
   try:    return gethostbyaddr(aIP)[0].partition('.')[0]
   except: return None

  self._sshclient = None
  self._hostname = GL_get_host_name(aIP)
  self._logfile = self._settings['esxi']['logformat'].format(self._hostname)

 def set_name(self, aHostname):
  self._hostname = aHostname
  self._logfile = self._settings['esxi']['logformat'].format(aHostname)

 def __enter__(self):
  if self.ssh_connect():
   return self
  else:
   raise RuntimeError("Error connecting to host")

 def __exit__(self, *ctx_info):
  self.ssh_close()

 def __str__(self):
  return self._hostname + " SSHConnected:" + str(self._sshclient != None)  + " statefile:" + self.statefile

 def log_msg(self, aMsg):
  from time import localtime, strftime
  output = unicode("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

 #
 # ESXi ssh interaction - Connect() send, send,.. Close()
 #
 def ssh_connect(self):
  if not self._sshclient:
   from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
   try:
    self._sshclient = SSHClient()
    self._sshclient.set_missing_host_key_policy(AutoAddPolicy())
    self._sshclient.connect(self._ip, username=self._settings['esxi']['username'], password=self._settings['esxi']['password'] )
   except AuthenticationException:
    self.log_msg("DEBUG: Authentication failed when connecting to %s" % self._ip)
    self._sshclient = None
    return False
  return True

 def ssh_send(self, aMessage):
  from select import select
  if self._sshclient:
   output = ""
   self.log_msg("ssh_send: [{}]".format(aMessage))
   stdin, stdout, stderr = self._sshclient.exec_command(aMessage)
   while not stdout.channel.exit_status_ready():
    if stdout.channel.recv_ready():
     rl, wl, xl = select([stdout.channel], [], [], 0.0)
     if len(rl) > 0:
      output = output + stdout.channel.recv(4096)
   return output.rstrip('\n')
  else:
   self.log_msg("Error: trying to send to closed channel")
   self._sshclient = None

 def ssh_close(self):
  if self._sshclient:
   try:
    self._sshclient.close()
    self._sshclient = None
   except Exception as err:
    self.log_msg( "Close error: " + str(err))

 #
 # SNMP interaction
 #
 def get_vm_id(self, aname):
  from netsnmp import VarList, Varbind, Session
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   for result in vmnameobjs:
    if result.val == aname:
     return int(result.iid)
  except:
   pass
  return -1

 def get_vm_state(self, aid):
  from netsnmp import VarList, Varbind, Session
  try:
   vmstateobj = VarList(Varbind(".1.3.6.1.4.1.6876.2.1.1.6." + str(aid)))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(vmstateobj)
   return vmstateobj[0].val
  except:
   pass
  return "unknown"

 def get_vm_list(self, aSort = None):
  # aSort = 'id' or 'name'
  from netsnmp import VarList, Varbind, Session
  statelist=[]
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   vmstateobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.6'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   session.walk(vmstateobjs)
   for indx,result in enumerate(vmnameobjs):
    statetuple = {'id':result.iid, 'name':result.val, 'state':vmstateobjs[indx].val ,'state_id':Device.get_state_str(vmstateobjs[indx].val)}
    statelist.append(statetuple)
  except:
   pass
  if aSort:
   statelist.sort(key = lambda x: x[aSort])
  return statelist
