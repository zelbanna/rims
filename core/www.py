"""Module docstring.

Generic WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

#
# web handling object
# - cookies are dictionaries which encodes type and TTL
#
class Web(object):

 def __init__(self,aBase):
  from os import getenv
  self._header = {}
  self._c_stor = {}
  self._c_life = {}
  self._base = aBase
  self.form  = None
  bcookie = getenv("HTTP_COOKIE")
  self.cookie = {} if not bcookie else dict(map( lambda c: c.split("="), bcookie.split('; ')))

 def __getitem__(self,aKey):
  return self.form.getfirst(aKey,None)

 def __str__(self):
  return "Base:{} Cookie:[{}] Form:{}".format(self._base,self.cookie,self.form)

 def get(self,aKey,aDefault = None):
  return self.form.getfirst(aKey,aDefault)

 def log(self, aMsg):
  from logger import log
  log(aMsg,self.cookie.get("{}_id".format(self._base)))

 # Header Key/Values
 def add_header(self,aKey,aValue):
  self._header[aKey] = aValue

 # Cookie Param + Data and Life
 def add_cookie(self,aParam,aData,aLife=3000):
  self._c_stor[aParam] = aData
  self._c_life[aParam] = aLife

 def put_headers(self):
  for key,value in self._header.iteritems():
   print "{}: {}\r".format(key,value)
  for key,value in self._c_stor.iteritems():
   print "Set-Cookie: {}={}; Path=/; Max-Age={};\r".format(key,value,self._c_life.get(key,3000))
  self._header = None
  print "Content-Type: text/html\r\n"

 # Redirect will all cookies and headers set
 def put_redirect(self,aLocation):
  print "Location: {}\r".format(aLocation)
  self.put_headers()

 # Put full header and listener
 def put_html(self, aTitle = None):
  self.put_headers()
  from sys import stdout
  stdout.write("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'>\n<LINK REL='stylesheet' TYPE='text/css' HREF='z-style.css'>")
  if aTitle:
   stdout.write("<TITLE>" + aTitle + "</TITLE>")
  stdout.write("<LINK REL='shortcut icon' TYPE='image/png' HREF='images/" + self._base + ".png'/>")
  stdout.write("<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='z-functions.js'></SCRIPT>")
  stdout.write("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btnoperation ); });</SCRIPT></HEAD>")
  stdout.flush()

 ################################# AJAX #########################################
 #
 # call = <module>_<module_function>
 #
 def server(self):
  # Do something about field storage...
  import cgi
  self.form = cgi.FieldStorage()
  headers   = self.get('headers','yes')
  mod_fun   = self.get('call','front_login')
  (mod,void,fun) = mod_fun.partition('_')
  print "X-Z-Mod:{}\r".format(mod)
  print "X-Z-Fun:{}\r".format(fun)
  try:
   if headers == 'yes' and mod != 'front':
    print "Content-Type: text/html\r\n"
   from importlib import import_module
   module = import_module(self._base + ".site." + mod)
   getattr(module,fun,None)(self)
  except Exception, e:
   from sys import stdout
   if headers == 'no' or mod == 'front':
    stdout.write("Content-Type: text/html\r\n")
   keys = self.form.keys()
   from json import dumps
   stdout.write("<PRE STYLE='font-size:9px; font-weight:bold;'>" + (dumps({ 'res':'ERROR', 'type':'AJAX', 'api':"{}.site.{}".format(self._base,mod_fun), 'args':",".join(keys) , 'exception':type(e).__name__, 'info':str(e) }, sort_keys=True, indent=4) if not type(e).__name__ == 'RestException' else str(e)) + "</PRE>")

 ############################## CGI/Web functions ###############################

 def get_args2dict(self):
  return { key: self.form.getfirst(key,None) for key in self.form.keys() }

 def get_args2dict_except(self,aexceptlist = []):
  keys = self.form.keys()
  for exc in aexceptlist:
   try:    keys.remove(exc)
   except: pass
  return { key: self.form.getfirst(key,None) for key in keys }

 def get_args(self):
  reload = ""
  for key in self.form.keys():
   reload += ("&{}=".format(key) + "&{}=".format(key).join(self.form.getlist(key)))
  return reload[1:]

 def get_args_except(self,aexceptlist = []):
  reload = ""
  for key in self.form.keys():
   if not key in aexceptlist:
    reload += ("&{}=".format(key) + "&{}=".format(key).join(self.form.getlist(key)))
  return reload[1:]

 @classmethod
 def button(cls,aImg,**kwargs):
  return " ".join(["<A CLASS='z-op z-btn z-small-btn'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC=images/btn-%s.png></A>"%(aImg)])
