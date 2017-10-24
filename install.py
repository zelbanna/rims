#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

from sys import exit,argv

def install_sdcp(aFile):
 from sys import path as syspath
 from os import chmod,getcwd,remove
 syspath.insert(1, './')
 from tools.settings import convertSettings
 convertSettings(aFile)
 import PackageContainer as PC
 remove("PackageContainer.py")

 for dest in [ 'index','rest', PC.generic['sitebase'] ]:
  site = "{}/{}.cgi".format(PC.generic['docroot'],dest)
  with open(site,'w') as f:
   wr = f.write
   wr("#!/usr/bin/python\n")
   wr("# -*- coding: utf-8 -*-\n")
   wr("from sys import path as syspath\n")
   wr("syspath.insert(1, '{}')\n".format(getcwd().rpartition('/')[0]))
   if dest == 'rest':
    wr("import {}.core.rest as cgi\n".format(PC.generic['sitebase']))
    wr("cgi.server()\n")
   else:
    wr("from {}.core.www import Web\n".format(PC.generic['sitebase']))
    wr("cgi = Web()\n")
    wr("cgi.server('{}')\n".format(PC.generic['sitebase']))
  chmod(site,0755)

 #
 # Final copying of files
 #
 from os import listdir
 from shutil import copy
 imagedest = "{}/images/".format(PC.generic['docroot'])
 funcdest  = "{}/".format(PC.generic['docroot'])
 for file in listdir('images'):
  copy("images/" + file, imagedest + file)
 for file in listdir('infra'):
  copy("infra/" + file, funcdest + file)
 print "\nCopied necessary files\n"

 import pip
 pip.main(['install','pymysql','gitpython'])
 print "Please install mysql.txt to complete database installation"

if __name__ == "__main__":
 from sys import argv
 if len(argv) < 2:
  print "Usage: {} <json file>".format(argv[0])
  exit(0)
 else:
  install_sdcp(argv[1])
