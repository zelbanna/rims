#!/bin/bash
# Standalone server

mkdir /var/sockets

echo "Starting installation - please setup docker compose with infra first"
read mariadbpassword
echo "Continuing"

alias wanip='dig +short myip.opendns.com @resolver1.opendns.com'
alias su_as='su --shell=/bin/bash - '
alias tab2space='expand -i -t 1'
alias rims_reload='/etc/init.d/rims restart'
alias rims_clear='/etc/init.d/rims clear'
alias rims_mysql='mysql -urims -prims rims'

apt-get update
apt-get upgrade
apt-get install -y sudo nano net-tools git mariadb-client libsnmp-dev libxslt-dev apt-transport-https ca-certificates curl gnupg-agent software-properties-common
apt-get install python3 python3-pip

mysql -h 127.0.0.1 -uroot -p$mariadbpassword << `END`
CREATE DATABASE rims;
CREATE USER 'rims'@'%' IDENTIFIED BY 'rims';
GRANT ALL PRIVILEGES ON rims.* TO 'rims'@'%';
FLUSH PRIVILEGES;
`END`

mysql -h 127.0.0.1 -uroot -p$mariadbpassword << END
CREATE DATABASE pdns;
CREATE USER 'pdns'@'%' IDENTIFIED BY 'pdns';
GRANT ALL PRIVILEGES ON pdns.* TO pdns@'%';
FLUSH PRIVILEGES;
END

cd /usr/local/sbin
git init
git clone git@github.com:zelbanna/rims.git
# git clone http://github.com/azlux/log2ram.git
