#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "10.5GA"
__status__ = "Production"

from sys import exit,argv
from os import chmod,getcwd
from settings import convertSettings

if len(argv) < 2:
 print "Usage: {} <json settings file>".format(argv[0])
 exit(0)
else:
 convertSettings(argv[1])

import SettingsContainer as SC
siteajax  = "{}/ajax.cgi".format(SC.sdcp_docroot)
sitepane  = "{}/pane.cgi".format(SC.sdcp_docroot)
siterest  = "{}/rest.cgi".format(SC.sdcp_docroot)

for dest in [ 'ajax', 'pane', 'rest' ]:
 site = "{}/{}.cgi".format(SC.sdcp_docroot,dest)
 with open(site,'w') as f:
  wr = f.write
  wr("#!/usr/bin/python\n")
  wr("# -*- coding: utf-8 -*-\n")
  wr("from sys import path as syspath\n")
  wr("syspath.insert(1, '{}')\n".format(getcwd().rpartition('/')[0]))
  wr("from sdcp.site.www import Web\n")
  wr("web = Web(aDebug = True)\n")
  wr("web.{}()\n".format(dest))
 chmod(site,0755)

#
# Final copying of files
#
from os import listdir
from shutil import copy
imagedest = "{}/images/".format(SC.sdcp_docroot)
funcdest  = "{}/".format(SC.sdcp_docroot)
for file in listdir('site_images'):
 copy("site_images/" + file, imagedest + file)
for file in listdir('site_infra'):
 copy("site_infra/" + file, funcdest + file)

print "Copied necessary files"
print ""

import pip
pip.main(['install','pymysql'])

print "Please install mysql.txt to complete database installation"
