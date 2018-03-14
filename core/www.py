"""Module docstring.

Generic WWW/HTMLinterworking module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__= "Production"

#
# web handling object
# - cookies are 2x dictionaries which encodes type and TTL
#
class Web(object):

 def __init__(self,aREST):
  from os import getenv
  self._rest_url = aREST
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
  from common import rest_call
  return rest_call("%s?%s"%(self._rest_url, aAPI), aArgs, aTimeout = 60)['data']

 # Generic REST call with full output
 def rest_full(self, aURL, aAPI, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
  from common import rest_call
  return rest_call("%s?%s"%(aURL, aAPI) if aAPI else aURL, aArgs, aMethod, aHeader, True, aTimeout)

 ############################# Cookies #############################
 #
 # Cookies are key, value, lifetime
 # - Values are strings, numbers or dictionaries
 # - special case for dictionaries, the ',' char is used for joining items!

 def put_cookie(self,aName,aValue,aExpires):
  value = ",".join(["%s=%s"%(k,v) for k,v in aValue.iteritems()]) if isinstance(aValue,dict) else aValue
  print "<SCRIPT>set_cookie('%s','%s','%s');</SCRIPT>"%(aName,value,aExpires)

 # Unjar returns a dict with whatever was jar:ed into that cookie name (or empty)
 def cookie_unjar(self,aName):
  try:    return dict(value.split('=') for value in self.cookies[aName].split(','))
  except: return {}

 # Redirect
 def put_redirect(self,aLocation):
  print "<SCRIPT> window.location.replace('%s'); </SCRIPT>"%(aLocation)

 # Put full header and listener
 def put_html(self, aTitle = None):
  from sys import stdout
  stdout.write("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'>\n<LINK REL='stylesheet' TYPE='text/css' HREF='system.css'>")
  if aTitle:
   stdout.write("<TITLE>" + aTitle + "</TITLE>")
  stdout.write("<LINK REL='shortcut icon' TYPE='image/png' HREF='images/sdcp.png'/>")
  stdout.write("<SCRIPT SRC='https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'></SCRIPT>\n<SCRIPT SRC='system.js'></SCRIPT>")
  stdout.write("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ); });</SCRIPT>")
  stdout.write("</HEAD>")
  stdout.flush()

 ################################# AJAX #########################################
 #
 # call = <module>_<module_function>
 #
 def server(self):
  # Do something about field storage...
  import cgi
  from sys import stdout
  self.form = cgi.FieldStorage()
  mod_fun   = self.get('call','sdcp_login')
  (mod,void,fun) = mod_fun.partition('_')
  stdout.write("X-Z-Mod:%s\r\nX-Z-Fun:%s\r\n"%(mod,fun))
  stdout.write("Content-Type:text/html\r\n\n")
  try:
   from importlib import import_module
   module = import_module("sdcp.site." + mod)
   getattr(module,fun,None)(self)
  except Exception, e:
   stdout.write("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>API:&nbsp; sdcp.site.%s<BR>"%mod_fun)
   try:
    stdout.write("Type: %s<BR>Code: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY>"%(e[0]['exception'],e[0]['code']))
    try:
     for key,value in e[0]['info'].iteritems():
      stdout.write("%s: %s<BR>"%(key,value))
    except: stdout.write(e[0]['info'])
    stdout.write("</DETAILS>")
   except:
    stdout.write("Type: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS>"%(type(e).__name__,str(e)))
   stdout.write("<DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(",".join(self.form.keys())))

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
