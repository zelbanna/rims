"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
def installation(aDict):
 from sdcp import PackageContainer as PC
 from sdcp.tools.installation import install
 from json import load
 from os import path as ospath
 file = ospath.join(PC.repo,PC.file)
 with open(file) as settingsfile:
  settings = load(settingsfile)
 settings['file'] = str(PC.file)
 res = install(settings)
 ret = {'res':'OK', 'file':file, 'info':res}
 return ret
