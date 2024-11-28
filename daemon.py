#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
""" System daemon """
__author__ = "Zacharias El Banna"
from argparse import ArgumentParser
from json import load
from os import path as ospath
from sys import path as syspath, exit as sysexit, stderr
from time import sleep


parser = ArgumentParser(prog='rims',description='RIMS engine bootstrap')
parser.add_argument('-c','--config', help = 'Config file',default = '/etc/rims/rims.json', required=False)
parser.add_argument('-d','--debug', help = 'Debug output', required = False, action='store_true')
parser.add_argument('-k','--hard', help = 'Hard kill on close', required = False, action='store_true')
input = parser.parse_args()

stderr.write(f'Starting RIMS daemon\n')

if not input.config:
 parser.print_help()
 stderr.write("daemon: No config file\n")
 sysexit(1)

basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..'))
syspath.insert(1, basepath)

stderr.write(f"daemon: Opening config file {input.config}\n")
with open(input.config,'r') as file:
 config = load(file)

stderr.write("daemon: Creating RunTime\n")
try:
 from core.engine import RunTime
 rt = RunTime(config,input.debug,input.hard)
except Exception as e:
 stderr.write(f"daemon: Creating RunTime failed: {str(e)}\n")
 sysexit(2)

stderr.write("daemon: Attempting to load RunTime\n")
try:
 while not rt.load():
  sleep(10)
except Exception as e:
 stderr.write(f"daemon: Loading RunTime failed: {str(e)}\n")
 sysexit(3)

if rt.start():
 rt.wait()
 stderr.write("daemon: Clean closing of environment\n")
 sysexit(0)
else:
 rt.close()
 stderr.write("daemon: Starting environment failed\n")
 sysexit(1)
