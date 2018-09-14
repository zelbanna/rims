#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Redirector

"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

from sys import argv, path as syspath, exit

if len(argv) < 2:
 print "%s <docroot>"
 exit(1)

from os import path as ospath,chmod
basedir = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','..'))
pkgdir  = ospath.join(basedir,'zdcp')
destfile= ospath.abspath(ospath.join(argv[1],'index.cgi'))
syspath.insert(1, basedir)
from zdcp.Settings import SC

with open(destfile,'w+') as f:
 f.write('#!/usr/bin/python\n')
 f.write('# -*- coding: utf-8 -*-\n')
 f.write('print "Status: 301 Moved Permanently"\n')
 f.write('print "Location: %s/site/system_login"\n'%SC['system']['node'])
 f.write('print "\\r\\n"')
chmod(destfile,0755)
