"""BlueZ bluetooth server. Heavily depends on gattool so requires all of those files.
See: https://bitbucket.org/OscarAcena/pygattlib/src/default/README.md
"""
__author__  = "Zacharias El Banna"

from time import sleep

######################################## Bluetooth ########################################
#

class Server(object):

 def __init__(self, aCTX, aAbort, aArgs):
  self._ctx = aCTX
  self._abort = aAbort
  self._args = aArgs

 def process(self):
  while not self._abort.is_set():
   sleep(1)
   pass
