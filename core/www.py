"""Module docstring.

Generic WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

#
# web handling object
# - cookies are 2x dictionaries which encodes type and TTL
#
class Web(object):

 def __init__(self,aREST):
  from os import getenv
  self._header = {}
  self._rest_url = aREST
  self._c_stor = {}
  self._c_life = {}
  self.form  = None
  self.cookies = {}
  cookies = getenv("HTTP_COOKIE")
  if cookies:
   for cookie in cookies.split('; '):
    k,_,v = cookie.partition('=')
    self.cookies[k] = v

 def __getitem__(self,aKey):
  return self.form.getfirst(aKey,None)

 def __str__(self):
  return "<DETAILS CLASS='web blue'><SUMMARY>Web</SUMMARY>Web object<DETAILS><SUMMARY>Cookies</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS><SUMMARY>Form</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(str(self.cookies),self.form)

 def get(self,aKey,aDefault = None):
  return self.form.getfirst(aKey,aDefault)

 def log(self, aMsg):
  from logger import log
  log(aMsg,'sdcp')

 # Simplified SDCP REST call
 def rest_call(self, aAPI, aArgs = None):
  from rest import call
  return call(self._rest_url, aAPI, aArgs )['data']

 # Generic REST call
 def rest_generic(self, aURL, aAPI, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  from rest import call
  return call(aURL, aAPI, aArgs, aMethod, aHeader, True, aTimeout)['data']

 # Generic REST call with full output
 def rest_full(self, aURL, aAPI, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  from rest import call
  return call(aURL, aAPI, aArgs, aMethod, aHeader, True, aTimeout)

 # Header Key/Values
 def add_header(self,aKey,aValue):
  self._header[aKey] = aValue

 ############################# Cookies #############################
 #
 # Cookies are key, value, lifetime
 # - Values are strings, numbers or dictionaries
 # - special case for dictionaries, the ',' char is used for joining items!
 def cookie_jar(self,aName,aValue,aLife=3000):
  self._c_stor[aName] = ",".join(["%s=%s"%(k,v) for k,v in aValue.iteritems()])
  self._c_life[aName] = aLife

 # Unjar returns a dict with whatever was jar:ed into that cookie name (or empty)
 def cookie_unjar(self,aName):
  try:    return dict(value.split('=') for value in self.cookies[aName].split(','))
  except: return {}

 def cookie_add(self,aName,aValue,aLife=3000):
  self._c_stor[aName] = aValue
  self._c_life[aName] = aLife

 def put_headers(self):
  for key,value in self._header.iteritems():
   print "{}: {}\r".format(key,value)
  for key,value in self._c_stor.iteritems():
   print "Set-Cookie: %s=%s; Path=/; Max-Age=%i;\r"%(key,value,self._c_life.get(key,3000))
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
  stdout.write("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'>\n<LINK REL='stylesheet' TYPE='text/css' HREF='system.css'>")
  if aTitle:
   stdout.write("<TITLE>" + aTitle + "</TITLE>")
  stdout.write("<LINK REL='shortcut icon' TYPE='image/png' HREF='images/sdcp.png'/>")
  stdout.write("<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='system.js'></SCRIPT>")
  stdout.write("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ); });</SCRIPT>");
  stdout.write("</HEAD>")
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
  mod_fun   = self.get('call','sdcp_login')
  (mod,void,fun) = mod_fun.partition('_')
  print "X-Z-Mod:{}\r".format(mod)
  print "X-Z-Fun:{}\r".format(fun)
  try:
   if headers == 'yes' and mod != 'sdcp':
    print "Content-Type: text/html\r\n"
   from importlib import import_module
   module = import_module("sdcp.site." + mod)
   getattr(module,fun,None)(self)
  except Exception, e:
   from sys import stdout
   if headers == 'no' or mod == 'sdcp':
    stdout.write("Content-Type: text/html\r\n\n")
   keys    = self.form.keys()
   details = ("AJAX",mod_fun,type(e).__name__,",".join(keys), str(e)) 
   stdout.write("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>Type: %s<BR>API: sdcp.site.%s<BR>Excpt: %s<BR><DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%details)

 ############################## CGI/Web functions ###############################

 def get_args2dict(self,aExcept = []):
  return { key: self[key] for key in self.form.keys() if not key in aExcept }

 def get_args(self,aExcept = []):
  return "&".join(["%s=%s"%(key,self[key]) for key in self.form.keys() if not key in aExcept])

 @classmethod
 def button(cls,aImg,**kwargs):
  return " ".join(["<BUTTON CLASS='z-op small'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC=images/btn-%s.png></BUTTON>"%(aImg)])

 @classmethod
 def a_button(cls,aImg,**kwargs):
  return " ".join(["<A CLASS='btn z-op small'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC=images/btn-%s.png></A>"%(aImg)])

 @classmethod
 def dragndrop(cls):
  return "<SCRIPT>dragndrop();</SCRIPT>"
