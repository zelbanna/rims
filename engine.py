#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP Engine

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"


from os import path as ospath
from time import sleep
from sys import path as syspath, exit
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from json import loads, dumps
from importlib import import_module
from zdcp.Settings import SC
from zdcp.core.common import DB
from zdcp.core.engine import ApiThread
import socket
threadcount = 5
port = int(SC['system']['port'])
addr = ('', port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(addr)
sock.listen(5)

workers = {}
globals = {'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC,'workers':workers}
context = {'node':SC['system']['id'],'socket':sock,'address':addr,'path':ospath.join(basepath,'zdcp'),'globals':globals}
api_threads = [ApiThread(n,context) for n in range(threadcount)]
#
# Boot up worker threads as well, add necessary global first
#
# with DB() as db:
# count = db.do("SELECT * FROM task_jobs")
# context['workers']
# 
while len(api_threads) > 0:
 # Check if threads are still alive...
 api_threads = [a for a in api_threads if a.is_alive()]
 sleep(10)
sock.close()
print "ZDCP shutdown - no active threads(!)"
exit(1)
