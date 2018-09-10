#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP HTTP server.

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

from os import walk, path as ospath, environ
from sys import path as syspath, stdout
from json import loads, dumps
from importlib import import_module
from threading import Thread
from time import localtime, strftime, sleep
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import parse_qs

basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..'))
pkgpath  = ospath.join(basepath,'zdcp')
syspath.insert(1, basepath)
from zdcp.SettingsContainer import SC

############################### ZDCP Server ############################
#
#
class Server:
 """ Class manages HTTP interaction, provides interface to settings and log tools """

 def __init__(self, aPort, aNodeID):
  import socket
  self._threads = []
  self._id = aNodeID
  self._addr = ('', int(aPort))
  self._socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
  self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  self._socket.bind(self._addr)
  self._socket.listen(5)

 def start(self, aThreads):
  try:
   self._threads = [self.HttpThread(n,self._socket,'',self._id) for n in range(aThreads)]
   print "ZDCP server started %s workers @ %s"%(aThreads,self._addr)
   while len(self._threads) > 0:
    # Check if threads are still alive...
    self._threads = [t for t in self._threads if t.is_alive()]
    sleep(10)
  except:
   print "ZDCP server interrupted"
  else:
   print "ZDCP server shutdown due to no live threads"
  self._socket.close()

 #
 # HTTP Thread
 #
 class HttpThread(Thread):
  def __init__(self, aID, aSock, aAddr, aNodeID):
   Thread.__init__(self)
   self._id   = aID
   self._node = aNodeID
   self._sock = aSock
   self._addr = aAddr
   self.daemon = True
   self.start()

  def __str__(self):
   return "HttpThread %s [Node:%s,Daemon:%s,Alive:%s]"%(self._node,self._id,self.daemon,self.is_alive())

  def run(self):
   httpd = HTTPServer(self._addr, Server.SessionHandler, False)
   httpd._id = self._id
   httpd._node = self._node
   # Prevent the HTTP server from re-binding every handler.
   # https://stackoverflow.com/questions/46210672/
   httpd.socket = self._sock
   httpd.server_bind = self.server_close = lambda self: None
   try: httpd.serve_forever()
   except: pass

 #
 # ZDCP call handler
 #
 class SessionHandler(BaseHTTPRequestHandler):

  def __init__(self, *args):
   self._cookies = {}
   self._form    = {}
   BaseHTTPRequestHandler.__init__(self,*args)

  def __route(self):
   path = self.path.lstrip('/')
   call = path.partition('/')
   if   call[0] == 'api':
    self.__api(call[2])
   elif call[0] == 'infra' or call[0] == 'images':
    self.__infra(call[0],call[2])
   elif call[0] == 'site':
    self.__site(call[2])
   elif call[0] == 'zdcp.pdf':
    self.__infra('','zdcp.pdf')
   else:
    self.send_response(301)
    self.send_header('Location','site/system_login')
    self.end_headers()

  def __log_rest(self,aAPI,aArgs,aExtra):
   try:
    with open(SC['logs']['rest'], 'a') as f:
     f.write(unicode("%s: %s '%s' @ %s (%s) NATIVE\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aAPI, aArgs, self.server._node, aExtra.strip())))
   except: pass

  def do_HEAD(self):
   self.send_response(200)
   self.send_header("Content-type", "text/html")
   self.end_headers()

  def do_GET(self):
   self.__route()

  def do_POST(self):
   self.__route()

  ########################################## REST Function ####################################
  #
  def __api(self, aQuery):
   """Function process processes each call.
    - Expecting query string encoded as <REST-NODE/api>/module_function[&node=<node>] (thus module cannot contain '_', but function can)
    - Returns json:ed response from function
   """
   headers,output,additional= {'thread':self.server._id,'method':self.command},'null',{}
   # Partition QUERY
   (api,_,extra) = aQuery.partition('&')
   (mod,_,fun)   = api.partition('_')
   headers['module']= mod
   headers['function']= fun
   if extra:
     for part in extra.split("&"):
      (k,_,v) = part.partition('=')
      additional[k] = v
   headers['node'] = additional.get('node',self.server._node if not mod == 'system' else 'master')
   # Read data (if POST or other than GET)
   try:
    try:
     length = int(self.headers.getheader('content-length'))
     args = loads(self.rfile.read(length)) if length > 0 else {}
    except: args = {}
    self.__log_rest(api,dumps(args),extra)
    if headers['node'] == self.server._node:
     module = import_module("zdcp.rest.%s"%mod)
     module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC})
     output = dumps(getattr(module,fun,None)(args))
     headers['result'] = 'OK'
    else:
     from zdcp.core.common import rest_call
     try: res = rest_call("%s/api/%s"%(SC['nodes'][headers['node']],aQuery),args)
     except Exception as err: raise Exception(err)
     else: output = dumps(res['data'])
     headers['result'] = res['info'].get('x-api-result','ERROR')
   except Exception as e:
    headers.update({'result':'ERROR','args':args,'info':str(e),'xcpt':type(e).__name__})
   self.send_response(200 if headers['result'] == 'OK' else 500)
   self.send_header("Content-Type","application/json; charset=utf-8")
   self.send_header("Access-Control-Allow-Origin","*")
   for k,v in headers.iteritems():
    self.send_header("X-API-%s"%k.title(),v)
   self.end_headers()
   self.wfile.write(output)

  ########################################## Infra Function ####################################
  #
  def __infra(self, aPath, aQuery):
   headers,output = {},''
   if   aQuery.endswith(".jpg"):
    headers['Content-type'] = 'image/jpg'
    headers['Content-Disposition'] = 'inline'
   elif aQuery.endswith(".png"):
    headers['Content-type']='image/png'
    headers['Content-Disposition'] = 'inline'
   elif aQuery.endswith(".js"):
    headers['Content-type']='application/javascript; charset=utf-8'
   elif aQuery.endswith(".css"):
    headers['Content-type']='text/css; charset=utf-8'
   elif aQuery.endswith(".pdf"):
    headers['Content-type']='application/pdf'
   elif aQuery.endswith(".html"):
    headers['Content-type']='text/html; charset=utf-8'
   else:
    headers['Content-type']='application/octet-stream;'
   try:
    if aQuery.endswith("/") or len(aQuery) == 0:
     headers['Content-type']='text/html; charset=utf-8'
     _, _, filelist = next(walk(ospath.join(pkgpath,aPath,aQuery)), (None, None, []))
     output = "<BR>".join(["<A HREF='{0}'>{0}</A>".format(file) for file in filelist])
    else:
     with open(ospath.join(pkgpath,aPath,aQuery), 'rb') as file:
      output = file.read()
   except Exception as e:
    self.send_response(404)
    headers['X-Error'] = str(e)
    headers['X-Query'] = aQuery
    headers['X-Path'] = aPath
   else:
     self.send_response(200)
   for k,v in headers.iteritems():
    self.send_header(k,v)
   self.end_headers()
   self.wfile.write(output)

  ########################################## Site Function ####################################
  #
  # Before React.JS... do not optimize more than necessary
  #
  # - store form data?
  # Check input, either rfile is args - like rest - or
  def __site(self, aQuery):
   mod_fun,_,args = aQuery.partition('?')
   self.__parse_cookies()
   self.__parse_form(args)
   (mod,_,fun)    = mod_fun.partition('_')
   self.send_response(200)
   self.send_header("Content-type", 'text/html; charset=utf-8')
   self.end_headers()
   # Remove try/except to debug
   # print "_______________________ %s _____________________"%aQuery 
   try:
    module = import_module("zdcp.site." + mod)
    getattr(module,fun,None)(self)
   except Exception as e:
    self.wfile.write("<DETAILS CLASS='web'><SUMMARY CLASS='red'>ERROR</SUMMARY>API:&nbsp; zdcp.site.%s_%s<BR>"%(mod,fun))
    try:
     self.wfile.write("Type: %s<BR>Code: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY>"%(e[0]['exception'],e[0]['code']))
     try:
      for key,value in e[0]['info'].iteritems():
       self.wfile.write("%s: %s<BR>"%(key,value))
     except: self.wfile.write(e[0]['info'])
     self.wfile.write("</DETAILS>")
    except:
     self.wfile.write("Type: %s<BR><DETAILS open='open'><SUMMARY>Info</SUMMARY><CODE>%s</CODE></DETAILS>"%(type(e).__name__,str(e)))
    self.wfile.write("<DETAILS><SUMMARY>Args</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(",".join(self._form.keys())))


  def put_html(self, aTitle = None, aIcon = 'zdcp.png'):
   self.wfile.write("<!DOCTYPE html><HEAD><META CHARSET='UTF-8'><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/4.21.0.vis.min.css' /><LINK REL='stylesheet' TYPE='text/css' HREF='../infra/zdcp.css'>")
   if aTitle:
    self.wfile.write("<TITLE>" + aTitle + "</TITLE>")
   self.wfile.write("<LINK REL='shortcut icon' TYPE='image/png' HREF='../images/%s'/>"%(aIcon))
   self.wfile.write("<SCRIPT SRC='../infra/3.1.1.jquery.min.js'></SCRIPT><SCRIPT SRC='../infra/4.21.0.vis.min.js'></SCRIPT><SCRIPT SRC='../infra/zdcp.js'></SCRIPT>")
   self.wfile.write("<SCRIPT>$(function() { $(document.body).on('click','.z-op',btn ) .on('focusin focusout','input, select',focus ) .on('input','.slider',slide_monitor); });</SCRIPT>")
   self.wfile.write("</HEAD>")


  def wr(self,aTXT):
   self.wfile.write(aTXT)

  def node(self):
   return self.server._node

  def cookie(self,aName):
   return self._cookies.get(aName)

  def args(self):
   return self._form

  def __parse_cookies(self):
   try: cookie_str = self.headers.get('Cookie').split('; ')
   except: pass
   else:
    for cookie in cookie_str:
     k,_,v = cookie.partition('=')
     try:    self._cookies[k] = dict(x.split('=') for x in v.split(','))
     except: self._cookies[k] = v

  def __parse_form(self,aGet):
   try:    body_len = int(self.headers.getheader('content-length'))
   except: body_len = 0
   if body_len > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(self.rfile.read(body_len), keep_blank_values=1).iteritems() })
   if len(aGet) > 0:
    self._form.update({ k: l[0] for k,l in parse_qs(aGet, keep_blank_values=1).iteritems() })

  def __str__(self):
   return "<DETAILS CLASS='web blue'><SUMMARY>Web</SUMMARY>Web object<DETAILS><SUMMARY>Cookies</SUMMARY><CODE>%s</CODE></DETAILS><DETAILS><SUMMARY>Form</SUMMARY><CODE>%s</CODE></DETAILS></DETAILS>"%(str(self._cookies),self._form)

  def __getitem__(self,aKey):
   return self._form.get(aKey,None)

  def get(self,aKey,aDefault = None):
   return self._form.get(aKey,aDefault)

  def get_args2dict(self,aExcept = []):
   return { k:v for k,v in self._form.iteritems() if not k in aExcept }

  def get_args(self,aExcept = []):
   return "&".join(["%s=%s"%(k,v) for k,v in self._form.iteritems() if not k in aExcept])

  def button(self,aImg,**kwargs):
   return " ".join(["<A CLASS='btn z-op small'"," ".join(["%s='%s'"%(key,value) for key,value in kwargs.iteritems()]),"><IMG SRC='../images/btn-%s.png'></A>"%(aImg)])

  @classmethod
  def dragndrop(cls):
   return "<SCRIPT>dragndrop();</SCRIPT>"

  # Simplified SDCP REST call
  def rest_call(self, aAPI, aArgs = None, aTimeout = 60):
   from zdcp.core.common import rest_call
   return rest_call("%s/api/%s"%(SC['system']['node'],aAPI), aArgs, aTimeout = 60)['data']

  # Generic REST call with full output
  def rest_full(self, aURL, aArgs = None, aMethod = None, aHeader = None, aTimeout = 20):
   from zdcp.core.common import rest_call
   return rest_call(aURL, aArgs, aMethod, aHeader, True, aTimeout)

  def put_cookie(self,aName,aValue,aExpires):
   value = ",".join(["%s=%s"%(k,v) for k,v in aValue.iteritems()]) if isinstance(aValue,dict) else aValue
   self.wfile.write("<SCRIPT>set_cookie('%s','%s','%s');</SCRIPT>"%(aName,value,aExpires))

  # Redirect
  def put_redirect(self,aLocation):
   self.wfile.write("<SCRIPT> window.location.replace('%s'); </SCRIPT>"%(aLocation))

 

if __name__ == '__main__':
 #
 zdcp = Server(int(SC['system']['port']),SC['system']['id'])
 zdcp.start(5)
