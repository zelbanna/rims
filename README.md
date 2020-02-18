############# RIMS - REST based Infrastructure Management System ###############

RIMS is an API first based system to manage infrastructure: racks, pdus, consoles, devices, services etc.

The system uses a concept of nodes and servers (i.e. services on nodes).
- A node is any REST base interface to a system, all nodes have an ID and a URL
- There is a 'master' node that keeps a centralized database for all other (system) nodes.
- a Service can be DNS server, DHCP server and so on. They run on nodes (using the node REST interface for communication) or are proxied by system nodes to another, non-system, node. e.g. AWX. The latter method serves as means to harmonize functions vs service's native REST APIs.

Everything centers around the 'engine', it uses a config to bootstart itself. In addition there is a thread safe context object passed around to REST based functions. The context also provides a thread safe Database object which offers database op serialization
- The engine is a multithreaded web server serving infrastructure files, REST API and site files (and any other file using settings)
- There are worker threads waiting for tasks (or periodic functionality like status checks on devices)
- The engine routes REST calls between nodes using XHR (X-Route) or optional HTML GET attributes, which also serves some extra functionality (node = <node>, debug = true, log = true)
- When a call is made the engine looks up the appropriate module and function and feeds a de-JSON:ed argument and the context (with access to the database for instance). The return object is JSON serialized
- The engine can register external functions to provide REST service for any module (in the path) that accepts an argument list with 2 items according to function(context, json_args_dictionary).


############################## Package content ##################################
- devices: contains modules for device handling 
- core: Generic lib and core (engine) modules
- tools: various tools for interaction with engine or database
- site: the web frontend and ajax for driving the web gui until React.JS
- rest: backend REST system modules
- templates: various templates for config, site layout, tasks

################################### Guidelines ##################################

- REST functions are defined in file <file> and accepts an argument tuple, (Context, Dictionary) => def func(aCTX, aArgs), they must return something that can be JSON serialized (!)
a request is routed to the function by calling URL/<api|external>/<file>/func with argument as dictionary (before serialization)

- Devices inherit (at least) from Device class in generic and can override various functions. They will get instatiated and added to the system during install phase. an __icon__ provide visualization icon (relative the image/ directory)

################################## Good to know #################################

Run install.py with config.json (using appropriate values)

- Don't forget:
To be able to reload different services, please add something similar to /etc/sudoers (actually limit for pdns and isc-dhcp-server)

- Debian
(extended)
apt-get install libglib2.0-dev libbluetooth-dev libboost-dev libboost-thread-dev libboost-python-dev

###################################### Tools ####################################
Useful tools to save disk I/O on low wear devices:

git clone http://github.com/azlux/log2ram

mkdir -P /var/log/influxdb/wal
update WAL in influxdb to /var/log/influxdb/wal
This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).


##################################### REACT #####################################

In the project directory, you can run:

### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (Webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### `yarn build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify
