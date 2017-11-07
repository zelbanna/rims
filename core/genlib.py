"""Module docstring.

Generic Library

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

################################# Generics ####################################

def get_host_name(aIP):
 from socket import gethostbyaddr
 try:    return gethostbyaddr(aIP)[0].partition('.')[0]
 except: return None

def ip2int(addr):
 from struct import unpack
 from socket import inet_aton
 return unpack("!I", inet_aton(addr))[0]

def int2ip(addr):
 from struct import pack
 from socket import inet_ntoa
 return inet_ntoa(pack("!I", addr))

def ips2range(addr1,addr2):
 from struct import pack, unpack
 from socket import inet_ntoa, inet_aton
 return map(lambda addr: inet_ntoa(pack("!I", addr)), range(unpack("!I", inet_aton(addr1))[0], unpack("!I", inet_aton(addr2))[0] + 1))

def ipint2range(start,end):
 from struct import pack
 from socket import inet_ntoa
 return map(lambda addr: inet_ntoa(pack("!I", addr)), range(start,end + 1))

def ip2ptr(addr):
 octets = addr.split('.')
 octets.reverse()
 return ".".join(octets) + ".in-addr.arpa"

def ip2arpa(addr):
 octets = addr.split('.')[:3]
 octets.reverse()
 return ".".join(octets) + ".in-addr.arpa"

def int2mac(aInt):
 return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()

def mac2int(aMAC):
 try:    return int(aMAC.replace(":",""),16)
 except: return 0

def ping_os(ip):
 from os import system
 return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0
