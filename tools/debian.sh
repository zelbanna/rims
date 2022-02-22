#!/bin/bash
# Standalone server

groupadd -g 900 docker
useradd -g 900 -u 900 -M -s /usr/sbin/nologin docker
mkdir /var/sockets

echo "Starting installation - give root DB password on the next line and press enter"
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
apt-get install python3 python3-pip python3-pymysql python3-paramiko

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian  $(lsb_release -cs) stable"
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

docker network create --subnet=172.18.0.0/16 services
echo "Creating containers"
echo "MariaDB: 172.18.0.2"
echo "InfluxDB: 172.18.0.3 -> add to config.json"
echo "Grafana: 172.18.0.6 -> proxy to port 3000 locally"
echo "PDNS Recursor: 172.18.0.4 -> configure API and add to config.json, proxy to port 53 locally"
echo "PDNS Server: 172.18.0.5 -> configure API and add to config.json"
echo ""
echo " - press enter to continue - "
read
docker create --name=mariadb -e PUID=900 -e PGID=900 -e MYSQL_ROOT_PASSWORD=$mariadbpassword -e TZ=Europe/Stockholm -v mariadb:/config --net services --ip 172.18.0.2 --restart unless-stopped linuxserver/mariadb
docker start mariadb
docker create --name=influxdb2 --user 900:900 -p 8086:8086/tcp -v influxdb2:/var/lib/influxdb2 -v influxdb2.conf.d:/etc/influxdb2 --net services --ip 172.18.0.3 --restart unless-stopped influxdb
docker create --name=grafana --user 900:900 -p 3000:3000/tcp -v grafana:/var/lib/grafana --net services --ip 172.18.0.6 --restart unless-stopped grafana/grafana
docker create --name=pdns-server --user 900:root -v pdns-server:/etc/powerdns  -v /var/sockets/pdns-server:/var/run/pdns --net services --ip 172.18.0.5 --restart unless-stopped xddxdd/powerdns
docker create --name=pdns-recursor -p 53:53 -p 53:53/udp -v pdns-recursor:/etc/powerdns  --net services --ip 172.18.0.4 --restart unless-stopped xddxdd/powerdns-recursor
docker create --name=telegraf --user 900:900 -p 8092:8092/udp -p 8125:8125/udp -p 8094:8094/tcp -v telegraf:/etc/telegraf -v /var/run/docker.sock:/var/run/docker.sock -v /var/sockets:/var/sockets --net services --ip 172.18.0.7 --restart unless-stopped telegraf
wget https://raw.githubusercontent.com/PowerDNS/pdns/rel/rec-4.4.x/modules/gmysqlbackend/schema.mysql.sql

mysql -h 172.18.0.2 -uroot -p$mariadbpassword << `END`
CREATE DATABASE rims;
CREATE USER 'rims'@'172.18.0.1' IDENTIFIED BY 'rims';
GRANT ALL PRIVILEGES ON rims.* TO 'rims'@'172.18.0.1';
FLUSH PRIVILEGES;
`END`

mysql -h 172.18.0.2 -uroot -p$mariadbpassword << END
CREATE DATABASE pdns;
CREATE USER 'pdns'@'172.18.0.1' IDENTIFIED BY 'pdns';
GRANT ALL PRIVILEGES ON pdns.* TO pdns@172.18.0.1;
CREATE USER 'pdns'@'172.18.0.5' IDENTIFIED BY 'pdns';
GRANT ALL PRIVILEGES ON pdns.* TO pdns@172.18.0.5;
FLUSH PRIVILEGES;
END

echo "PDNS Server installation"
echo ""
echo " - press enter to continue - "
read
rm /var/lib/docker/volumes/pdns-server/_data/pdns.d/*

cat schema.mysql.sql | mysql -h 172.18.0.2 -uroot -p$mariadbpassword pdns

mysql -h 172.18.0.2 -uroot -p$mariadbpassword pdns << END
ALTER TABLE records ADD CONSTRAINT records_domain_id_ibfk FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE comments ADD CONSTRAINT comments_domain_id_ibfk FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE domainmetadata ADD CONSTRAINT domainmetadata_domain_id_ibfk FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE cryptokeys ADD CONSTRAINT cryptokeys_domain_id_ibfk FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE ON UPDATE CASCADE;
END

echo "Update"
echo "cat >> /var/lib/docker/volumes/pdns-server/_data/pdns.conf"
echo "api=yes"
echo "api-key=CHANGEME"
echo "webserver-address=172.18.0.3"
echo "webserver-allow-from=172.18.0.0/24"

echo "Create the following backend connection for PowerDNS volume (pdns-server):"
echo " >> pdns.d/pdns.local.gmysql.conf"
echo "launch+=gmysql"
echo "gmysql-host=172.18.0.2"
echo "gmysql-port=3306"
echo "gmysql-dbname=pdns"
echo "gmysql-user=pdns"
echo "gmysql-password=pdns"
echo "gmysql-dnssec=no"
echo ""
echo " - press enter to continue - "
read

echo "Update PDNS recursor"
echo "cat > /var/lib/docker/volumes/pdns-recursor/_data/recursor.conf"
echo ""
echo "api-config-dir=/etc/powerdns/recursor.d"
echo "api-key=CHANGEME"
echo "config-dir=/etc/powerdns"
echo "forward-zones="
echo "forward-zones-recurse="
echo "hint-file=/usr/share/dns/root.hints"
echo "include-dir=/etc/powerdns/recursor.d"
echo "local-address=0.0.0.0"
echo "lua-config-file=/etc/powerdns/recursor.lua"
echo "public-suffix-list-file=/usr/share/publicsuffix/public_suffix_list.dat"
echo "quiet=yes"
echo "security-poll-suffix="
echo "webserver=yes"
echo "webserver-address=172.18.0.4"
echo "webserver-allow-from=172.18.0.0/24"
echo "webserver-loglevel=normal"
echo "webserver-port=8082"
echo ""
echo " - press enter to continue - "
read
echo "Installing InfluxDB"
echo " - run setup later to create a v1 DBRP"
echo " - then create a token for RIMS API"
echo ""
echo "docker exec -it influxdb2 influx setup"
echo ""
echo "docker exec -it influxdb2 influx bucket list"
echo "docker exec -it influxdb2 influx v1 dbrp create --db rims --rp autogen --default --bucket-id <bucket_id>"


pip3 install python3-netsnmp

cd /usr/local/sbin
git init
git clone git@github.com:zelbanna/rims.git
git clone http://github.com/azlux/log2ram.git
cd
ln -s /usr/local/sbin/rims
cd rims
