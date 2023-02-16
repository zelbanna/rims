#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
#
# Parses SEOM CSV reports for solar production and inserts into IoT TSDB...
#
from json import load
from argparse import ArgumentParser, BooleanOptionalAction
from os   import path as ospath
from sys  import exit
from datetime import datetime
from pytz import timezone
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
parser = ArgumentParser(prog='seom-parser', description = 'Program parses SEOM solar production CSVs')
parser.add_argument('file', metavar='file', help = 'CSV file')
parser.add_argument('-d','--debug', help = 'Debug mode', action = BooleanOptionalAction, default=False)
parser.add_argument('-c','--config', help = 'Config unless config.json', default='../config.json')
parser.add_argument('-b','--bucket', help = 'InfluDB bucket unless iot', default='iot')
parser.add_argument('-t','--timezone', help = 'Timezone unless Europe/Stockholm', default='Europe/Stockholm')

args = parser.parse_args()

try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), args.config))) as f:
  config = load(f)['influxdb']
except Exception as e:
 print(f'Error opening config file: {str(e)}')
 exit(1)

tzone = timezone(args.timezone)
tmpl = 'monetary,entity_id=sensor.seom value=%s %s'
records = [[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

try:
 with open (args.file, 'r', encoding = 'latin-1') as f:
  f.readline()   # Remove year header
  if len(f.readline().split(';')) < 46:   # Remove headers and check that the file seems correctly formatted
   raise Exception("Not enough commas => ';' found in file")
  for row in f:
   cols = row.split(';')
   for mon in range(1,13):
    if cols[33+mon]:
     dp = cols[33+mon].strip('\n').split('-')
     # Remove one hour since CSV hours is from 1 to 24 but in the real world clock hours goes from 0 to 23....
     dt = tzone.localize(datetime(int(dp[0]),int(dp[1]),int(dp[2]),int(cols[33])-1,0,0))
     val = '0' if not cols[10+mon] else cols[10+mon].replace(',','.')
     if args.debug:
      print(f'{str(dt)} : {int(dt.timestamp())} -> {val}')
     records[mon].append((val, int(dt.timestamp())))
except Exception as e:
 print(f'Error parsing CSV: {str(e)}')
else:
 client = InfluxDBClient(url=config['url'], token=config['token'], org=config['org'])
 try:
  with client.write_api(write_options=SYNCHRONOUS) as write_api:
   for mon in records:
    r = [tmpl%hour for hour in mon]
    write_api.write(bucket = args.bucket, write_precision = WritePrecision.S, record = r)
 except Exception as e:
  print(f'InfluxDB exception: {str(e)}')
  exit(1)
 else:
  print("Wrote file content to TSDB")
  exit(0)
