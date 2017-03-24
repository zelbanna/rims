#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Program docstring.

Application to normalize DevHandler DB wrt to fields 


"""
__author__ = "Zacharias El Banna"
__version__ = "1.0"
__status__ = "Production"

from sys import argv

if len(argv) < 2:
 print argv[0],"<fieldname to add>"
else:
 from sys import path as syspath
 syspath.append("../..")
 from sdcp.devices.DevHandler import Devices
 devs = Devices()
 devs.add_db_position(argv[1])
 print "Added position []".format(argv[1])



