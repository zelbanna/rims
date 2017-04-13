"""Moduledocstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.3GA"
__status__= "Production"

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

 def log_msg(self, aMsg, aLog = None):
  if not aLog:
   import sdcp.SettingsContainer as SC
   aLog = SC.sdcp_logformat
  with open(aLog, 'a') as f:
   from time import localtime, strftime
   f.write( unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aMsg) ) )

 ################################# AJAX #########################################
 #
 #
 def ajax(self):
  ajaxcall = self.get_value('call')
  if not ajaxcall:
   from json import dumps
   print dumps({'err':'No ajax call argument'})
   return
  
  module = ajaxcall.partition('_')[0]
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
  try:
   fun(self)
  except Exception as err:
   keys = self.get_keys()
   keys.remove('call')
   keys = ",".join(keys)
   from json import dumps
   print dumps({ 'call':ajaxcall, 'args': keys, 'err':str(err) })

 ################################# PANE #########################################
 #
 #
 def pane(self):
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
 
 ################################# REST #########################################
 #
 # REST API:
 # - rpc: operation/function to call
 # - args: json string with arguments passed on as single argument to function call
 #
 def rest(self):
  from json import loads, dumps
  rpc  = self.get_value('rpc')
  args = loads(self.get_value('args',str({})))
  module = rpc.partition('_')[0]
  if   module == 'ddi':
   import rest_ddi as mod
  else:
   mod = None
  try:
   fun = getattr(mod,rpc,lambda x: { 'err':'no_such_op_in_module', 'op':x })
   print dumps(fun(args))
  except Exception as err:
   print dumps({ 'err':'module_error', 'res':str(err) })

 ############################## CGI/Web functions ###############################
 def get_dict(self):
  form = {}
  for key in self._form.keys():
   form[key] = self._form.getfirst(key)
  return form

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
