"""Module docstring.

Generic Library

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

############################################ Database ######################################
#
# Database Class
#
class DB(object):

 def __init__(self):
  self._conn = None
  self._curs = None

 def connect(self):
  import sdcp.SettingsContainer as SC
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host='localhost', port=3306, user=SC.sdcp_dbuser, passwd=SC.sdcp_dbpass, db=SC.sdcp_db, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 def connect_details(self, aHost, aUser, aPass, aDB):
  from pymysql import connect
  from pymysql.cursors import DictCursor
  self._conn = connect(host=aHost, port=3306, user=aUser, passwd=aPass, db=aDB, cursorclass=DictCursor)
  self._curs = self._conn.cursor()

 def do(self,aStr):
  return self._curs.execute(aStr)

 def commit(self):
  self._conn.commit()

 def get_row(self):
  return self._curs.fetchone()

 # Bug in fetchall, a tuple is not an empty list in contrary to func spec
 def get_all_rows(self):
  rows = self._curs.fetchall()
  return rows if rows != () else []

 def get_all_dict(self, aTarget):
  return dict(map(lambda x: (x[aTarget],x),self._curs.fetchall()))

 def get_cursor(self):
  return self._curs

 def get_last_id(self):
  return self._curs.lastrowid

 def close(self):
  self._curs.close()
  self._conn.close()

################################# Generics ####################################

def get_host(ahost):
 from socket import gethostbyname
 try:
  return gethostbyname(ahost)
 except:
  return None

def is_ip(addr):
 from socket import inet_aton
 try:
  inet_aton(addr)
  return True
 except:
  return False

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
 try:
  return int(aMAC.replace(":",""),16)
 except:
  return 0

def is_mac(aMAC):           
 try:
  aMAC = aMAC.replace(":","")
  return len(aMAC) == 12 and int(aMAC,16)
 except:         
  return False

def ping_os(ip):
 from os import system
 return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0

def log_msg(amsg):
 import sdcp.SettingsContainer as SC
 from time import localtime, strftime
 with open(SC.sdcp_logformat, 'a') as f:
  f.write(unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), amsg)))
