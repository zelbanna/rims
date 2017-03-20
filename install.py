#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "1.1GA"
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
sitefile  = "{}/site.cgi".format(SC.sdcp_docroot)
imagedest = "{}/images".format(SC.sdcp_docroot)
funcdest  = "{}/".format(SC.sdcp_docroot)

with open(sitefile,'w') as f:
 wr = f.write
 wr("#!/usr/bin/python\n")
 wr("# -*- coding: utf-8 -*-\n")
 wr("from sys import path as syspath\n")
 wr("syspath.insert(1, '{}')\n".format(getcwd().rpartition('/')[0]))
 wr("from sdcp.site.www import Web\n")
 wr("web = Web(aDebug = True)\n")
 wr("web.site_start()\n")
chmod(sitefile,0755)

print "ToDo: copy style and z-functions as well as entire image"
