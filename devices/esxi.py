"""The ESXi interworking module"""
__author__  = "Zacharias El Banna"
__type__    = "hypervisor"
__icon__    = "viz-server.png"
__oid__     = 6876

from rims.devices.generic import Device as GenericDevice
from rims.core.common import VarList, Session

########################################### ESXi ############################################
#
# TODO: put a session object in the Context cache for esxi and self._id, reuse this to start pyVmomi migration
#
class Device(GenericDevice):

 @classmethod
 def get_state_str(cls,aState):
  return { "powered on":"on", "powered off":"off","suspended":"suspended" }.get(aState)

 @classmethod
 def get_functions(cls):
  return ['manage']

 def __init__(self, aCTX, aID, aIP = None):
  GenericDevice.__init__(self, aCTX, aID, aIP)
  self._sshclient = None
  #cache = aCTX.cache.get('esxi',{})
  #if not cache:
  # aCTX['esxi'] = cache
  #dev = cache.get(aID,{})
  #if not dev:
  # cache[aID] = dev
  #self._cache = dev

 def __enter__(self):
  if not self._sshclient:
   from paramiko import SSHClient, AutoAddPolicy, AuthenticationException
   try:
    self._sshclient = SSHClient()
    self._sshclient.set_missing_host_key_policy(AutoAddPolicy())
    self._sshclient.connect(self._ip, username=self._ctx.config['esxi']['username'], password=self._ctx.config['esxi']['password'] )
   except AuthenticationException:
    self.log("DEBUG: Authentication failed when connecting")
    self._sshclient = None
    raise RuntimeError("ESXi_Error connecting to host")
   except NoValidConnections as e:
    self.log("DEBUG: Could not connect")
    self._sshclient = None
    raise RuntimeError("ESXi_Error connecting to host")

  return self

 def __exit__(self, *ctx_info):
  if self._sshclient:
   try:
    self._sshclient.close()
    self._sshclient = None
   except Exception as err:
    self.log( "ERROR: %s"%(err))

 def __str__(self):
  return "ESXi(ip = %s, connected=%s)"%(self._ip,(self._sshclient != None))

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

 ####################################### Commands ####################################
 #
 # SSH interaction - Connect() send, send,.. Close()
 #

 def _command(self, aMessage):
  from select import select
  if self._sshclient:
   output = ""
   #self.log("ssh_send: [{}]".format(aMessage))
   stdin, stdout, stderr = self._sshclient.exec_command(aMessage)
   while not stdout.channel.exit_status_ready():
    if stdout.channel.recv_ready():
     rl, wl, xl = select([stdout.channel], [], [], 0.0)
     if len(rl) > 0:
      output = output + stdout.channel.recv(4096).decode()
   return output.rstrip('\n')
  else:
   self.log("ERROR: trying to send to closed channel")
   self._sshclient = None

 #
 def operation(self, aType):
  self.log("Host operation - %s"%aType)
  if aType == 'shutdown':
   return 'HOST_NOT_SHUTTING_DOWN'
   # self._command("poweroff")
  return 'OPERATION_NOT_IMPLEMENTED_%s'%aType.upper()

 #
 # TODO: Convert to pyVmomi
 # 
 def vm_operation(self, aOP, aID, aUUID = None, aSnapshot = None):
  """Function vm_operation ... operates on VMs

  Args:
   - aID => VM ID
   - aOP => 'create/revert/remove' (for snapshots on VM id's), 'hostoff' (for host), 'on/off/reboot/shutdown/suspend' (for VM id's)
   - aUUID => (optional) test against UUID in case SNMP ID/VM ID is not correct anymore
   - aSnapshot => (optional). For snapshot removal, remove snapshot with id aSnapshot

  Output:
   - id => VM ID
   - status => 'OK'/<error_code>
   - state_id => state_id
   - state => textual rep of current state
  """
  ret = {'id':aID,'status':'OK'}
  try:
   if aUUID:
    session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
    uuidobj = VarList('.1.3.6.1.4.1.6876.2.1.1.10.%s'%aID)
    session.get(uuidobj)
    if uuidobj[0].val.decode() !=  aUUID:
     raise Exception('UUID_NOT_MATCHING')
   if aOP in ['on','off','reboot','shutdown','suspend']:
    from time import sleep
    self._command("vim-cmd vmsvc/power.%s %s"%(aOP,aID))
    sleep(5)
   ret.update(self.get_vm_state(aID))
   self.log("VM operation [%s] executed on %s, state:%s"%(aOP,aID,ret.get('state','unknown')))
  except Exception as err:
   ret['status'] = 'NOT_OK'
   ret['info'] = repr(err)
   self.log("VM operation [%s] failed on %s => %s"%(aOP,aID,ret['info']))
  return ret

 #
 # TODO: Convert to pyVmomi
 #
 def snapshot(self, aOP, aID, aSnapshot):
  ret = {'status':'OK'}
  if aOP == 'list':
   snapshots = self._command("vim-cmd vmsvc/snapshot.get %s"%aID)
   ret['data'] = []
   ret['highest'] = 0
   data = {'id':None,'name':None,'desc':None,'created':None,'state':None}
   for field in snapshots.splitlines():
    if "Snapshot" in field:
     parts = field.partition(':')
     key = parts[0].strip()
     val = parts[2].strip()
     if key[-4:] == 'Name':
      data['name'] = val
     elif key[-10:] == 'Desciption':
      data['desc'] = val
     elif key[-10:] == 'Created On':
      data['created'] = val
     elif key[-2:] == 'Id':
      data['id'] = val
      if int(val) > ret['highest']:
       ret['highest'] = int(val)
     elif key[-5:] == 'State':
      # Last!
      data['state'] = val
      ret['data'].append(data)
      data = {'id':None,'name':None,'desc':None,'created':None,'state':None}
  elif aOP == 'create':
   from time import strftime
   self._command("vim-cmd vmsvc/snapshot.create %s 'Portal Snapshot' '%s'"%(aID,strftime("%Y%m%d")))
  elif aOP == 'revert':
   self._command("vim-cmd vmsvc/snapshot.revert %s %s suppressPowerOff"%(aID,aSnapshot))
  elif aOP == 'remove':
   self._command("vim-cmd vmsvc/snapshot.remove %s %s"%(aID,aSnapshot))
   ret['deleted'] = True
  ret.update(self.get_vm_state(aID))
  self.log("VM snapshot [%s] on %s"%(aOP,aID))
  return ret

 ############################################# SNMP ###########################################
 #
 # SNMP interaction, feels quicker than the VMomi stuff...
 #
 def get_info(self, aID):
  vm = {'interfaces':{},'vm':None}
  try:
   # Name, Config file, State, Device UUID (ISO 11578)
   vmobj = VarList('.1.3.6.1.4.1.6876.2.1.1.2.%s'%aID,'.1.3.6.1.4.1.6876.2.1.1.3.%s'%aID,'.1.3.6.1.4.1.6876.2.1.1.6.%s'%aID,'.1.3.6.1.4.1.6876.2.1.1.10.%s'%aID)
   # Name, portgroup, MAC
   vminterfaces = VarList('.1.3.6.1.4.1.6876.2.4.1.3.%s'%aID,'.1.3.6.1.4.1.6876.2.4.1.4.%s'%aID,'.1.3.6.1.4.1.6876.2.4.1.7.%s'%aID)
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.get(vmobj)
   session.walk(vminterfaces)
   vm = {'name':vmobj[0].val.decode(),'config':vmobj[1].val.decode(),'state':Device.get_state_str(vmobj[2].val.decode()),'bios_uuid':vmobj[3].val.decode(),'interfaces':{}}
   for obj in vminterfaces:
    tag,_,_ = obj.tag.rpartition('.')
    if   tag == '.1.3.6.1.4.1.6876.2.4.1.3':
     vm['interfaces'][obj.iid] = {'name':obj.val.decode()}
    elif tag == '.1.3.6.1.4.1.6876.2.4.1.4':
     vm['interfaces'][obj.iid]['port'] = obj.val.decode()
    elif tag == '.1.3.6.1.4.1.6876.2.4.1.7':
     vm['interfaces'][obj.iid]['mac'] = ':'.join(obj.val.hex()[i:i+2] for i in [0,2,4,6,8,10]).upper()
  except: pass
  return vm

 #
 #
 def get_vm_state(self, aID):
  ret = {}
  try:
   vmstateobj = VarList('.1.3.6.1.4.1.6876.2.1.1.6.%s'%aID)
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.get(vmstateobj)
   ret['state'] = Device.get_state_str(vmstateobj[0].val.decode())
  except:
   ret['state'] = 'unknown'
  return ret

 #
 #
 def get_vm_list(self, aSort = None):
  # aSort = 'id' or 'name'
  statelist=[]
  try:
   vmnameobjs = VarList('.1.3.6.1.4.1.6876.2.1.1.2')
   vmstateobjs = VarList('.1.3.6.1.4.1.6876.2.1.1.6')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(vmnameobjs)
   session.walk(vmstateobjs)
   for indx,result in enumerate(vmnameobjs):
    statelist.append({'id':result.iid, 'name':result.val.decode(),'state':Device.get_state_str(vmstateobjs[indx].val.decode())})
  except: pass
  if aSort:
   statelist.sort(key = lambda x: x[aSort])
  return statelist

 #
 def get_inventory(self):
  vms = {}
  try:
   # Name, Config file, Device UUID (ISO 11578)
   vmobjs = VarList('.1.3.6.1.4.1.6876.2.1.1.2','.1.3.6.1.4.1.6876.2.1.1.3','.1.3.6.1.4.1.6876.2.1.1.10')
   # Name, portgroup, MAC (not ':'-expanded)
   vminterfaces = VarList('.1.3.6.1.4.1.6876.2.4.1.3','.1.3.6.1.4.1.6876.2.4.1.4','.1.3.6.1.4.1.6876.2.4.1.7')
   session = Session(Version = 2, DestHost = self._ip, Community = self._ctx.config['snmp']['read'], UseNumeric = 1, Timeout = int(self._ctx.config['snmp'].get('timeout',100000)), Retries = 2)
   session.walk(vmobjs)
   session.walk(vminterfaces)
   for obj in vmobjs:
    if   obj.tag == '.1.3.6.1.4.1.6876.2.1.1.2':
     vms[obj.iid] = {'interfaces':{},'vm':obj.val.decode()}
    elif obj.tag == '.1.3.6.1.4.1.6876.2.1.1.3':
     vms[obj.iid]['config'] = obj.val.decode()
    elif obj.tag == '.1.3.6.1.4.1.6876.2.1.1.10':
     vms[obj.iid]['bios_uuid'] = obj.val.decode()
   for obj in vminterfaces:
    tag,_,iid = obj.tag.rpartition('.')
    if   tag == '.1.3.6.1.4.1.6876.2.4.1.3':
     vms[iid]['interfaces'][obj.iid] = {'name':obj.val.decode()}
    elif tag == '.1.3.6.1.4.1.6876.2.4.1.4':
     vms[iid]['interfaces'][obj.iid]['port'] = obj.val.decode()
    elif tag == '.1.3.6.1.4.1.6876.2.4.1.7':
     vms[iid]['interfaces'][obj.iid]['mac'] = ("%s"%obj.val.hex()).upper()
  except: pass
  return vms
