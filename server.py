#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP HTTP server.

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

from os import getenv, path as ospath, environ
from sys import path as syspath
from json import loads, dumps
from importlib import import_module
from threading import Thread
from time import localtime, strftime, sleep
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..')))

############################### ZDCP Server ############################
#
#
class Server:
 """ Class manages HTTP interaction, provides interface to settings and log tools """

 def __init__(self, aPort, aNodeID):
  import socket
  self._threads = []
  self._id = aNodeID
  self._socket = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
  self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  self._socket.bind(('', int(aPort)))
  self._socket.listen(5)

 def start(self, aThreads):
  try:
   print "Starting ZDCP Server"
   self._threads = [self.HttpThread(n,self._socket,'',self._id) for n in range(aThreads)]
   while True:
    sleep(3)
  except:
   print " pressed, stopping ZDCP"
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
   httpd = HTTPServer(self._addr, Server.RestHandler, False)
   httpd._id = self._id
   httpd._node = self._node
   # Prevent the HTTP server from re-binding every handler.
   # https://stackoverflow.com/questions/46210672/
   httpd.socket = self._sock
   httpd.server_bind = self.server_close = lambda self: None
   try: httpd.serve_forever()
   except: pass

 #
 # ZDCP REST call handler, similar for Site is future simplification
 #
 class RestHandler(BaseHTTPRequestHandler):

  #
  def do_HEAD(self):
   self.send_response(200)
   self.send_header("Content-type", "text/html")
   self.end_headers()

  #
  def do_GET(self):
   self.__process('GET')
  #
  def do_POST(self):
   self.__process('POST')

  #
  def __log(self,aAPI,aArgs,aExtra):
   try:
    with open('/var/log/system/rest.log', 'a') as f:
     f.write(unicode("%s: %s '%s' @ %s (%s) NATIVE\n"%(strftime('%Y-%m-%d %H:%M:%S', localtime()), aAPI, aArgs, self.server._node, aExtra.strip())))
   except Exception as e:
    print "Error logging: %s"%str(e)

  #
  def __process(self,aMethod):
   """Function process processes each call.
    - Expecting query string encoded as <REST-NODE>/module_function[&node=<node>] (thus module cannot contain '_', but function can)
    - Returns json:ed response from function
    - Method not used for now
   """
   query,headers,output,args,cookies,additional= self.path.lstrip('/'),{'thread':self.server._id,'method':self.command},'null',None,{},{}
   # Cookies
   try: cookie_str = self.headers.get('Cookie').split('; ')
   except: pass
   else:
    for cookie in cookie_str:
     k,_,v = cookie.partition('=')
     try:    cookies[k] = dict(x.split('=') for x in v.split(','))
     except: cookies[k] = v
   # Partition QUERY
   (api,_,extra) = query.partition('&')
   (mod,_,fun)   = api.partition('_')
   headers['api']= api
   if extra:
     for part in extra.split("&"):
      (k,_,v) = part.partition('=')
      additional[k] = v
   headers['node'] = additional.get('node',self.server._node if not mod == 'system' else 'master')
   # Read data (if POST or other than GET)
   try:    data = self.rfile.read(int(self.headers.getheader('content-length')))
   except: data = ""
   self.__log(api,data,extra)
   try:
    args = loads(data) if len(data) > 0 else {}
    if headers['node'] == self.server._node:
     module = import_module("zdcp.rest.%s"%mod)
     module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module})
     output = dumps(getattr(module,fun,None)(args))
     headers['result'] = 'OK'
    else:
     from zdcp.core.common import rest_call
     from zdcp.SettingsContainer import SC
     try: res = rest_call("%s/%s"%(SC['nodes'][headers['node']],query),args)
     except Exception as err: raise Exception(err)
     else: output = dumps(res['data'])
     headers['result'] = res['info']['x-api-res']
   except Exception as e:
    headers.update({'result':'ERROR','args':args,'info':str(e),'xcpt':type(e).__name__})
   self.send_response(200 if headers['result'] == 'OK' else 590)
   self.send_header("Content-Type","application/json; charset=utf-8")
   self.send_header("Access-Control-Allow-Origin","*")
   for k,v in headers.iteritems():
    self.send_header("X-API-%s"%k.title(),v)
   self.end_headers()
   self.wfile.write(output)

if __name__ == '__main__':
 zdcp = Server(9000,'master')
 zdcp.start(5)
