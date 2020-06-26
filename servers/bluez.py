"""BlueZ bluetooth server. Heavily depends on gattool so requires all of those files.
See: https://bitbucket.org/OscarAcena/pygattlib/src/default/README.md
"""
__author__  = "Zacharias El Banna"

from time import sleep
from gattlib import DiscoveryService

######################################## Bluetooth ########################################
#
# configuration / aArgs should be:
# - device
# - timeout
# - sleep
#

class Server(object):

 def __init__(self, aCTX, aAbort, aArgs):
  self._ctx = aCTX
  self._abort = aAbort
  self._args = aArgs
  self._service = DiscoveryService(aArgs.get('device','hci0'))
  self._ctx.ipc['bluez']['data'] = {}

 def process(self):
  ctx, abort, service, data = self._ctx, self._abort, self._service, ctx.ipc['bluez']['data']
  try:
   timeout, timesleep = int(self._args.get('timeout',10)), int(self._args.get('sleep',20))
  except:
   timeout, timesleep = 10, 20
  while not abort.is_set():
   try:
    discovered= service.discover(timeout)
   except Exception as e:
    ctx.log(f"BlueZ Exception: {e}")
   else:
    data.update(discovered)
   sleep(timesleep)
