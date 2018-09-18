#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

ZDCP Engine

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"


from os import path as ospath
from json import loads, dumps
from importlib import import_module
from time import sleep
from sys import path as syspath, exit
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from zdcp.Settings import SC
from zdcp.core.common import DB
from zdcp.core.engine import ApiThread, WorkerThread
import socket

# Socket
threadcount = 5
port = int(SC['system']['port'])
addr = ('', port)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(addr)
sock.listen(5)

# Context vars
workers = {}
globals = {'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC,'workers':workers}
context = {'node':SC['system']['id'],'socket':sock,'address':addr,'path':ospath.join(basepath,'zdcp'),'globals':globals}

# Workers and API threads
#
if SC['system']['id'] == 'master':
 with DB() as db:
  db.do("SELECT * FROM task_jobs LEFT JOIN nodes ON task_jobs.node_id = nodes.id WHERE node = 'master'")
  tasks = db.get_rows()
else:
 from zdcp.core.common import rest_call
 tasks = rest_call("%s/api/system_task_list"%SC['system']['master'],{'node':SC['system']['id']})['data']['tasks']

for task in tasks:
 args = {'id':"P%s"%task['id'],'periodic':True,'frequency':task['frequency'],'module':task['module'],'func':task['func'],'args':loads(task['args'])}
 WorkerThread(args,SC,workers)
api_threads = [ApiThread(n,context) for n in range(threadcount)]

while len(api_threads) > 0:
 # Check if threads are still alive...
 api_threads = [a for a in api_threads if a.is_alive()]
 sleep(10)
sock.close()
print "ZDCP shutdown - no active threads(!)"
exit(1)
