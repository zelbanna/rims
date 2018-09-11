"""Module docstring.

SRX Module

"""
__author__  = "Zacharias El Banna"
__version__ = "4.0GA"
__status__  = "Production"
__type__    = "network"
__icon__    = "../images/viz-srx.png"

from junos import Junos

################################ SRX Object #####################################

class Device(Junos):

 @classmethod
 def get_functions(cls):
  return Junos.get_functions()

 def __init__(self,aIP,aID=None):
  Junos.__init__(self, aIP,aID)
  self.dnslist = []
  self.dhcpip = ""
  self.tunnels = 0

 def __str__(self):
  return Junos.__str__(self) + " Resolvers:" + str(self.dnslist) + " IP:" + self.dhcpip + " IPsec:" + str(self.tunnels)

 def load_dhcp(self):
  try:
   result = self._router.rpc.get_dhcp_client_information() 
   addresslist = result.xpath(".//address-obtained")
   if len(addresslist) > 0:
    self.dnslist = result.xpath(".//dhcp-option[dhcp-option-name='name-server']/dhcp-option-value")[0].text.strip('[] ').replace(", "," ").split()
    self.dhcpip = addresslist[0].text
  except Exception as err:
   self.log_msg("System Error - verifying DHCP assignment: " + str(err))
   return False
  return True

 def renew_dhcp(self, interface):
  try:
   return self._router.rpc.cli("request system services dhcp renew " + interface, format='text')
  except Exception as err:
   self.log_msg("System Error - cannot renew DHCP lease: " +str(err))
  return False
   
 def get_ipsec(self,gwname):
  from lxml import etree
  try:
   # Could actually just look at "show security ike security-associations" - len of that result
   # is the number of ikes (not tunnels though) with GW etc
   # If tunnel is down though we don't know if config is aggresive or state down, should check
   self.tunnels = int(self._router.rpc.get_security_associations_information()[0].text)
   ike = self._router.rpc.get_config(filter_xml=etree.XML('<configuration><security><ike><gateway></gateway></ike></security></configuration>'))
   address = ike.xpath(".//gateway[name='" + gwname + "']/address")
   return address[0].text, self.tunnels
  except Exception as err:
   self.log_msg("System Error - getting IPsec data: " + str(err))
   return None, self.tunnels

 def set_ipsec(self,gwname,oldip,newip):
  try:
   self._config.load("set security ike gateway " + gwname + " address " + newip, format = 'set')
   self._config.load("delete security ike gateway " + gwname + " address " + oldip, format = 'set')
   self._config.commit("commit by setIPsec ["+gwname+"]")
  except Exception as err:
   self.log_msg("System Error - modifying IPsec: " + str(err))
   return False
  return True
