############# RIMS - REST based Infrastructure Management System ###############

RIMS is an API first based system to manage infrastructure

The system uses a concept of nodes and servers (i.e. services on nodes).
- A node is any REST base interface to a system, all nodes have an ID and a URL
- There is a 'master' node that keeps a centralized database for all other (system) nodes.
- a Service can be DNS server, DHCP server and so on. They run on nodes (using the node REST interface for communication) or are proxied by system nodes to another, non-system, node. e.g. AWX. The latter method serves as means to harmonize functions vs service's native REST APIs.

Everything centers around the 'engine', it uses a config to bootstart itself. In addition there is a thread safe context object passed around to REST based functions. The context also provides a thread safe Database object which offers database op serialization
- The engine is a multithreaded web server serving infrastructure files, REST API and site files (and any other file using settings)
- There are worker threads waiting for tasks (or periodic functionality like status checks on devices)
- The engine routes REST calls between nodes using XHR (X-Route) or optional HTML GET attributes, which also serves some extra functionality (node = <node>, debug = true, log = true)
- When a call is made the engine looks up the appropriate module and function and feeds a de-JSON:ed argument and the context (with access to the database for instance). The return object is JSON serialized

############################## Package content ##################################
- api: backend REST system modules
- devices: contains modules for device handling 
- core: Generic lib and core (engine) modules
- tools: various tools for interaction with engine or database
- templates: various templates for tasks

################################### Guidelines ##################################

- REST functions are defined in file <file> and accepts an argument tuple, (Context, Dictionary) => def func(aRT, aArgs), they must return something that can be JSON serialized (!)
a request is routed to the function by calling URL/<api>/<file>/func with argument as dictionary (before serialization) or use the core provided node_function when requireing REST  within another function

- Devices inherit (at least) from Device class in generic and can override various functions. They will get instatiated and added to the system during install phase. an __icon__ provide visualization icon (relative the image/ directory)

################################## Good to know #################################

Run install.py with config.json (using appropriate values)

- Debian
(extended)
apt-get install libglib2.0-dev libbluetooth-dev libboost-dev libboost-thread-dev libboost-python-dev

###################################### Tools ####################################
Useful tools to save disk I/O on low wear devices:

git clone http://github.com/azlux/log2ram

mkdir -P /var/log/influxdb/wal
update WAL in influxdb to /var/log/influxdb/wal
