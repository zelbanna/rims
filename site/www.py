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
  self._debug = aDebug
  print "Content-Type: text/html\r\n"
  stdout.flush()

 def ajax(self):
  fun  = None
  ajaxcall = self.get_value('call')
  if not ajaxcall:
   print "<SPAN style='font-size:10px'>No ajax call argument</SPAN>"
   return
  import ajax as ajaxmod
  fun = getattr(ajaxmod,ajaxcall,None)  
  if self._debug:
   try:
    fun(self)
   except Exception as err:
    print "<SPAN style='font-size:10px'>Ajax call:[{}] error: [{}]</SPAN>".format(ajaxcall,str(err))
  else:
   if fun:
    fun(self)
   else:
    print "<SPAN style='font-size:10px'>Ajax call:[{}] no such function</SPAN>".format(ajaxcall) 

 def pane(self):
  fun  = None
  paneview = self.get_value('view')
  if not paneview:
   print "<SPAN style='font-size:10px'>No pane view argument</SPAN>"
   return
  import pane as panemod
  fun = getattr(panemod,paneview,None)
  if self._debug:
   try:
    fun(self)
   except Exception as err:
    print "Pane view:[{}] error: [{}]".format(paneview,str(err))
  else:
   if fun:
    fun(self)
   else:
    print "Pane view :[{}] no such view".format(paneview)
                 
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
