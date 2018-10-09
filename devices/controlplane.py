"""Module docstring.

Control Plane Device

"""
__author__  = "Zacharias El Banna"
__version__ = "5.1GA"
__status__  = "Production"
__type__    = "controlplane"

class Device(object):

 @classmethod
 def get_functions(cls):
  return []

 def __init__(self, aIP, aSettings):
  pass

 def __str__(self):
  return "Control Plane"

 def __enter__(self):
  return self

 def __exit__(self, *ctx_info):
  pass
