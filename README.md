############# RIMS - REST based Infrastructure Management System ###############

RIMS is an API first based system to manage infrastructure: racks, pdus, consoles, devices, services etc.

The system uses a concept of nodes and servers (i.e. services on nodes).
- A node is any REST base interface to a system (e.g. openstack etc), all nodes have an ID and a URL
- There is a 'master' node that keeps a centralized database and settings for all other (system) nodes.
- There are system nodes which are registered with the master during install and fetch settings from the master
- a Service can be DNS server, DHCP server, NOTIFY (e.g. slack), and so on. They run on nodes (using the node REST interface for communication 

The structure is the following. Everything centers around the 'engine', it uses a config to bootstart itself. In addition there is a thread safe context object passed around to REST based functions. The context also provides a thread safe Database object which offers database op serialization)
- The engine is a multithreaded web server serving infrastructure files, REST API and site files (and any other file using settings)
- There are worker threads waiting for tasks (or periodic functionality like status checks on devices)
- The engine routes REST calls between nodes using optional HTML GET attributes, which also serves some extra functionality (node = <node>, debug = true, log = true)
- When a call is made the engine looks up the appropriate module and function and feeds a de-JSON:ed argument and the context (with access to the database for instance). The return object is JSON serialized and output
- The engine can register external functions to provide REST service for any module (in the path) that accepts an argument list with 2 items according to function(json_args_dictionary, context).


############################## Package content ##################################
- devices: contains modules for device handling 
- core: Generic lib and core (engine) modules
- tools: various tools for interaction with engine or database
- site: the web frontend and ajax for driving the web gui until React.JS
- rest: backend REST system modules


############################## Configuration File ###############################

{
    "db_host": "127.0.0.1", # IP address of database host - only on 'master' node
    "db_name": "rims",      # Database name - i.e. rims   - only on 'master' node
    "db_pass": "rims",      # Username for 'rims' user    - only on 'master' node
    "db_user": "rims",      # Password for 'rims' user    - only on 'master' node
    "id": "master",         # ID of node
    "master": "http://192.168.0.1:8080",   # REST interface of master node, globally reachable
    "port": 8080,           # Local port to register the engine on
    "template": "engine.init", # From templates, which engine startup file to use, .init is for old schoole /etc/init.d/ service
    "workers": 30,          # Number of worker nodes to manage tasks and threaded functions
    "theme":"blue",         # The default skin theme to be used - available in infra library, only applicable on UI nodes
    "logs": {
        "system": "/var/log/system/system.log",  # Where to output system logging
        "rest": "/var/log/system/rest.log"       # Where to output REST api logs
    }
}

################################## Good to know #################################

Run install.py with config.json (using appropriate values)

- Don't forget:
To be able to reload different services, please add something similar to /etc/sudoers (actually limit for pdns and isc-dhcp-server) unless running engine as root

- Debian
apt-get install libsnmp-dev python3-pip graphviz libgraphviz-dev

- DataStructure through ERAlchemy:
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"

- Install will generate a server engine startup file, this one will start the backend site and REST server but needs to be installed first - e.g. 'engine.init install' => rims
