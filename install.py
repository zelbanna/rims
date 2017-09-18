#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

from sys import exit,argv
from os import chmod,getcwd
from tools.settings import convertSettings

if len(argv) < 2:
 print "Usage: {} <json settings file>".format(argv[0])
 exit(0)
else:
 convertSettings(argv[1])

import PackageContainer as PC

for dest in [ 'ajax', 'pane', 'rest' ]:
 site = "{}/{}.cgi".format(PC.generic_docroot,dest)
 with open(site,'w') as f:
  wr = f.write
  wr("#!/usr/bin/python\n")
  wr("# -*- coding: utf-8 -*-\n")
  wr("from sys import path as syspath\n")
  wr("syspath.insert(1, '{}')\n".format(getcwd().rpartition('/')[0]))
  if dest == 'rest':
   wr("import {}.core.rest as REST\n".format(PC.generic_sitebase))
   wr("REST.server()\n")
  else:
   wr("from {}.site.www import Web\n".format(PC.generic_sitebase))
   wr("web = Web()\n")
   if dest == 'ajax':
    wr("web.ajax('{}')\n".format(PC.generic_sitebase + ".site"))
   else:
    wr("web.{}()\n".format(dest))
 chmod(site,0755)

#
# Final copying of files
#
from os import listdir
from shutil import copy
imagedest = "{}/images/".format(PC.generic_docroot)
funcdest  = "{}/".format(PC.generic_docroot)
for file in listdir('site_images'):
 copy("site_images/" + file, imagedest + file)
for file in listdir('site_infra'):
 copy("site_infra/" + file, funcdest + file)

print "Copied necessary files"
print ""

import pip
pip.main(['install','pymysql'])

print "Please install mysql.txt to complete database installation"
