"""Module docstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.5GA"
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
  ajaxcall = self.get_value('call','none_nofunc')
  (module,void,func) = ajaxcall.partition('_')
  from importlib import import_module
  try:
   ajaxmod = import_module("sdcp.site.ajax_" + module)
   fun = getattr(ajaxmod,func,None)
   fun(self)
  except Exception as err:
   keys = self.get_keys()
   if 'call' in keys:
    keys.remove('call')
   keys = ",".join(keys)
   from json import dumps
   print dumps({ 'ajax_module':module, 'function':func, 'args': keys, 'err':str(err) }, sort_keys=True)

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
 
 ################################# REST #########################################
 #
 # REST API:
 # - rpc: operation/function to call
 # - args: json string with arguments passed on as single argument to function call
 # - format: pretty print if True
 #
 def rest(self):
  from sys import stdout
  from json import loads, dumps
  from importlib import import_module
  print "Content-Type: text/html\r\n"
  stdout.flush()
  rpc  = self.get_value('rpc','none_nofunc')
  args = self.get_value('args',str({}))
  (module,void,func) = rpc.partition('_')
  try:
   mod = import_module("sdcp.site.rest_" + module)
   fun = getattr(mod,func,lambda x: { 'err':"No such function in module", 'args':x, 'rest_module':module, 'function':func })
   print dumps(fun(loads(args)))
  except Exception as err:
   print dumps({ 'err':'module_error', 'res':str(err), 'rest_module':module, 'function':func }, sort_keys=True)

 ############################## CGI/Web functions ###############################
 def json2html(self,astring):
  from urllib import quote_plus
  return quote_plus(astring)

 def get_dict(self):
  form = {}
  for key in self._form.keys():
   form[key] = self._form.getfirst(key)
  return form

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
