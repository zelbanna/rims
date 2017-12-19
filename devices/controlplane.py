"""Module docstring.

Control Plane Device

"""
__author__  = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__  = "Production"
__type__    = "controlplane"

class Device(object):

 def __init__(self, aIP, aID = None):
  pass

 def __str__(self):
  return "Control Plane"

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass
