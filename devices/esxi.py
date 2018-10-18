"""The ESXi interworking module"""
__author__  = "Zacharias El Banna"
__type__    = "hypervisor"
__icon__    = "../images/viz-server.png"
__oid__     = 6876

from .generic import Device as GenericDevice
from zdcp.core.common import VarList, Varbind, Session

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

 def __init__(self,aIP, aSettings, aHostname = None):
  GenericDevice.__init__(self,aIP, aSettings)
  self._sshclient = None
  self._hostname  =  aHostname if aHostname else self._ip
  self._logfile   = self._settings['esxi'].get('logformat',self._settings['logs']['system']).format(self._hostname)

 def __enter__(self):
  if self.ssh_connect():
   return self
  else:
   raise RuntimeError("ESXi_Error connecting to host")

 def __exit__(self, *ctx_info):
  self.ssh_close()

 def __str__(self):
  return self._hostname + " SSHConnected:" + str(self._sshclient != None)

 def log_msg(self, aMsg):
  from time import localtime, strftime
  output = str("{} : {}".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg))
  with open(self._logfile, 'a') as f:
   f.write(output + "\n")

 def interfaces(self):
  interfaces = super(Device,self).interfaces()
  for k,v in interfaces.items():
   parts = v['name'].split()
   if parts[0] == 'Device':
    v['name'] = parts[1]
   elif parts[0] == 'Link':
    v['name'] = parts[2]
   elif parts[0] == 'Virtual':
    v['name'] = parts[2]
   elif parts[0] == 'Traditional':
    v['name'] = parts[4]
   else:
    v['name']= v['name'][0:25]
   v['description'] = v['description'][0:25]
  return interfaces


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
    self.log_msg("ESXi_DEBUG: Authentication failed when connecting")
    self._sshclient = None
    return False
  return True

 def ssh_send(self, aMessage):
  from select import select
  if self._sshclient:
   output = ""
   self.log_msg("ESXi_ssh_send: [{}]".format(aMessage))
   stdin, stdout, stderr = self._sshclient.exec_command(aMessage)
   while not stdout.channel.exit_status_ready():
    if stdout.channel.recv_ready():
     rl, wl, xl = select([stdout.channel], [], [], 0.0)
     if len(rl) > 0:
      output = output + stdout.channel.recv(4096).decode()
   return output.rstrip('\n')
  else:
   self.log_msg("ESXi_Error: trying to send to closed channel")
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
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   for result in vmnameobjs:
    if result.val.decode() == aname:
     return int(result.iid)
  except: pass
  return -1

 def get_vm_state(self, aid):
  try:
   vmstateobj = VarList(Varbind(".1.3.6.1.4.1.6876.2.1.1.6." + str(aid)))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(vmstateobj)
   return vmstateobj[0].val.decode()
  except: pass
  return "unknown"

 def get_vm_list(self, aSort = None):
  # aSort = 'id' or 'name'
  statelist=[]
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   vmstateobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.6'))
   session = Session(Version = 2, DestHost = self._ip, Community = self._settings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   session.walk(vmstateobjs)
   for indx,result in enumerate(vmnameobjs):
    statetuple = {'id':result.iid, 'name':result.val.decode(), 'state':vmstateobjs[indx].val.decode() ,'state_id':Device.get_state_str(vmstateobjs[indx].val.decode())}
    statelist.append(statetuple)
  except: pass
  if aSort:
   statelist.sort(key = lambda x: x[aSort])
  return statelist
