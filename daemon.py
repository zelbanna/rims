#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" System daemon """
__author__ = "Zacharias El Banna"
from os import path as ospath, getpid
from sys import path as syspath, argv, exit
from json import load
from argparse import ArgumentParser

parser = ArgumentParser(prog='rims',description='RIMS engine bootstrap')
parser.add_argument('-c','--config', help = 'Config file',default = 'config.json', required=False)
parser.add_argument('-d','--debug', help = 'Debug output', required = False, action='store_true')
parserinput = parser.parse_args()

if not parserinput.config:
 parser.print_help()
 exit(0)

from time import sleep
basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)

with open(parserinput.config,'r') as file:
 config = load(file)

from core.engine import Context
ctx = Context(config,parserinput.debug)
while not ctx.load():
 sleep(30)

if ctx.start():
 print(getpid())
 ctx.wait()
 exit(0)
else:
 ctx.close()
 exit(1)
