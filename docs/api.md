# REST API

Every REST endpoint is a Python function. The path `/api/<module>/<function>` maps
directly to `<function>(aRT, aArgs)` in `rims/api/<module>.py`, where `aRT` is the
engine runtime and `aArgs` the decoded arguments. There is no routing table and no
decorator registry: adding a function to a module publishes it.

## Calling convention

```
POST /api/device/info
Content-Type: application/json
Cookie: rims=<token>

{"id": 42}
```

| Aspect | POST | GET |
| --- | --- | --- |
| Arguments | JSON body, or `application/x-www-form-urlencoded` | query string via `parse_qs`, so **every value is a list** |
| Authentication | cookie `rims` or header `X-Token` | same |
| Attributed user | the token's user id | always `0` (see [code review](code-review.md)) |

Prefer POST with JSON. GET is convenient for probing but the list-valued arguments
mean most functions will not behave as they do over POST.

The response body is the JSON encoding of whatever the function returns. An unknown
module raises (reported through headers); an unknown *function* resolves to
`lambda x, y: None` and returns `null` with status 200.

### Request headers

| Header | Meaning |
| --- | --- |
| `Cookie: rims=<token>` | user session token from `POST /auth` |
| `X-Token: <config token>` | shared node token; identifies engine-to-engine traffic as user `internal` |
| `X-Route: <node>` | run the call on that node — the receiving engine forwards it verbatim over REST |
| `X-Log: false` | do not write this call to the REST log |
| `If-None-Match: W/"<build>"` | conditional GET for static assets; matching the build yields `304` |

### Response headers

| Header | Meaning |
| --- | --- |
| `X-Powered-By` | `RIMS Engine <version>.<build>` |
| `X-Module`, `X-Function` | what was resolved |
| `X-Route` | node that executed the call |
| `X-User-ID` | token owner, or `internal` |
| `X-Exception`, `X-Info`, `X-Args` | set when the call raised |
| `X-Debug-NN` | traceback lines, debug mode only |

The HTTP status comes from `X-Code`: `200` on success, `401` when no token matched,
`404` for an unknown path, the upstream code for a `RestException`, and `600` for any
other unhandled exception.

### Return-value conventions

Not enforced by the engine, but followed by nearly every module:

| Key | Meaning |
| --- | --- |
| `status` | `OK` / `NOT_OK` (and variants such as `NOT_OK_DEVICE`) |
| `data` | the payload: a row, a list of rows, or a dict |
| `count` | number of rows in `data` |
| `info` | error detail when `status` is not `OK` |

Functions that both read and write take an `op` argument — commonly `update`,
`delete` or a device operation — and return the stored state. A `new` id is passed as
the literal string `new` where a row is created.

## Non-API endpoints

| Endpoint | Auth | Purpose |
| --- | --- | --- |
| `POST /auth` | none | `{username, password}` to log in, `{verify: token}` to validate, `{destroy: token}` to log out |
| `POST /front` | none | portal title and login message from `config['site']['portal']` |
| `POST /vizmap` | none | network map data: `{id}` calls `visualize.show`, `{device}` calls `device.management` |
| `POST /register` | `X-Token` | a satellite node registers `{id, port}`; the master stores `http://<client-ip>:<port>` |
| `GET /` | none | `301` to `index.html` |
| `GET /<path>` | none | static file from `site/` |
| `GET /files/<name>/<path>` | none | file from `config['files'][<name>]` |

## Authentication flow

```
POST /auth {"username":"admin","password":"changeme"}
  → {"status":"OK","token":"A1B2…","id":1,"alias":"admin","class":"admin",
     "expires":"Mon, 06 Oct 2025 12:00:00 UTC","node":"master"}
```

Store the token in the `rims` cookie and send it with every subsequent call. Tokens
live five days, are reused for the same user id and source IP, and are held both in
memory on every node and in `user_tokens` on the master. On a non-master node `/auth`
is proxied to `config['master']`.

## Command line

`tools/api.py` is a thin CLI over this API — it reads the node token from the config
file and prints the response headers plus the decoded payload:

```bash
tools/api.py system/report
tools/api.py device/info '{"id":42}'
tools/api.py -n site-b interface/list '{"device_id":42}'   # route to another node
```

## Introspection

The API describes itself, which is the authoritative source when this page drifts:

* `POST /api/system/rest_explore` — every module and the functions it exports
  (optionally narrowed with `{"api": "device"}`)
* `POST /api/system/rest_information {"api":"device","function":"info"}` — the module
  and function docstrings
* `POST /api/system/report` — runtime state, versions, counters
* `POST /api/system/task_list` — scheduled tasks

## Module inventory

Generated from the function signatures and docstrings of this revision.
In the argument column, `*` marks an argument the docstring calls required and `~` one
it calls "optional required" — required in combination with others, typically for a
specific `op`.

### `device`

Device API module. This is the main device interaction module for device info, update, listing,discovery etc

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | field, search, extra, rack_id, sort, dict |  |
| `management` | id* | Retrieves basic management information (IP, URL, hostname and username). Used internally and by site and visualize JScript |
| `hostname` | id* | Retrieves hostname |
| `info` | id*, op, extra | Retrieves and updates device info (excluding rack info which is only fetched) |
| `extended` | id*, op, hostname~, ipam_id~, a_domain_id~, extra | Updates 'extended' device info (RACK info etc) |
| `rack` | device_id*, op | Provides rack information for a specific device |
| `control` | id~, user_id*, device_op~, pem_op~, pem_id~ | Provides an operational interface towards device, either using ID or IP |
| `search` | hostname~, node~ | Returns device id for device matching name conditions |
| `new` | hostname*, class, mac, ipam_network_id, ip, if_domain_id~, a_domain_id | Creates a new host and sets up IP, management interface and DNS records |
| `delete` | id* | Deletes a device, first removing all dependeing interfaces (an IPs) |
| `discover` | network_id*, a_domain_id, if_domain_id |  |
| `oids` | – | Returns unique oids found |
| `function` | id*, op*, type* |  |
| `configuration_template` | id* |  |
| `system_info_discover` | network_id, lookup | Discovers system macs and enterprise oid for devices (on a network segment) |
| `type_list` | sort | Lists currenct device types |
| `model_list` | op | Returns the current models inventory |
| `model_sync` | – | Syncs device models table with devices tables' models |
| `model_info` | id*, op, defaults_file, image_file, parameters | Provides model info. Note that name and id can only be sync:ed to the system (there is no 'new' id as new models should be detected instead ATM) |
| `model_delete` | id | Delete a specific model |
| `vm_mapping` | device_id, clear | Maps VMs on existing hypervisors using device management (!) interface MAC |
| `class_list` | type | List available device classes |
| `detect_info` | ip*, basic, decode | Does device detection and mapping |

### `devices/avocent`

Avocent REST module. Provides calls to interact with avocent PDUs

| Function | Arguments | Notes |
| --- | --- | --- |
| `update` | device_id*, slot*, unit*, text* |  |
| `info` | device_id*, op |  |
| `inventory` | device_id* |  |
| `op` | device_id*, slot*, state*, unit* |  |

### `devices/esxi`

ESXi API module. Provides interworking with ESXi device module to provide esxi VM interaction

| Function | Arguments | Notes |
| --- | --- | --- |
| `inventory` | device_id*, sort |  |
| `vm_info` | device_id*, vm_id*, op | Info returns state information for VM |
| `vm_map` | bios_uuid*, device_id~, host_id, op | Maps or retrieves VM to device ID mapping |
| `vm_op` | device_id*, vm_id*, op*, uuid | Op provides VM operation control |
| `vm_snapshot` | device_id*, vm_id*, op*, snapshot | Snapshot provides VM snapshot control |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |

### `devices/opengear`

Opengear REST module. Provides interworking with (through SNMP) opengear console server

| Function | Arguments | Notes |
| --- | --- | --- |
| `inventory` | device_id* |  |
| `info` | device_id*, op |  |

### `dns`

DNS API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `domain_list` | filter, sync |  |
| `domain_info` | id*, type*, master*, name*, server_id, op |  |
| `domain_delete` | id* | Deletes a domain from local caching and remote nameserver. All records will have no domain |
| `domain_ptr_list` | prefix | Returns matching PTR domain id's and extra server info for a prefix |
| `domain_forwarders` | – | Returns information for forwarders / recursors |
| `record_list` | type, domain_id* |  |
| `record_info` | name*, domain_id*, type*, op*, content |  |
| `record_delete` | name*, domain_id*, type |  |
| `statistics` | count | Returns statistics from all recursors |
| `sync_nameserver` | – | Synchronizes nameservers with the local cached |
| `sync_recursor` | – | Synchronizes recursors and with database/forwarders to point them to the correct nameserver |
| `sync_data` | server_id*, foreign_id* | Retrieves various data for synchronizing nameservers, data is retrieved in canonical format. Only return PTR records that fits a /24 |

### `fdb`

FDB API module. This module provides FDB interaction with network devices

| Function | Arguments | Notes |
| --- | --- | --- |
| `sync` | id*, ip, type | Retrieves switch table for a device and populate FDB table for caching |
| `list` | field, search | Retrieves switch table entries from database |
| `search` | mac* | Finds mac to host mapping |
| `check` | – | Initiate a check/fdb_sync on all network devices |

### `interface`

Interface API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | device_id, sort, filter | List interfaces for a specific device |
| `info` | interface_id*, device_id*, ipam_id, mac, connection_id, snmp_index, name, description, op, extra, record | Show or update a specific interface for a device |
| `delete` | interface_id~, interfaces~ | Delete device interfaces using either id of interface or device (the latter where interfaces are not up or bound to ip addresses) |
| `cleanup` | device_id* | Cleanup interfaces using id of device. Interfaces which doesn't have any associations |
| `addresses` | interface_id | Returns all addresses associated with interface |
| `connect` | a_id*, b_id*, disconnect, map | Connects two device interfaces simultaneously to each other, removes old interfaces before |
| `disconnect` | connection_id* | Disconnects a connection |
| `snmp` | device_id*, index | SNMP Discovery function for interfaces. Either provide info for a single interface or trying to detect new interfaces |
| `stats` | device_id*, ip | Fetches interface stats for a particular device interface(s) |
| `connection_info` | connection_id*, op, map~ | To find out connection info |
| `lldp` | device_id*, ip | To find out lldp information |
| `lldp_mapping` | device_id* | Discovers connections using lldp info |
| `clear` | device_id | Clear all interface statistics |
| `check` | networks, repeat | Initiate a status check for devices' interfaces |
| `process` | devices* | Processes a list of devices and their interfaces |
| `report` | device_id*, up, down | Updates interface status |

### `inventory`

Inventory API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | search, field~, extra, sort, dict | Retrives the inventory |
| `vendor_list` | – | Retrieves vendors in inventory |
| `info` | id, op, device_id, serial, model, license, license_key, support_contract, support_end_date, description, purchase_order, location, comments | Operates on inventory items |
| `delete` | id* | Deleted an inventory item |

### `ipam`

IPAM API module. Provides IP network and address management

| Function | Arguments | Notes |
| --- | --- | --- |
| `network_list` | – | Lists networks |
| `network_info` | id*, op, network~, mask~, gateway~, description, vrf, reverse_zone_id~, extra | Info |
| `network_delete` | id* |  |
| `network_discover` | id*, simultaneous | Discovers _new_ IP:s that answer to icmp probe within a certain network. A list of such IP:s are returned |
| `address_list` | network_id*, dict, extra | Allocation of IP addresses within a network |
| `address_info` | id*, op, ip~, network_id~, hostname~, a_domain_id~ | Manages IPAM address instance info and also updates DNS |
| `address_sanitize` | hostname | Sanitize info, e.g. hostnames, so that they will fit into DNS records |
| `address_find` | network_id* |  |
| `address_delete` | id* | Deletes an IP id |
| `clear` | device_id, network_id | Clear all interface statistics, for all or subset of ipam addresses |
| `check` | networks, repeat | Initiate a status check for all or a subset of IP:s that belongs to proper interfaces |
| `process` | addresses* | Checks all IP addresses |
| `report` | up, down | Updates addresses' status |
| `server_leases` | type* | Server_leases returns free or active server leases for DHCP servers |
| `server_macs` | server_id*, alternatives | Returns all MACs for ip addresses belonging to networks belonging to particular server |
| `reservation_list` | server_id, network_id | Retrieves allocated ip addresses for either server_id or network_id |
| `reservation_new` | – | Inserts a new reservation for address (ip) or scope of addresses (start => end) |
| `reservation_delete` | id | Deletes a reserved address (id) |

### `location`

Location API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | dict | Retrives locations |
| `info` | id*, op, name | Operates on location items |
| `delete` | id* | Deletes a location |

### `master`

Master node REST module. Provides system and DB interaction

| Function | Arguments | Notes |
| --- | --- | --- |
| `inventory` | node*, user_id | Provides inventory info for particular nodes |
| `node_list` | – |  |
| `node_info` | id*, op |  |
| `node_delete` | id* |  |
| `node_to_api` | node | Returns api for a specific node name |
| `user_list` | – |  |
| `user_encrypt` | data | Encrypts 'data' with password hash technique |
| `user_info` | id*, op, name, alias, class, email, password, theme |  |
| `user_delete` | id* |  |
| `server_list` | type |  |
| `server_info` | id* |  |
| `server_delete` | id* |  |
| `server_operation` | id*, op* | Server status sends 'op' message to server @ node and convey result. What 'op' means is server dependend |
| `activity_list` | start, mode |  |
| `activity_daily` | date, extras |  |
| `activity_info` | id*, user_id~, type_id~, event, date, time |  |
| `activity_delete` | id* |  |
| `activity_type_list` | – |  |
| `activity_type_info` | – |  |
| `activity_type_delete` | id* |  |

### `multimedia`

Multimedia API module. Provides generic control functionality

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | – |  |
| `cleanup` | – |  |
| `delete` | path*, file* |  |
| `transfer` | path*, file* |  |
| `check_srt` | filepath, path, file | Find the 'first' SRT file in a directory |
| `check_title` | filepath, path, file | Tries to determine if this is a series or movie and then how to rename the file such that it would be easy to catalog |
| `check_content` | filepath, path, file, srt | Checks file using avprobe to determine content and how to optimize file |
| `process` | filepath, path, file, name, info, title, episode | Process a media file |
| `delay_set` | original*, offset* | Sets offset in ms for file 'original' (MKV) |

### `mysql`

MYSQL API module. This module provides system support for mysql DB operations

| Function | Arguments | Notes |
| --- | --- | --- |
| `dump` | mode*, username, password, database, host | Dumps database schema or values or full database info |
| `restore` | file, username, password, host | Restores database schema or values or full database info, Caution (!) if restoring a schema there will be no/0 rows in any table in the database |
| `diff` | schema_file*, username, password, database, host | Makes a diff between current database schema and the supplied schema file |
| `patch` | schema_file*, username, password, database, host | Patches current database schema with the supplied schema file |

### `pdu`

PDU API module. Implements PDU methods

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | empty | List PDUs |

### `pem`

PEM API module. Implements PEM methods

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | device_id*, lookup | Provides PEM management for a device |
| `info` | id*, device_id~, op | Provides pem management for a PEM |
| `delete` | id* | Deletes a PEM |

### `portal`

Portal REST module. Provides node independent interaction

| Function | Arguments | Notes |
| --- | --- | --- |
| `application` | – | Using 'portal' config ('title', 'message' and title of start page...) |
| `menu` | – |  |
| `resources` | type* | Returns site information |
| `resource` | type*, title* | Returns resource href |
| `theme_list` | – | Returns a list of available themes |
| `theme_info` | theme* | Returns theme parameters |

### `rack`

Racks REST module. Rack infrastructure management, info, listing etc (of PDUs, console servers and devices)

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | sort |  |
| `info` | id*, op |  |
| `inventory` | id |  |
| `devices` | id*, sort | Devices finds device information for rack such that we can build a rack "layout" |
| `delete` | id* |  |

### `reservation`

reservation REST module. Provides basic reservation functionality for devices

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | extended |  |
| `new` | device_id*, info, shutdown, days | Creates a new reservation |
| `delete` | device_id*, user_id* | Creates a new reservation |
| `info` | device_id*, op, info, shutdown | Provides reservation info and operation |
| `extend` | device_id*, days | Extends reservation for device |
| `expiration_status` | threshold | Runs shutdown and kills power when no time left |

### `services/airthings`

Airthings API module. Implements logics to use scheduler and influxdb handler for Airthings statistics

| Function | Arguments | Notes |
| --- | --- | --- |
| `auth` | – | Provides basic authentication and returns data on success for Oauth2 Client credentials flow. There is no refresh token involved so auth has to be called periodically to populate the state |
| `get` | api*, debug | Provides a generic GET call for the airthings API. since there is only v1 api this info must be omitted in the 'api' argument |
| `process` | – | Checks airthings API, process data and queue reporting to influxDB bucket |
| `status` | type* | Check cache state and auth status |
| `sync` | id*, schedule | Refresh Oauth token, essentially call for a new one and populate the state tables |
| `restart` | id* | Reload Oauth state |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/hass`

hass API module. Implements logics to reuse scheduler and influxdb handler for statistics

| Function | Arguments | Notes |
| --- | --- | --- |
| `process` | – | Checks hass API, process data and queue reporting to influxDB bucket |
| `entity` | entity_id* | Does a simple hass entity check |
| `states` | – | Returns hass entites |
| `status` | type* | Does a simple hass check to verify working connectivity |
| `sync` | id* | Args: |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/influxdb`

InfluxDB service API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `process` | – | - expected records as lists or generators... hence no length output |
| `query` | – |  |
| `status` | type* | Leases. No OP |
| `sync` | id* | No OP |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/iscdhcp`

ISCDHCP API module. The specific ISCDHCP REST interface to reload and fetch info from ISCDHCP server.

| Function | Arguments | Notes |
| --- | --- | --- |
| `status` | binding | Leases |
| `sync` | id* | Reload the DHCP server to use updated info |
| `update` | id, mac~, ip~, network~ | Check: update specific entry |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/keadhcp`

ISC Kea API module.

| Function | Arguments | Notes |
| --- | --- | --- |
| `status` | – |  |
| `sync` | id* | Reload the DHCP server to use updated info |
| `update` | id, mac~, ip~, network~ | Check: update specific entry |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/nibe`

Nibe API module. Implements logics to use scheduler and influxdb handler for Nibe statistics

| Function | Arguments | Notes |
| --- | --- | --- |
| `bootstrap` | mode | Provides start behavior, i.e. bootstrap authentication and token handling process |
| `auth` | code*, state* | Is callback URI for phase one Oauth 2.0 authentication |
| `process` | – | Checks nibe API, process data and queue reporting to influxDB bucket |
| `get` | api*, debug | Provides a generic GET call for the nibe API. since there is only v1 api this info must be omitted in the 'api' argument |
| `status` | type* | Check cache state and auth status |
| `sync` | id*, schedule | Refresh Oauth token |
| `restart` | id* | Reload Oauth state |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/nodhcp`

NoDHCP API module. Implements dummy DHCP server

| Function | Arguments | Notes |
| --- | --- | --- |
| `status` | type* | Leases. No OP |
| `sync` | id* | No OP |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/nodns`

NoDNS API module. Backend in case no nameserver is available, only on DB node, records can be exported :-)

| Function | Arguments | Notes |
| --- | --- | --- |
| `domain_list` | – | Returns all domains by this server |
| `domain_info` | id*, name*, type*, master*, op | Provide domain info and modification |
| `domain_delete` | id* | Let local domain database management handle this, NO OP |
| `record_list` | type, domain_id | List device information where we have something -> i.e. on .local devices |
| `record_info` | name*, domain_id*, type*, op, content, ttl | If new, do a mapping of either arpa or ip, else show ip info |
| `record_delete` | domain_id*, namne*, type* | Deletes records info per type |
| `sync` | id* | Synchronize device table and recreate records, write resolv info to file |
| `status` | – | Returns server status |
| `statistics` | – | Returns server statistics |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mappings of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/oui`

OUI API module. Implements OUI sync logic

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | – | Returns a list of OUI:s |
| `info` | oui* | Retrieves OUI info from database |
| `status` | type* | No OP |
| `sync` | id*, clear | Fetch and populate OUI table |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/powerdns_recursor`

PowerDNS Recursor API module. Provides powerdns specific REST interface for recursor functions.

| Function | Arguments | Notes |
| --- | --- | --- |
| `sync` | domains | Sync domain caching with recursor forwarder |
| `status` | count | Returns recursor status - the number of forwarding zones |
| `statistics` | – | Returns recursor statistics |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `services/powerdns_server`

PowerDNS API module. Provides powerdns specific REST interface. Essentially to create a GUI management

| Function | Arguments | Notes |
| --- | --- | --- |
| `domain_list` | – | Provides a list of all domains from this server |
| `domain_info` | type*, master*, id*, name*, op | Create/update domain info |
| `domain_delete` | id* | Deletes a zone - assumes all metadata and RRs is automatically removed |
| `record_list` | domain_id*, type | Records |
| `record_info` | domain_id*, name*, type*, op, content, ttl |  |
| `record_delete` | domain_id*, namne*, type* | Deletes records info per type |
| `sync` | id* |  |
| `status` | – | Return various status elements |
| `statistics` | – | Return various status elements |
| `restart` | – | Provides restart capabilities of service |
| `parameters` | – | Provides parameter mapping of anticipated config vs actual |
| `start` | – | Provides start behavior |
| `stop` | – | Provides stop behavior |
| `close` | – | Provides closing behavior, wrapping up data and file handlers before closing |

### `statistics`

Statistics API module. Implements device statistics methods for influxDB

| Function | Arguments | Notes |
| --- | --- | --- |
| `query_interface` | device_id*, interface_id*, range | Retrieves/queries database for interface statistics, formatted to Xbps |
| `query_ddp` | device_id*, measurement*, name*, range | Retrieves/queries database for device (DDP) statistics |
| `list` | device_id*, lookup | Provides stats for a device |
| `info` | id*, device_id~, op | Provides data point management for a device |
| `delete` | id* | Deletes a data point |
| `lookup` | device_id | Looks up device type based data points |
| `check` | networks, repeat | Initiate a statistics check for all or a subset of devices' interfaces and extra data points |
| `process` | devices* | Processes a list of devices with datapoints and their interfaces |

### `system`

System functions locally available

| Function | Arguments | Notes |
| --- | --- | --- |
| `traceback` | – |  |
| `memory_objects` | – | Memory objects retrieves number of allocated memory objects |
| `state_queue` | timeout, log | Process context workers and watch for locked processes |
| `environment` | node, build | Produces non-config environment for nodes |
| `report` | – | Generates a system report |
| `reload` | – | Reloads all system modules |
| `reinit` | – | Installs new services and device type |
| `active_users` | – | Retrives active user ( wrt to tokens) with ip addresses. Pull method for syncing active users to auth server |
| `active_sync` | – | Sync authentication servers vs the token database. Pushes active users to services |
| `rest_explore` | api |  |
| `rest_information` | api*, function* | Provides easy access to docstring for api/function |
| `logs_clear` | name |  |
| `logs_get` | count, name |  |
| `file_list` | directory~, fullpath~ | List files in directory pinpointed by directory (in config at the node) or by fullpath |
| `database_backup` | filename* | Does Database Backup to file |
| `node_to_api` | node | Returns api for a specific node name |
| `worker` | module*, function*, args, frequency~, output | Instantiate a worker thread with arguments |
| `task_list` | – | Returns active task list |
| `inventory` | user_id | Takes a user_id and produce an inventory for the node, for now until user id passed into functions |

### `visualize`

Visualize API module. This module provides data for vis.js networking

| Function | Arguments | Notes |
| --- | --- | --- |
| `list` | – | Produces a list of available map/network entries |
| `delete` | id | Deletes a map |
| `show` | id~ | Get map data from name or id |
| `network` | id~, op, type*, diameter, name, options, nodes, edges | To view or update information for specific network map id or generate a network map for device id/ip |
