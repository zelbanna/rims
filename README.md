############# RIMS - REST based Infrastructure Management System ###############

RIMS is an API first based system to manage infrastructure

Github: https://github.com/zelbanna/rims.git
Docker: https://hub.docker.com/zelbanna/rims

git clone git@github.com:zelbanna/rims.git

The system uses a concept of nodes and servers (i.e. services on nodes).
- A node is any REST base interface to a system, all nodes have an ID and a URL
- There is a 'master' node that keeps a centralized database for all other (system) nodes.
- a Service can be DNS server, DHCP server and so on. They run on nodes (using the node REST interface for communication) or are proxied by system nodes to another, non-system, node. e.g. AWX. The latter method serves as means to harmonize functions vs service's native REST APIs.

Everything centers around the 'engine', it uses a config to bootstart itself. In addition there is a thread safe context object passed around to REST based functions. The context also provides a thread safe Database object which offers database op serialization
- The engine is a multithreaded web server serving infrastructure files, REST API and site files (and any other file using settings)
- There are worker threads waiting for tasks (or periodic functionality like status checks on devices)
- The engine routes REST calls between nodes using XHR (X-Route) or optional HTML GET attributes, which also serves some extra functionality (node = <node>, debug = true, log = true)
- When a call is made the engine looks up the appropriate module and function and feeds a de-JSON:ed argument and the context (with access to the database for instance).

############################## Package content ##################################
- api: backend REST system modules
- devices: contains modules for device handling 
- core: Generic lib and core (engine) modules
- tools: various tools for interaction with engine or database
- templates: various templates for tasks
- react: react-JS source code for dynamic piece of the site
- static: static content for the site
- site: built site content for the internal web server
