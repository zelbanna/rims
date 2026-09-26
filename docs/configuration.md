# Configuration

The engine is configured by a single JSON file, passed with `-c/--config` and
defaulting to `/etc/rims/rims.json`. `config/rims.json.tmpl` is a filled-in example;
this page documents every key the code actually reads, and the default applied when it
is absent.

The file holds database credentials, the node token and SNMP communities, so
`.gitignore` excludes `*.json` from the repository on purpose. Keep it out of the
image and mount it (the Compose file mounts a named volume at `/etc/rims`).

## Core keys

| Key | Required | Default | Meaning |
| --- | --- | --- | --- |
| `id` | yes | – | This node's name. The master node is conventionally called `master` and some behaviour keys off that literal string (`/auth` and the `master` API module). |
| `master` | yes | – | Base URL of the master node. A node without `database` fetches its environment from `<master>/api/system/environment` and proxies `/auth` there. |
| `port` | no | not served | HTTP listen port. Omit to serve HTTPS only. |
| `ssl` | no | not served | HTTPS listener: `port`, `certfile`, `keyfile`, optional `password`. |
| `token` | no | `None` | Shared secret for engine-to-engine calls, sent as `X-Token`. Requests carrying it are attributed to the user `internal`, and `/register` accepts nothing else. |
| `debug` | no | `false` | Log to stderr instead of files, record per-worker runtimes, and return traceback lines as `X-Debug-NN` headers. `-d` on the command line has the same effect. |
| `workers` | no | `20` | Size of the worker thread pool. |
| `startupdelay` | no | `10` | Seconds the house-keeping thread waits before its first pass. |
| `salt` | no | `WBEUAHfO` | Read into the config, but **not currently used** by the authentication path; passwords are plain SHA-256. |
| `template` | no | – | Present in the template file but not read by any code in this revision. |
| `files` | no | `{}` | Named directories exposed read-only under `/files/<name>/`. Also listed in `/api/system/report`. |

## `database`

Required on the master; omit it on satellite nodes so they read their environment over
REST instead.

```json
"database": { "host": "10.0.0.5", "name": "rims", "username": "rims", "password": "secret" }
```

All four keys are required when the object is present. Connections are MySQL/MariaDB
via `pymysql`; each thread gets its own connection through `RunTime.clone()`.

The database and its schema must already exist — the engine creates neither. A master
whose database is unreachable retries `load()` every 10 seconds instead of starting, so
a server that comes up late is tolerated but a missing schema is not. See
[deployment](deployment.md#the-database-comes-first).

## `logging`

```json
"logging": {
  "rest":   { "enabled": true, "file": "/var/log/rims/rims.rest.log" },
  "system": { "enabled": true, "file": "/var/log/rims/rims.system.log" }
}
```

Both sub-objects default to `{"enabled": false, "file": null}`. `rest` logs one line
per API call (timestamp, endpoint, arguments, user and route; arguments are suppressed
for `system/worker`), `system` receives everything `RunTime.log()` produces. In debug
mode both go to stderr and the `file` values are ignored. A client can opt out of REST
logging for a single call with the header `X-Log: false`.

`/api/system/logs_get` tails these files and `/api/system/logs_clear` truncates them,
so the paths must be writable by the engine.

## `influxdb`

```json
"influxdb": { "url": "http://10.0.0.6:8086", "org": "infra", "bucket": "rims", "token": "…" }
```

All four keys are required when present. Without this block the engine installs
`InfluxDummy`, which accepts writes and discards them — statistics collection then
runs but stores nothing. Writes are buffered and flushed by
`api/services/influxdb.process`, which is why the template schedules it every 150
seconds.

## `snmp`

```json
"snmp": { "read": "public", "write": "private", "timeout": "500000" }
```

Used by every SNMP-based driver and by device detection. `read` and `write` are v2c
communities; `timeout` is passed to `easysnmp.Session` and defaults to `3` where the
drivers read it defensively. Device detection (`api/device.detect_info`,
`device.discover`, `device.system_info_discover`) receives this object as a whole.

## `netconf`

Credentials and site-wide values used to render device configuration templates
(`Device.configuration()`), and shown as the management username in
`api/device.info`/`extended`.

| Key | Used for |
| --- | --- |
| `username`, `password` | login shown/used in generated configuration |
| `encrypted` | pre-hashed password for configurations that take one |
| `dns`, `ntp`, `tacplus` | server addresses injected into templates |
| `anonftp` | anonymous FTP source for image transfers |

`username` and `password` are read unconditionally; the rest are optional.

## `tasks`

A list of API functions scheduled at load time. `templates/task.*.json` holds
ready-made entries.

```json
"tasks": [
  { "module": "ipam", "function": "check", "args": { "repeat": 300 } },
  { "module": "system", "function": "database_backup",
    "args": { "filename": "/var/log/rims/rims.backup" }, "frequency": 86400 },
  { "module": "services.hass", "function": "start" },
  { "module": "services.influxdb", "function": "process", "frequency": 150 }
]
```

| Key | Required | Meaning |
| --- | --- | --- |
| `module` | yes | Module below `api/`; `/` or `.` separates packages (`services.influxdb`). |
| `function` | yes | Function in that module, called as `function(aRT, args)`. |
| `args` | no | Dict passed as `aArgs`; defaults to `{}`. |
| `frequency` | no | Seconds between runs. Omitted or `0` means run once at startup. |
| `output` | no | Log the return value; defaults to the engine's debug flag. |

Periodic tasks are clock-aligned: a task with `frequency` 300 first runs at the next
five-minute boundary. A module or function that cannot be imported is logged as
`WorkerPool ERROR` and skipped — the engine still starts.

## `services`

One entry per service backend that runs on, or is proxied by, this node. The key is
the service name and its shape is defined by the module in `api/services/` that reads
it. Service *instances* are rows in the `servers` table; this block only holds the
connection details.

| Config key | Module | Keys read |
| --- | --- | --- |
| `powerdns.server` | `powerdns_server` | `url`, `key`, `nameserver`, `endpoint` |
| `powerdns.recursor` | `powerdns_recursor` | `url`, `key` |
| `nodns` | `nodns` | `file`, `endpoint` (defaults to `127.0.0.1:53`) |
| `iscdhcp` | `iscdhcp` | `active` (lease file), `static` (generated reservations), `reload` (command line) |
| `isckea` | `keadhcp` | Kea control endpoint — **note the key is `isckea`, not `keadhcp`, and the template does not show it** |
| `oui` | `oui` | `location` (URL of `oui.txt`) |
| `nibe` | `nibe` | `client_id`, `client_secret`, `redirect_uri`, `system_id`, `bucket`, `measurement`, `frequency`, `state`, `token_file` |
| `hass` | `hass` | Home Assistant URL/token plus telemetry settings |
| `airthings` | `airthings` | OAuth client credentials plus telemetry settings |

## `site`

Drives the portal. `api/portal.py` and `POST /front` read it, and `RunTime.__init__`
annotates each entry with a `type` derived from which of `module`, `frame` or `tab` it
contains.

```json
"site": {
  "portal": { "message": "Management Portal Login", "title": "Management",
              "start": "devices", "theme": "light" },
  "menuitem": { "devices": { "module": "device", "function": "Main" } },
  "resource": { "influxdb": { "tab": "http://10.0.0.6:8086" },
                "rack":     { "module": "rack", "function": "Main" } }
}
```

| Key | Meaning |
| --- | --- |
| `portal.title`, `portal.message` | Window title and login message |
| `portal.start` | `menuitem` shown after login |
| `portal.theme` | Default theme (`light`/`dark`), overridable per user |
| `menuitem.<name>` | Main navigation entry |
| `resource.<name>` | Secondary entry, listed under Resources |

Each `menuitem`/`resource` entry is one of:

* `{"module": "<react module>", "function": "Main"}` — a React component (`type: module`)
* `{"frame": "<url>"}` — embedded in an iframe (`type: frame`)
* `{"tab": "<url>"}` — opened in a new browser tab (`type: tab`)

The `site` block is effectively required: `POST /front`, `api/portal.*` and the local
branch of `RunTime.environment()` index `config['site']` directly and raise `KeyError`
without it. The engine logs `No site defined` at startup as a hint.

## Device driver settings

Some drivers read their own top-level block. These are not in the template:

| Key | Read by | Keys |
| --- | --- | --- |
| `esxi` | `devices/esxi.py`, `devices/proxmox.py` | `username`, `password` (SSH) |
| `ipmi` | `devices/ipmi.py` | `username`, `password` (passed to `ipmitool`) |
| `multimedia` | `api/multimedia.py` | `torrent_directory`, `media_directory`, `temp_directory` |

## Minimal examples

Master node with a database and no extras:

```json
{
 "id": "master",
 "master": "http://10.0.0.10:8080",
 "port": 8080,
 "database": { "host": "10.0.0.5", "name": "rims", "username": "rims", "password": "secret" },
 "token": "shared-node-secret",
 "site": { "portal": { "title": "Management", "start": "devices" },
           "menuitem": { "devices": { "module": "device", "function": "Main" } } }
}
```

Satellite node — no `database`, so it pulls everything from the master:

```json
{
 "id": "site-b",
 "master": "http://10.0.0.10:8080",
 "port": 8080,
 "token": "shared-node-secret",
 "snmp": { "read": "public", "write": "private" },
 "site": { "portal": { "title": "Site B", "start": "devices" },
           "menuitem": { "devices": { "module": "device", "function": "Main" } } }
}
```
