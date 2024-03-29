#!/bin/bash
# Standalone server
#

apt-get install -y yarn graphviz graphviz-dev pylint
pip3 install graphviz

cd /usr/local/sbin

apt-get remove yarn cmdtest npm
apt autoremove
apt-get install nodejs yarn

yarn create react-app rims-frontend
cd /usr/local/sbin/rims-frontend/

#
# Extra packages
yarn add @fortawesome/fontawesome-free
yarn add vis-network
yarn add vis-timeline

ln /usr/local/sbin/rims/package.json

#
# Redirect all libs
#
rm -fR src;    mkdir src;    mount -B /usr/local/sbin/rims/react /usr/local/sbin/rims-frontend/src
rm -fR build;  mkdir build;  mount -B /usr/local/sbin/rims/site /usr/local/sbin/rims-frontend/build
rm -fR public; mkdir public; mount -B /usr/local/sbin/rims/static /usr/local/sbin/rims-frontend/public
