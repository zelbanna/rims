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
  return self.get(aKey,None)

 def __str__(self):
  return "<DETAILS CLASS='web blue'><SUMMARY>Web</SUMMARY>Base: %s<DETAILS><SUMMARY>Cookies</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS><SUMMARY>Form</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(self._base,str(self.cookie),self.form)

 def get(self,aKey,aDefault = None):
  return self.form.getfirst(aKey,aDefault)

 def log(self, aMsg):
  from logger import log
  log(aMsg,self.cookie.get("{}_id".format(self._base)))

 def rest_call(self, aURL, aAPI, aArgs = None, aMethod = None, aHeader = None):
  from rest import call
  return call(aURL, aAPI, aArgs, aMethod, aHeader)

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
  stdout.write("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'>\n<LINK REL='stylesheet' TYPE='text/css' HREF='system.css'>")
  if aTitle:
   stdout.write("<TITLE>" + aTitle + "</TITLE>")
  stdout.write("<LINK REL='shortcut icon' TYPE='image/png' HREF='images/%s.png'/>"%self._base)
  stdout.write("<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='system.js'></SCRIPT>")
  stdout.write("<SCRIPT>$(function() { $(document.body).on('click','a.z-op',btn ) .on('focusin focusout','input, select',focus ); });</SCRIPT>");
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
   keys    = self.form.keys()
   details = ("AJAX",self._base,mod_fun,type(e).__name__,",".join(keys), str(e)) 
   stdout.write("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>Type: %s<BR>API: %s.site.%s<BR>Excpt: %s<BR><DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%details)

 ############################## CGI/Web functions ###############################

 def get_args2dict(self):
  return { key: self[key] for key in self.form.keys() }

 def get_args2dict_except(self,aexceptlist = []):
  keys = self.form.keys()
  for exc in aexceptlist:
   try:    keys.remove(exc)
   except: pass
  return { key: self[key] for key in keys }

 def get_args(self):
  return "&".join(["%s=%s"%(key,self[key]) for key in self.form.keys()])

 def get_args_except(self,aexceptlist = []):
  keys = self.form.keys()
  for exc in aexceptlist:
   try:    keys.remove(exc)
   except: pass
  return "&".join(["%s=%s"%(key,self[key]) for key in keys])

 @classmethod
 def button(cls,aImg,**kwargs):
  return " ".join(["<A CLASS='z-op btn small-btn'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC=images/btn-%s.png></A>"%(aImg)])
 # Add drag n drop

 @classmethod
 def dragndrop(cls):
  return "<SCRIPT>dragndrop();</SCRIPT>"
