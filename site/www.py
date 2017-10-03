"""Module docstring.

Generic WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"

#
# web handling object
# - cookies are dictionaries which encodes
#
class Web(object):

 def __init__(self):
  from os import getenv
  bcookie = getenv("HTTP_COOKIE")
  self._header = {}
  self._c_stor = {}
  self._c_life = {}
  self.form = None  
  self.cookie = {} if not bcookie else dict(map( lambda c: c.split("="), bcookie.split('; ')))
 
 # Header Key/Values
 def add_header(self,aKey,aValue):
  self._header[aKey] = aValue

 # Cookie Param + Data and Life 
 def add_cookie(self,aParam,aData,aLife=3000):
  self._c_stor[aParam] = aData
  self._c_life[aParam] = aLife

 def _put_headers(self):
  for key,value in self._header.iteritems():
   print "{}: {}\r".format(key,value)   
  for key,value in self._c_stor.iteritems():
   print "Set-Cookie: {}={}; Path=/; Max-Age={};\r".format(key,value,self._c_life.get(key,3000))   
  self._header = None
  print "Content-Type: text/html\r\n"

 # Redirect will all cookies and headers set
 def put_redirect(self,aLocation):
  print "Location: {}\r".format(aLocation)
  self._put_headers()

 # Put full header and listener
 def put_html(self, aTitle = None):
  self._put_headers()
  print "<HEAD><META CHARSET='UTF-8'>\n<LINK REL='stylesheet' TYPE='text/css' HREF='z-style.css'>"
  if aTitle:
   print "<TITLE>{}</TITLE>".format(aTitle)
  print "<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='z-functions.js'></SCRIPT>"
  print "<SCRIPT>$(function() { $(document.body).on('click','.z-op',btnoperation ); });</SCRIPT></HEAD>"
  from sys import stdout
  stdout.flush()

 ################################# AJAX #########################################
 #
 # call = <module>_<module_function>
 #
 def ajax(self,aSiteBase):
  from sys import stdout
  print "Content-Type: text/html\r\n"
  stdout.flush()
  import cgi
  self.form = cgi.FieldStorage()
  ajaxcall = self.get_value('call','none_nocall')
  (module,void,call) = ajaxcall.partition('_')
  from importlib import import_module
  try:
   ajaxmod = import_module(aSiteBase + ".site.ajax_" + module)
   fun = getattr(ajaxmod,call,None)
   fun(self)
  except Exception as err:
   keys = self.form.keys()
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
  self.form = cgi.FieldStorage()
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

 ############################## CGI/Web functions ###############################

 def quote(self,aString):
  from urllib import quote_plus
  return quote_plus(aString)

 def get_args2dict_except(self,aexceptlist = []):
  keys = self.form.keys()
  for exc in aexceptlist:
   try:
    keys.remove(exc)
   except:
    pass
  return dict(map(lambda x: (x,self.form.getfirst(x,None)), keys))

 def get_value(self,aid,adefault = None):
  return self.form.getfirst(aid,adefault)

 def get_args(self):
  reload = ""
  for key in self.form.keys():
   reload = reload + "&{}=".format(key) + "&{}=".format(key).join(self.form.getlist(key))
  return reload[1:]
  
 def get_args_except(self,aexceptlist = []):
  reload = ""
  for key in self.form.keys():
   if not key in aexceptlist:
    reload = reload + "&{}=".format(key) + "&{}=".format(key).join(self.form.getlist(key))
  return reload[1:]

 def get_include(self,aurl):
  from urllib import urlopen
  try:
   sock = urlopen(aurl)
   html = sock.read()
   sock.close()
   return html
  except Exception as err:
   return ""
