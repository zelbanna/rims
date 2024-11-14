#!/bin/bash
#
# Redirect all libs
#
rm -fR /usr/local/sbin/rims-frontend/src;    mkdir /usr/local/sbin/rims-frontend/src;    mount -B /rims/react /usr/local/sbin/rims-frontend/src
rm -fR /usr/local/sbin/rims-frontend/build;  mkdir /usr/local/sbin/rims-frontend/build;  mount -B /rims/site  /usr/local/sbin/rims-frontend/build
rm -fR /usr/local/sbin/rims-frontend/public; mkdir /usr/local/sbin/rims-frontend/public; mount -B /rims/static /usr/local/sbin/rims-frontend/public
