#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "10.5GA"
__status__ = "Production"

from subprocess import call
from os import walk,path
from sys import argv, exit

if len(argv) < 2:
 print argv[0],"<version>"
 exit(0)

for root,dirs,files in walk('.'):
 if ".git" in dirs:
  dirs.remove('.git')
 #print "Directory:",root
 for file in files:
  if file[-2:] == 'py':
   print path.join(root,file)
   call(["sed","-i","s/__version__ = "10.5GA"
