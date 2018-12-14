#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" System engine """
__author__ = "Zacharias El Banna"
from os import path as ospath, getpid
from sys import path as syspath, argv, exit
from argparse import ArgumentParser

parser = ArgumentParser(prog='rims',description='RIMS engine bootstrap')
parser.add_argument('-c','--config', help = 'Config file',default = 'config.json', required=False)
input = parser.parse_args()

if not input.config:
 parser.print_help()
 exit(0)

from time import sleep
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)
from core.engine import Context

ctx = Context(input.config)

while not ctx.load_system():
 sleep(30)

if ctx.start():
 print(getpid())
 ctx.wait()
 exit(0)
else:
 ctx.close()
 exit(1)
