"""Module docstring.

The ESXi interworking module

"""
__author__  = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__  = "Production"
__type__    = "hypervisor"

from sdcp import PackageContainer as PC
from generic import Device as GenericDevice

########################################### ESXi ############################################
#

class Device(GenericDevice):

 _vmstatemap  = { "1" : "powered on", "2" : "powered off", "3" : "suspended", "powered on" : "1", "powered off" : "2", "suspended" : "3" }

 @classmethod
 def get_state_str(cls,astate):
  return cls._vmstatemap[astate]

 @classmethod
 def get_widgets(cls):
  return ['manage']

 def __init__(self,aIP,aID=None):
  GenericDevice.__init__(self,aIP,aID)
  from sdcp.core import genlib as GL
  # Override log file
  self._hostname = GL.get_host_name(aIP)
  self._logfile = PC.esxi['logformat'].format(self._hostname)
  self._sshclient = None
  self.statefile = PC.esxi['shutdownfile'].format(self._hostname) 

 def set_name(self, aHostname):
  self._hostname = aHostname
  self._logfile = PC.esxi['logformat'].format(aHostname)
  self.statefile = PC.esxi['shutdownfile'].format(aHostname) 

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
 
 def create_lock(self,atime):
  from sdcp.core.extras import pidfile_lock
  pidfile_lock("/tmp/esxi." + self._hostname + ".vm.pid",atime)

 def release_lock(self):
  from sdcp.core.extras import pidfile_release
  pidfile_release("/tmp/esxi." + self._hostname + ".vm.pid")

 #
 # ESXi ssh interaction - Connect() send, send,.. Close()
 #
 def ssh_connect(self):
  if not self._sshclient:
   from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
   try:
    self._sshclient = SSHClient()
    self._sshclient.set_missing_host_key_policy(AutoAddPolicy())
    self._sshclient.connect(self._ip, username=PC.esxi['username'], password=PC.esxi['password'] )
   except AuthenticationException:
    self.log_msg("DEBUG: Authentication failed when connecting to %s" % self._ip)
    self._sshclient = None
    return False
  return True

 def ssh_send(self, aMessage, aID=None):
  from select import select
  if self._sshclient:
   output = ""
   self.log_msg("ssh_send ({}): [{}]".format(aID,aMessage))
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

 def get_id_vm(self, aname):
  from netsnmp import VarList, Varbind, Session
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   for result in vmnameobjs:
    if result.val == aname:
     return int(result.iid)
  except:
   pass
  return -1
 
 def get_state_vm(self, aid):
  from netsnmp import VarList, Varbind, Session
  try:
   vmstateobj = VarList(Varbind(".1.3.6.1.4.1.6876.2.1.1.6." + str(aid)))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(vmstateobj)
   return Device.get_state_str(vmstateobj[0].val)
  except:
   pass
  return "unknown"

 def get_vms(self, aSort = None):
  #
  # Returns a list with tuples of strings: [ vm.id, vm.name, vm.powerstate, vm.to_be_backedup ]
  #
  # aSort = 'id' or 'name'
  from netsnmp import VarList, Varbind, Session
  statelist=[]
  try:
   vmnameobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.2'))
   vmstateobjs = VarList(Varbind('.1.3.6.1.4.1.6876.2.1.1.6'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(vmnameobjs)
   session.walk(vmstateobjs)
   for index,result in enumerate(vmnameobjs):
    statetuple = [result.iid, result.val, Device.get_state_str(vmstateobjs[index].val)]
    statelist.append(statetuple)
  except:
   pass
  if aSort == 'name':
   statelist.sort(key = lambda x: x[1])
  return statelist

 #
 # Shutdown methods to/from default statefile
 #
 #

 def startup_vms(self):
  from os import remove, path
  from time import sleep
  # Power up everything in the statefile
  if not path.isfile(self.statefile):
   self.log_msg("startup_vms: Has no reason to run powerUp as no VMs were shutdown..")
   return False
  
  self.create_lock(2)
  self.ssh_connect()

  statefilefd = open(self.statefile)
  for line in statefilefd:
   if line == "---------\n":
    self.log_msg("startup_vms: Powerup - MARK found, wait a while for dependent")
    sleep(60)
   else:
    vm = line.strip('\n').split(',')
    if vm[2] == "1":
     self.ssh_send("vim-cmd vmsvc/power.on " + vm[0])
  remove(sfile)
  self.ssh_close()
  self.release_lock()
  return True

 def shutdown_vms(self, aExceptlist):
  from os import remove, path
  from time import sleep
  # Power down everything and save to the statefile, APCupsd statemachine:
  #
  # 1) apcupsd calls event triggering shutdown (runlimit, timelimit)
  # 2.1) apcupsd calls doshutdown
  # 2.2) apcupsd writes /etc/apcupsd/powerfail   <<--- This triggers everything
  #
  # X) Remove doshutdown's shutdown request within apccontrol
  # X) Create a doshutdown which simply calls /usr/local/sbin/esxi-shutdown.py <esxi-host> for all esxi-hosts
  # X) Add  to  doshutdown a `shutdown -h 10`
  #
  # 3) any call to shutdown -h x will call /etc/init.d/halt within x seconds - THIS WILL TRIGGER CONTROLLED SHUTDOWN OF EVERYTHING
  # 4) /etc/init.d/halt will call /etc/apcupsd/ups-monitor
  # 5) ups-monitor checks for powerfail file and calls /etc/apcupsd/apccontrol (again) with killpower
  # 6) apccontrol killpower -> /sbin/apcupsd killpower
  # 7) UPS is signaled and start shutdown sequence ( awaiting new power feed )
  if path.isfile(self.statefile):
   self.log_msg("shutdown_vms: Shutdown all VMs VMs are already shutdown! exit")
   return False

  deplist=[]
  freelist=[]
  self.create_lock(2)

  try:
   vmlist = self.getVMs()
   self.ssh_connect()
   # Start go through all vms
   #
   for vm in vmlist:
    # Only interested in active VMs
    if vm[2] == "1":
     if vm[1].startswith("svc-nas"):
      deplist.append(vm)
     elif vm[1] not in aExceptlist:
      freelist.append(vm)
      self.ssh_send("vim-cmd vmsvc/power.shutdown " + vm[0])

   # Write statelog
   #
   statefilefd = open(self.statefile,'w')
   for vm in deplist:
    statefilefd.write(vm[0]+','+ vm[1] + ',' + vm[2] +"\n")
   statefilefd.write("---------\n")
   for vm in freelist:
    statefilefd.write(vm[0]+','+ vm[1] + ',' + vm[2] +"\n")
   statefilefd.close()
 
   # Shutdown VMs that has a dependence
   #
   sleep(20)
   for vm in deplist:
    self.ssh_send("vim-cmd vmsvc/power.shutdown " + vm[0])

   # Powering off machines that doesn't respond too well to guest shutdowns
   #
   sleep(60)
   vmlist = self.get_vms()
   for vm in vmlist:
    if vm[2] == "1":
     if vm[1].startswith("svc-nas"):
      self.log_msg("shutdown_vms: Shutdown of NAS vm not completed..")
     elif vm[1].startswith("pulse"):
      self.ssh_send("vim-cmd vmsvc/power.off " + vm[0])
      self.log_msg("shutdown_vms: powering off machine: {}!".format(vm[0]))
     elif vm[1] not in aExceptlist:
      # Correct? or pass?
      self.ssh_send("vim-cmd vmsvc/power.suspend " + vm[0])
      self.log_msg("shutdown_vms: suspending machine: {}!".format(vm[0]))

   # Done, finish off local machine
   #
   self.ssh_close()
   self.release_lock()
   self.log_msg("shutdown_vms: Done! Ready for powerloss, awaiting system halt")
  except Exception as vmerror:
   self.log_msg("ERROR: " + str(vmerror))
