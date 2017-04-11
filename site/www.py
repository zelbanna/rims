"""Moduledocstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.0GA"
__status__= "Production"

#
# - reload_args -> get_args_except
# + site.cgi?
# + ajax/pane
#
#
# - Log function to avoid importing GenLib EVERYwhere..
#
#################################### Web Items #######################################

class Web(object):
 
 def __init__(self, aDebug=False):
  from sys import stdout
  import cgi
  if aDebug:
   import cgitb
   cgitb.enable(display=0, logdir="/tmp/")
  self._form = cgi.FieldStorage()
  self._debug = aDebug
  print "Content-Type: text/html\r\n"
  stdout.flush()

 def ajax(self):
  ajaxcall = self.get_value('call')
  if not ajaxcall:
   print "<SPAN style='font-size:10px'>No ajax call argument</SPAN>"
   return
  module = ajaxcall.split('_')[0]
  if   module == 'device':
   import ajax_device as ajaxmod
  elif module == 'rack':
   import ajax_rack as ajaxmod
  elif module == 'esxi':
   import ajax_esxi as ajaxmod
  elif module == 'graph':
   import ajax_graph as ajaxmod
  elif module == 'pdu':
   import ajax_pdu as ajaxmod
  elif module == 'console':
   import ajax_console as ajaxmod
  else:
   import ajax_extra as ajaxmod
  fun = getattr(ajaxmod,ajaxcall,None)  
  if not self._debug:
   fun(self)
  else:
   try:
    fun(self)
   except Exception as err:
    print "<SPAN style='font-size:10px'>Ajax Error - {}:({}) error: [{}]</SPAN>".format(ajaxcall,",".join(self.get_keys()),str(err))

 def pane(self):
  paneview = self.get_value('view')
  if not paneview:
   print "<SPAN style='font-size:10px'>No pane view argument</SPAN>"
   return
  import pane as panemod
  fun = getattr(panemod,paneview,None)
  if not self._debug:
   fun(self)
  else:
   try:
    fun(self)
   except Exception as err:
    print "Pane view:[{}] error: [{}]".format(paneview,str(err))
                 
 def get_keys(self):
  return self._form.keys()

 def get_value(self,aid,adefault = None):
  return self._form.getfirst(aid,adefault)

 def get_list(self, aid):
  return self._form.getlist(aid)
  
 def get_args_except(self,aexceptlist = []):
  reload = ""
  for key in self._form.keys():
   if not key in aexceptlist:
    reload = reload + "&{}=".format(key) + "&{}=".format(key).join(self._form.getlist(key))
  return reload[1:]

 # These should be the two mandatory items any web page needs to load 
 def get_header_base(self, aExtra = ""):
  return "<HEAD>\n<LINK REL='stylesheet' TYPE='text/css' HREF='z-style.css'>\n<META CHARSET='UTF-8'>\n{}\n</HEAD>".format(aExtra)

 def get_header_full(self,aTitle):
  return self.get_header_base("<TITLE>{}</TITLE>\n<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='z-functions.js'></SCRIPT>".format(aTitle))

 def get_listeners(self,aselector = "div_navbar"):
  return "<SCRIPT>$(function() { $('#"+ aselector +"').on('click','.z-op',function() { btnoperation(this); } ); });</SCRIPT>"

 def get_include(self,aurl):
  from urllib import urlopen
  try:
   sock = urlopen(aurl)
   html = sock.read()
   sock.close()
   return html
  except Exception as err:
   return ""

 def get_proxy(self,aurl,op,args):
  from json import loads
  if not self._debug:
   return  loads(self.get_include(aurl + "ajax.cgi?call=remote_json&op={}&{}".format(op,args)))
  else:
   self.log_msg(aurl + "?call=remote_json&op={}&{}".format(op,args))
   try:
    return loads(self.get_include(aurl + "ajax.cgi?call=remote_json&op={}&{}".format(op,args)))
   except Exception as err:
    self.log_msg("Error in get_proxy: {}".format(str(err)))
    return { "res":"get_proxy_err" }


 def log_msg(self, aMsg, aLog='/var/log/system/system.log'):
  from time import localtime, strftime
  output = unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg) )
  with open(aLog, 'a') as f:
   f.write( output )
