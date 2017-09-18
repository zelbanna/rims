"""Module docstring.

Xtra Generic Library

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

################################# Generics ####################################

_debug = False

def set_debug(astate):
 global _debug
 _debug = astate

def str2hex(arg):
 try:
  return '0x{0:02x}'.format(int(arg))
 except:
  return '0x00'    

def get_results(test):
 return "success" if test else "failure"

def log_msg(amsg):
 import sdcp.PackageContainer as SC
 from time import localtime, strftime
 if _debug: print "Log: " + amsg
 with open(SC.generic_logformat, 'a') as f:
  f.write(unicode("{} : {}\n".format(strftime('%Y-%m-%d %H:%M:%S', localtime()), amsg)))

#
# Lightweight argument parser, returns a dictionary with found arguments - { arg : value }
# Requires - or -- before any argument
#
def simple_arg_parser(args):
 # args should really be the argv
 argdict = {}
 currkey = None
 for arg in args:
  if arg.startswith('-'):
   if currkey:
    argdict[currkey] = True
   currkey = arg.lstrip('-')
  else:
   if currkey:
    argdict[currkey] = arg
    currkey = None
 if currkey:
  argdict[currkey] = True
 return argdict

def pidfile_write(pidfname):
 from os import getpid
 pidfile = open(pidfname,'w')
 pidfile.write(str(getpid()))
 pidfile.close()

def pidfile_read(pidfname):
 pid = -1
 from os import path as ospath
 if ospath.isfile(pidfname):
  pidfile = open(pidfname)
  pid = pidfile.readline().strip('\n')
  pidfile.close()
 return int(pid)

def pidfile_release(pidfname):
 from os import path as ospath
 if ospath.isfile(pidfname):
  from os import remove
  remove(pidfname)

def pidfile_lock(pidfname, sleeptime):
 from time import sleep
 from os import path as ospath
 while ospath.isfile(pidfname):
  sleep(sleeptime)
 pidfile_write(pidfname) 

def file_replace(afile,old,new):
 if afile == "" or new == "" or old == "":
  return False

 filedata = None
 with open(afile, 'r') as f:
  filedata = f.read()

 filedata = filedata.replace(old,new)

 with open(afile, 'w') as f:
  f.write(filedata)
 return True
