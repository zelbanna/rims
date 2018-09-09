# zdcp
DC Project

- devices: contains modules for device handling 
- core: Generic lib and core modules
- tools: various modules 
- site: the web frontend and ajax for driving the web gui until React
- rest: backend REST system

Run install.py with settings.json (using appropriate values)

################################## Good to know #################################
- Don't forget:
To be able to reload different services, please add something similar to /etc/sudoers (actually limit for pdns and isc-dhcp-server):
www-data ALL=(ALL) NOPASSWD: /bin/systemctl

- DataStructure through ERAlchemy:
apt-get install graphviz libgraphviz-dev
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

- Install will generate a server startup file, this one will start the backend site and REST server
