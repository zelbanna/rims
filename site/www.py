"""Module docstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

class Web(object):
 
 #
 # Create a web object and prep content for display, or download (by forcing to octet stream)
 # 
 def __init__(self, aDebug=False):
  import cgi
  if aDebug:
   import cgitb
   cgitb.enable(display=0, logdir="/tmp/")
  self._form = cgi.FieldStorage()
  self._debug = aDebug

 def log_msg(self, aMsg, aLog = None):
  if not aLog:
   import sdcp.SettingsContainer as SC
   aLog = SC.sdcp_logformat
  with open(aLog, 'a') as f:
   from time import localtime, strftime
   f.write( unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg) ) )

 ################################# AJAX #########################################
 #
 # call = <module>_<module_function>
 #
 def ajax(self):
  from sys import stdout
  print "Content-Type: text/html\r\n"
  stdout.flush()
  ajaxcall = self.get_value('call','none_nocall')
  (module,void,call) = ajaxcall.partition('_')
  from importlib import import_module
  try:
   ajaxmod = import_module("sdcp.site.ajax_" + module)
   fun = getattr(ajaxmod,call,None)
   fun(self)
  except Exception as err:
   keys = self.get_keys()
   if 'call' in keys:
    keys.remove('call')
   keys = ",".join(keys)
   from json import dumps
   print dumps({ 'ajax_module':module, 'call':call, 'args': keys, 'err':str(err) }, sort_keys=True)

 ################################# PANE #########################################
 #
 #
 def pane(self):
  from sys import stdout
  print "Content-Type: text/html\r\n"
  stdout.flush()
  paneview = self.get_value('view')
  if not paneview:
   print "<SPAN style='font-size:10px'>No pane view argument</SPAN>"
   return
  import pane as panemod
  fun = getattr(panemod,paneview,None)
  try:
    fun(self)
  except Exception as err:
   print "<SPAN style='font-size:10px'>Pane view:[{}] error: [{}]".format(paneview, str(err))
   if not paneview in dir(panemod):
    print " - possible panes:[{}]".format(", ".join(filter(lambda p: p[:2] != "__", dir(panemod))))
   print "</SPAN>"
 
 ############################## CGI/Web functions ###############################
 
 def quote(self,aString):
  from urllib import quote_plus
  return quote_plus(aString)

 def get_dict(self):
  return dict(map(lambda x: (x,self._form.getfirst(x,None)), self._form.keys()))

 def get_keys(self):
  return self._form.keys()

 def get_args2dict_except(self,aexceptlist = []):
  keys = self._form.keys()
  for exc in aexceptlist:
   try:
    keys.remove(exc)
   except:
    pass
  return dict(map(lambda x: (x,self._form.getfirst(x,None)), keys))

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
