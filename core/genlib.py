"""Generic Library. Many are for reference, make them 'inline'"""
__author__ = "Zacharias El Banna"

from sys import stderr
##############################################################################

def debug_decorator(func_name):
 def decorator(func):
  def decorated(*args,**kwargs):
   res = func(*args,**kwargs)
   stderr.write(f'DEBUGGER: {func_name}({args},{kwargs}) => {res}\n')
   return res
  return decorated
 return decorator

################################### Generics ##################################

def mac_bin_to_hex(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(*octets)

def mac_bin_to_int(inc_bin_mac_address):
  octets = [ord(c) for c in inc_bin_mac_address]
  return int("{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}".format(*octets),16)


def random_string(aLength):
 import string
 import random
 return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(aLength))

def get_host_name(aIP):
 from socket import gethostbyaddr
 try:
  return gethostbyaddr(aIP)[0].partition('.')[0]
 except:
  return None

def v4ToInt(addr):
 from struct import unpack
 from socket import inet_aton
 return unpack('!I', inet_aton(addr))[0]

def intToV4(addr):
 from struct import pack
 from socket import inet_ntoa
 return inet_ntoa(pack('!I', addr))

def v4ToPtr(addr):
 octets = addr.split('.')
 octets.reverse()
 octets.append('in-addr.arpa')
 return '.'.join(octets)

def v4ToArpa(addr):
 octets = addr.split('.')[:3]
 octets.reverse()
 octets.append('in-addr.arpa')
 return '.'.join(octets)

def intToMac(aInt):
 return ':'.join('%s%s'%x for x in zip(*[iter('{:012x}'.format(aInt))]*2))

def macToInt(aMAC):
 try:
  return int(aMAC.replace(':',''),16)
 except:
  return 0

def ping_os(aIP):
 from subprocess import run, DEVNULL
 res = run(['ping','-c','1','-w','1',aIP], stdout=DEVNULL)
 return res.returncode == 0

def get_quote(aString):
 from urllib.parse import quote_plus
 return quote_plus(aString)

def strToHex(arg):
 try:
  return '0x{0:02x}'.format(int(arg))
 except:
  return '0x00'

def file_replace(afile,old,new):
 if afile == '' or new == '' or old == '':
  return False
 with open(afile, 'r') as f:
  filedata = f.read()
 filedata = filedata.replace(old,new)
 with open(afile, 'w') as f:
  f.write(filedata)
 return True
