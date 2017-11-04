# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def install(aFile):
 from os import chmod, getcwd, remove, listdir
 from json import load
 from shutil import copy
 import pip

 try:
  with open(aFile) as f:
   config = load(f)
  with open("PackageContainer.py",'w') as f:
   for name,category in config.iteritems():
    f.write("{}={}\n".format(name,repr(category)))
   f.write("file={}\n".format(repr(aFile)))
   f.write("repo={}\n".format(repr(getcwd())))
  print "Parsed settings and wrote PackageContainer"
 except Exception as err:
  print "Error handling settings files: {}".format(str(err))
  return 1

 import PackageContainer as PC
 remove("PackageContainer.py")

 try:
  remove("core/logger.py")
 except:
  pass
 with open("core/logger.py",'w') as f:
  f.write("def log(aMsg,aID=None):\n")
  f.write(" from time import localtime, strftime\n")
  f.write(" with open('" + PC.generic['logformat'] + "', 'w') as f:\n")
  f.write(repr("  f.write(unicode('{} ({}): {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), aID, aMsg)))")[1:-1] + "\n")
 from core.logger import log
 log("Installing SDCP with settings from {}".format(aFile))

 for dest in [ 'index','rest', PC.generic['sitebase'] ]:
  site = "{}/{}.cgi".format(PC.generic['docroot'],dest)
  with open(site,'w') as f:
   wr = f.write
   wr("#!/usr/bin/python\n")
   wr("# -*- coding: utf-8 -*-\n")
   wr("from sys import path as syspath\n")
   wr("syspath.insert(1, '{}')\n".format(getcwd().rpartition('/')[0]))
   if dest == 'rest':
    wr("from {0}.core import rest as cgi\n".format(PC.generic['sitebase']))
   else:
    wr("from {0}.core.www import Web\n".format(PC.generic['sitebase']))
    wr("cgi = Web('{}')\n".format(PC.generic['sitebase']))
   wr("cgi.server()\n")
  chmod(site,0755)

 imagedest = "{}/images/".format(PC.generic['docroot'])
 funcdest  = "{}/".format(PC.generic['docroot'])
 for file in listdir('images'):
  copy("images/" + file, imagedest + file)
 for file in listdir('infra'):
  copy("infra/" + file, funcdest + file)
 print "\nCopied necessary files\n\nInstalling necessary modules:"

 pip.main(['install','pymysql','gitpython'])

 if PC.generic.get('db'):
  from rest.device import sync_types
  res = sync_types(None)
  print "\nInserted {} device types".format(res['new'])
 
 return 0
 
