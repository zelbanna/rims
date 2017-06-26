"""Module docstring.

WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

class Web(object):

 def __init__(self):
  from os import getenv
  cookie = getenv("HTTP_COOKIE")
  self._browser_cookie = {} if not cookie else dict(map( lambda c: c.split("="), getenv("HTTP_COOKIE").replace(";",'').split()))
  self._header = {}
  self._cookie = {}
  self._form = None

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
  import cgi
  self._form = cgi.FieldStorage()
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
 # pane, view = <module>_<function>
 #
 def pane(self):
  import cgi
  self._form = cgi.FieldStorage()
  paneview = self.get_value('view')
  try:
   import pane as panemod
   getattr(panemod,paneview,None)(self)
  except Exception as err:
   print "Content-Type: text/html\r\n"
   print "<SPAN style='font-size:10px'>Pane view:[{}] error: [{}]".format(paneview, str(err))
   if not paneview in dir(panemod):
    print " - possible panes:[{}]".format(", ".join(filter(lambda p: p[:2] != "__", dir(panemod))))
   print "</SPAN>"

 # Header Key/Values
 def put_header(self,aKey,aValue):
  self._header[aKey] = aValue

 # Cookie Name + Params, Data= main
 def put_cookie(self,aName,aData):
  self._cookie[aName] = aData

 # Put a proper HTML header + body header (!) for the browser
 def put_html_header(self, aTitle = None):
  self._has_header = True
  for key,value in self._header.iteritems():
   print "{}: {}\r".format(key,value)   
  for key,value in self._cookie.iteritems():
   print "Set-Cookie: {}={}; Path=/; Max-Age=3000;\r".format(key,value)
  self._header = None
  print "Content-Type: text/html\r\n"
  print "<HEAD>"
  print "<LINK REL='stylesheet' TYPE='text/css' HREF='z-style.css'>\n<META CHARSET='UTF-8'>"
  if aTitle:
   print "<TITLE>{}</TITLE>".format(aTitle)
  print "<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='z-functions.js'></SCRIPT>"
  print "</HEAD>"
  from sys import stdout
  stdout.flush()
 
 ############################## CGI/Web functions ###############################
 def get_cookie(self):
  return self._browser_cookie

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
