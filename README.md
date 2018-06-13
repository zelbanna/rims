# zdcp
DC Project

- devices: contains modules for device handling 
- core: Generic stuff
- tools: various modules 
- site: the web frontend and ajax for driving the web gui until React
- rest: backend REST system

Run install.py with settings.json (using appropriate values)

############################### Good to know stuff #############################
- Don't forgets:
-- to be able to reload different services, please add something similar to /etc/sudoers (actually limit for pdns and isc-dhcp-server):
www-data ALL=(ALL) NOPASSWD: /bin/systemctl
-- For Apache2 - update index files, e.g.: DirectoryIndex index.cgi index.html

- DataStructure through ERAlchemy:
apt-get install graphviz libgraphviz-dev
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

