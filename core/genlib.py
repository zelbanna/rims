"""Generic Library. Many are for reference, make them 'inline'"""
__author__ = "Zacharias El Banna"

##############################################################################

def debug_decorator(func_name):
 def decorator(func):
  def decorated(*args,**kwargs):
   res = func(*args,**kwargs)
   print(f'DEBUGGER: {func_name}({args},{kwargs}) => {res}')
   return res
  return decorated
 return decorator

################################### Generics ##################################

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
 from os import system
 return system(f'ping -c 1 -w 1 {aIP} > /dev/null 2>&1') == 0

def external_ip():
 from dns import resolver
 from socket import gethostbyname
 try:
  opendns  = resolver.Resolver()
  opendns.nameservers = [gethostbyname('resolver1.opendns.com')]
  res = str(opendns.query('myip.opendns.com','A').response.answer[0])
  return res.split()[4]
 except:
  return None

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
