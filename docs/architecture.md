# Architecture

This document describes how the engine is put together: what starts what, which
threads exist, how a request becomes a Python call, and what the node, service and
device abstractions actually are in code.

## Boot sequence

`daemon.py` is the entry point.

```
daemon.py
 ├─ argparse: -c/--config, -i/--init, -d/--debug, -k/--hard
 ├─ insert the package parent directory into sys.path (so `import rims.…` works)
 ├─ load the JSON config
 ├─ --init → seed admin user, master node row and the 'generic' device type
 ├─ RunTime(config, debug, hard)      core/engine.py
 ├─ rt.load()      retry every 10s until it returns True
 ├─ rt.start()     workers, scheduler, sockets, signal handlers
 └─ rt.wait()      block until the kill event is set
```

The retry loop around `load()` is the engine's only concession to a dependency that is
not ready: a master whose database is unreachable, or a satellite whose master is not
answering, writes `Load environment error: …` and tries again every 10 seconds,
indefinitely. It is a *wait*, not a bootstrap — the engine never creates a database,
tables or rows of its own, so a missing schema keeps the loop spinning until someone
applies `config/schema.db`. Storage is assumed to exist and to be running.

`RunTime.__init__` only builds structure; nothing moves yet. It stores the config,
derives `self.node` from `config['id']`, computes `self.path` (the package directory)
and `self.site` (`<path>/site`), creates the queue, the abort/kill events, the
`Scheduler`, an empty analytics dict, and the `DB` and InfluxDB handles. It also
normalises a few config defaults in place (`salt`, `workers`, `logging.rest`,
`logging.system`) and annotates each `site.menuitem`/`site.resource` entry with a
`type` of `module`, `frame` or `tab`.

`RunTime.load()` calls `environment(self.node)` and merges the result into
`self.nodes`, `self.services` and `self.tokens`, then schedules everything in
`config['tasks']`. `environment()` has three branches:

| Caller | Branch | Source of truth |
| --- | --- | --- |
| `environment(None)` | local summary: nodes, services, scheduled tasks, version/build | in-memory state |
| node with `config['database']` (the master) | SQL over `nodes`, `servers`, `service_types`, `users`, `user_tokens` | the database |
| node without a database | `rest_call` to `config['master']` + `/api/system/environment` | the master node |

The third branch is why a satellite node needs nothing but a config file and a token:
it learns the node table, the service table and the active user tokens from the master.
`load()` logs a warning when the master's `__build__` differs from the local one.

`RunTime.start()` creates the worker pool (`config['workers']`, default 20), the
`HouseKeeping` thread, starts the scheduler, binds the sockets (four
`SocketServer` threads per socket) and installs handlers for `SIGTERM`, `SIGINT` and
`SIGUSR1`.

`RunTime.close()` sets the abort event, flushes InfluxDB, calls `close()` on every
service that runs on this node, drains the worker queue by injecting dummy tasks
(skipped with `--hard`), closes the sockets and finally sets the kill event so
`wait()` returns.

## Threads

| Thread | Count | Role |
| --- | --- | --- |
| main | 1 | boots the engine, then blocks in `RunTime.wait()` |
| `SocketServer` | 4 per listening socket | `HTTPServer.handle_request()` loop with a 0.5s timeout; each serves `SessionHandler` |
| `Worker` | `config['workers']` | pulls `(func, api, sema, output, args, kwargs)` tuples off the queue and executes them |
| `Scheduler` | 1 | `sched.scheduler` wrapper; when an event fires it *enqueues* the task rather than running it, so scheduling never blocks |
| `HouseKeeping` | 1 | every 30 minutes: log stuck workers, drop expired tokens, force a garbage collection |

Every thread that needs state calls `RunTime.clone()`, a shallow copy of the runtime
with a **fresh `DB` instance**. That is the whole concurrency story: config, node
table and caches are shared; database connections are not. Inside `DB`, an `RLock`
serialises statements, so a thread can re-enter its own connection (nested `with
aRT.db as db`) while other threads wait.

A `DB` handle connects lazily on `__enter__` and disconnects on `__exit__` once the
last nested user has left (`_conn_waiting` back to zero), so an idle worker holds no
connection. There is no ping, no reconnect and no retry: if the server is down or has
dropped the connection, the statement raises and the API call answers `X-Code: 600`.
A failed connect also leaves the handle's bookkeeping unbalanced — see
[code review C13](code-review.md).

Signals: `SIGTERM`/`SIGINT` trigger `close()`; `SIGUSR1` triggers `module_reload()`,
which re-imports every loaded `rims.*` module. That is how code is refreshed without
dropping the process — also exposed as `POST /api/system/reload`.

## HTTP handling

`SessionHandler` (a `BaseHTTPRequestHandler`) writes the status line itself in
`header()` and always answers with `Connection: close`. It stamps every response with
`X-Powered-By: RIMS Engine <version>.<build>`.

### GET

| Path | Behaviour |
| --- | --- |
| any, with `If-None-Match` matching the current build | `304 Not Modified` |
| `/` | `301` to `index.html` |
| `/api/<module>/<function>?a=1&b=2` | API call; arguments come from `parse_qs`, so **every value is a list** |
| `/files/<key>/<rest>/<file>` | file below `config['files'][key]` |
| anything else | file below `site/`; a directory yields a generated link listing |

Static responses set `Content-type` for `js`, `css`, `html` and `txt`, plus
`Cache-Control: public, max-age=0` and a weak `ETag` of the build number — which is
why a build bump invalidates every cached asset at once.

### POST

| Path | Auth | Behaviour |
| --- | --- | --- |
| `/api/<module>/<function>` | cookie `rims` or `X-Token` | API call; body is JSON or form-urlencoded |
| `/auth` | none (this *is* the login) | login, `verify` or `destroy` a token |
| `/front` | none | portal title/message from `config['site']['portal']` |
| `/vizmap` | none (deliberately bypassed) | `api/visualize.show` or `api/device.management` for the network map |
| `/register` | `X-Token` | a satellite node registers its id and port; the master upserts the `nodes` row |

### From URL to function

`SessionHandler.api()` splits the path into module and function, then decides where
the call runs based on `X-Route` (defaulting to the local node, or `master` for the
`master` module):

* **local** — `import_module(f"rims.api.{mod}")` and call
  `getattr(module, fun)(self._rt, args)`. An unknown function resolves to
  `lambda x, y: None`, so a typo yields `null`, not a 500.
* **remote** — `rest_call` to `<nodes[route]['url']>/api/<module>/<function>` with the
  shared `X-Token`, passing the body through undecoded.

The return value is JSON-encoded as the response body. `RestException` maps to
`X-Code`/`X-Exception`/`X-Info` headers; any other exception becomes `X-Code: 600`,
plus `X-Debug-NN` traceback lines when the engine runs in debug mode.

## Authentication

Tokens are 16-character random strings held in `self.tokens` (in memory on every node)
and in the `user_tokens` table on the master, with a five-day lifetime.

* `POST /auth {username, password}` — the master hashes the password with SHA-256 and
  matches it against `users.password`. An existing token for the same user id and
  source IP is reused and refreshed; otherwise a new one is inserted. The response
  carries `token`, `id`, `alias`, `class`, `theme` and `expires`, and the frontend
  stores it in the `rims` cookie.
* `POST /auth {verify: <token>}` — validates a token and refreshes the recorded
  client IP.
* `POST /auth {destroy: <token>}` — logout; drops the token from memory and the table.
* On a non-master node, `/auth` is proxied to `config['master']` and the answer is
  cached locally.

Two credentials therefore exist side by side: user tokens (cookie `rims`, per user)
and the shared node token `config['token']` (header `X-Token`), which identifies
engine-to-engine traffic and resolves to the user id `internal`.

`HouseKeeping` expires stale tokens; the master also deletes rows older than five days
in `environment()`.

## Work queues and scheduling

The queue carries six-tuples: `(function, is_api, semaphore, log_output, args,
kwargs)`. `is_api` selects the calling convention — `func(ctx, args)` for API
functions, `func(*args, **kwargs)` for plain ones.

| Helper | Use |
| --- | --- |
| `queue_api(fun, args, sema, output)` | enqueue an API function |
| `queue_function(fun, *args, **kwargs)` | enqueue a plain function |
| `queue_semaphore(fun, sema, …)` | same, but bounded by a semaphore |
| `queue_block(fun, list)` | fan out over a list and block until all elements are done |
| `schedule_api(fun, name, delay, frequency)` | run an API function later, optionally repeating |
| `schedule_api_task(module, function, frequency, args=…)` | resolve `rims.api.<module>.<function>` by name and schedule it — this is what `config['tasks']` uses |
| `schedule_api_periodic(fun, name, frequency)` | repeating API function |
| `schedule_function(fun, name, delay, frequency, prio)` | repeating plain function |

Periodic tasks are aligned to the wall clock: `Scheduler.periodic_delay(frequency)`
returns `frequency - now % frequency`, so a 300-second task fires on every five-minute
boundary rather than 300 seconds after boot.

Worker instrumentation is intentionally cheap: `workers_active()`,
`workers_idle()`, `workers_alive()` and `queue_size()` feed
`/api/system/state_queue` and `/api/system/report`, and per-worker runtimes are only
tracked in debug mode.

## Nodes

A node is identified by `config['id']` and reachable at the URL stored in the `nodes`
table. Two mechanisms make a call node-agnostic:

* **`X-Route`** on an incoming request — the engine either handles the call or
  forwards it verbatim to the named node. The frontend uses this to talk to any node
  through the one it is connected to.
* **`RunTime.node_function(node, module, function, **kwargs)`** — returns a callable
  that is either a `functools.partial` over the local function or a partial over
  `rest_call` to the remote node. Callers cannot tell the difference, which is why
  arguments must always be keyword arguments: the REST path forwards `**kwargs` to
  `rest_call`.

A satellite node bootstraps by POSTing `/register` to the master with the shared
token; the master records `http://<client-ip>:<port>` for it.

## Services

A service is a Python module in `api/services/` plus a row in `servers` binding it to
a node. The module declares its kind with `__type__` (`NAMESERVER`, `RECURSOR`,
`DHCP`, `TSDB`, `TELEMETRY`, `INFO`), and `RunTime.reinit()` scans the directory and
upserts those into `service_types`.

Services converge on a common function vocabulary, which is what lets the UI treat
different backends alike:

| Function | Meaning |
| --- | --- |
| `start` / `stop` / `close` | lifecycle; `close` is called for every local service during engine shutdown |
| `status` | health and runtime state |
| `parameters` | expected configuration versus what is actually set |
| `sync` | push RIMS state into the backend |
| `restart` | reload the backend |
| `process` | the periodic work unit, usually scheduled from `config['tasks']` |

Implementations in this tree: PowerDNS authoritative and recursor, a database-backed
`nodns`, ISC DHCP, Kea, a dummy `nodhcp`, InfluxDB, Home Assistant, Nibe, Airthings
and an IEEE OUI importer.

## Devices

Each module in `devices/` is one device type and declares:

| Attribute | Meaning |
| --- | --- |
| `__type__` | base class of device — `network`, `os`, `hypervisor`, `pdu`, `console`, `storage`, `wifi_controller`, `controlplane`, `generic` |
| `__icon__` | icon used by the visualiser |
| `__oid__` | SNMP enterprise OID used for auto-detection |
| `Device` | the driver class, usually subclassing `devices.generic.Device` |

`Device.get_functions()` lists the operations the UI may offer for the type and
`get_data_points()` the SNMP statistics to collect. `RunTime.reinit()` (exposed as
`/api/system/reinit`) imports every module, reads those attributes and upserts
`device_types` — so registering a new driver means dropping in a file and calling
`reinit`.

At call time, `api/device.py`, `api/interface.py`, `api/fdb.py`, `api/statistics.py`
and `api/pem.py` look the type name up in the database and
`import_module(f"rims.devices.{type}")`. `Device` is a context manager, so drivers
that hold an SSH or SNMP session release it on exit:

```python
module = import_module(f"rims.devices.{info['type']}")
with getattr(module,'Device')(aRT, id, info['ip']) as dev:
 result = dev.operation('reboot')
```

`devices/detector.py` is the other half of the story: given an SNMP response it maps
enterprise OID plus system description onto a type, model and version, which is how
`device.detect_info` and `device.discover` classify unknown hosts.

## Data model

The schema is `config/schema.db` (MariaDB, InnoDB, ~32 tables). The clusters are:

* **devices** — `devices`, `device_types`, `device_models`, `device_inventory`,
  `device_statistics`, `device_pems`, `device_vm_uuid`, `interfaces`,
  `interface_alternatives`, `connections`, `fdb`
* **addressing** — `ipam_networks`, `ipam_addresses`, `ipam_reservations`, `domains`,
  `records`
* **physical** — `locations`, `racks`, `rack_info`, `pdu_info`, `console_info`,
  `inventory`
* **platform** — `nodes`, `servers`, `service_types`, `users`, `user_tokens`,
  `activities`, `activity_types`, `reservations`, `visualize`, `oui`

`tools/erd.py` renders an entity-relationship diagram from a live database into
`static/erd.pdf`.

## Observability

* `RunTime.log()` writes to `config['logging']['system']['file']`, or to stderr in
  debug mode. REST calls are logged to `config['logging']['rest']['file']` unless the
  request carries `X-Log: false`.
* `RunTime.analytics()` counts API module/function and static-file hits in memory.
* `/api/system/report` returns uptime, version, worker and queue counts, InfluxDB
  buffer state, per-thread database statement counters, mounted file directories,
  loaded modules, unhandled device OIDs and the access counters.
* `/api/system/traceback`, `/api/system/state_queue` and `/api/system/memory_objects`
  expose stack traces, stuck workers and allocated object counts for live debugging.
