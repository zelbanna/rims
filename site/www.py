"""Moduledocstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__= "2.0GA"
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
  print "Content-Type: text/html\r\n"
  stdout.flush()
  
 def site_start(self):
  pane = self.get_value('pane')
  ajax = self.get_value('ajax')
  fun = None
  if pane:
   import pane as panemod
   fun = getattr(panemod,pane,None)
  elif ajax:
   import ajax as ajaxmod
   fun = getattr(ajaxmod,ajax,None)  
  else:
   print "<B>No function supplied - neither 'ajax' call nor 'pane' view (keys: {})</B>".format(str(self.get_keys()))
   return
  if fun:
   fun(self)  
  else:
   print "<B>No function mapping for pane:[{}] ajax:[{}] keys:[{}]</B>".format(pane,ajax)

 def get_keys(self):
  return self._form.keys()

 def get_value(self,aid,adefault = None):
  return self._form.getfirst(aid,adefault)

 def get_list(self, aid):
  return self._form.getlist(aid)
  
 def reload_args_except(self,aexceptlist = []):
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
  return "<SCRIPT>$(function() { $('#"+ aselector +"').on('click','.z-btnop',function() { btnoperation(this); } ); });</SCRIPT>"

 def get_include(self,aurl):
  from urllib import urlopen
  try:
   sock = urlopen(aurl)
   html = sock.read()
   sock.close()
   return html
  except Exception as err:
   return ""

 def log_msg(self, aMsg, aLog='/var/log/system/system.log'):
  from time import localtime, strftime
  output = unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg) )
  with open(aLog, 'a') as f:
   f.write( output )
