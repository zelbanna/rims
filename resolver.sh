#!/bin/bash
# cp /root/rims.bck/site/ipam.py site/ipam.py; git add site/ipam.py
# cp /root/rims.bck/rest/iscdhcp.py rest/iscdhcp.py; git add rest/iscdhcp.py

cp /root/rims.bck/templates/config.json   templates/config.json;   git add templates/config.json
cp /root/rims.bck/templates/site.json   templates/site.json;   git add templates/site.json

cp /root/rims.bck/site/opengear.py   site/opengear.py;   git add site/opengear.py
cp /root/rims.bck/site/ipam.py   site/ipam.py;   git add site/ipam.py
cp /root/rims.bck/site/system.py   site/system.py;   git add site/system.py
cp /root/rims.bck/site/esxi.py   site/esxi.py;   git add site/esxi.py
cp /root/rims.bck/site/multimedia.py   site/multimedia.py;   git add site/multimedia.py
cp /root/rims.bck/site/device.py site/device.py; git add site/device.py

cp /root/rims.bck/rest/rack.py    rest/rack.py;    git add rest/rack.py
cp /root/rims.bck/rest/location.py    rest/location.py;    git add rest/location.py
cp /root/rims.bck/rest/iscdhcp.py rest/iscdhcp.py; git add rest/iscdhcp.py
cp /root/rims.bck/rest/esxi.py    rest/esxi.py;    git add rest/esxi.py
cp /root/rims.bck/rest/ipam.py    rest/ipam.py;    git add rest/ipam.py
cp /root/rims.bck/rest/device.py  rest/device.py;  git add rest/device.py
cp /root/rims.bck/rest/system.py    rest/system.py;    git add rest/system.py
cp /root/rims.bck/rest/nodns.py    rest/nodns.py;    git add rest/nodns.py
cp /root/rims.bck/rest/powerdns.py    rest/powerdns.py;    git add rest/powerdns.py
cp /root/rims.bck/rest/dns.py    rest/dns.py;    git add rest/dns.py
cp /root/rims.bck/rest/monitor.py    rest/monitor.py;    git add rest/monitor.py
cp /root/rims.bck/rest/master.py    rest/master.py;    git add rest/master.py
cp /root/rims.bck/rest/influxdb.py    rest/influxdb.py;    git add rest/influxdb.py

cp /root/rims.bck/core/engine.py  core/engine.py;  git add core/engine.py


git rebase --continue
