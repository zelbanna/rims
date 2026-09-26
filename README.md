# RIMS — REST based Infrastructure Management System

RIMS is an API-first system for managing infrastructure: devices, IP addresses, DNS,
DHCP, racks, interfaces, VM mappings and the time-series statistics around them.
Everything the web UI can do is a REST call, and every REST call is a plain Python
function in a module under `api/`.

* Source: <https://github.com/zelbanna/rims>
* Images: <https://hub.docker.com/r/zelbanna/rims>
* Engine version: `9.5.0` (build `413`, see `core/engine.py`)
* Frontend version: `9.0.1` (see `package.json`)

## Documentation

| Document | Contents |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Engine internals, threading model, request routing, node/service/device model |
| [docs/configuration.md](docs/configuration.md) | Every key in `rims.json`, with defaults taken from the code |
| [docs/api.md](docs/api.md) | REST conventions, headers, authentication, and the full module/function inventory |
| [docs/deployment.md](docs/deployment.md) | Docker, Compose, bare metal, database bootstrap, frontend build |
| [docs/development.md](docs/development.md) | Code conventions, how to add an API module, device driver or service |
| [docs/code-review.md](docs/code-review.md) | Findings from the code review of this revision |

## Concepts

**Node** — a RIMS engine instance. Every node has an id (`config['id']`), a URL and a
row in the `nodes` table. One node is the **master**: it owns the MariaDB/MySQL
database and the user/token tables, and other nodes fetch their environment from it
over REST at startup.

**Server (service instance)** — a service running on, or proxied by, a node: a DNS
server, a DHCP server, a time-series database, a telemetry poller. Service code lives
in `api/services/` and is bound to a node through the `servers` table. Proxying lets
RIMS present one harmonised REST surface over service-native APIs (PowerDNS, ISC
DHCP, Kea, Home Assistant, InfluxDB, …).

**Device** — anything managed. Device *drivers* live in `devices/` (one module per
device type, each exposing a `Device` class) and are loaded dynamically by name from
the `device_types` table, so `api/device.py` never hard-codes a vendor.

**Engine** — the `RunTime` object in `core/engine.py`. It boots from a JSON config,
serves HTTP(S), owns the worker pool and the scheduler, and is passed to every API
function as the first argument (`aRT`) together with a thread-safe `DB` handle.

## Request flow

```
client ──HTTP──▶ SocketServer thread ──▶ SessionHandler.do_GET / do_POST
                                              │
                        ┌─── /api/<module>/<function> ─────────┐
                        │                                      │
             X-Route == this node                   X-Route == other node
                        │                                      │
      import rims.api.<module>, call                rest_call to that node's
      <function>(aRT, args) inline                  /api/<module>/<function>
```

Background work takes the same shape: the scheduler and the queue hand
`(function, args)` pairs to worker threads, each of which has its own cloned context
and database connection. See [docs/architecture.md](docs/architecture.md).

## Quick start

```bash
git clone git@github.com:zelbanna/rims.git
cd rims

# 1. database (MariaDB/MySQL), from the packaged schema
mysql -h <db-host> -u root -p < config/schema.db

# 2. configuration
cp config/rims.json.tmpl /etc/rims/rims.json   # then edit it

# 3. first run: create the admin user, master node row and generic device type
./daemon.py -c /etc/rims/rims.json --init
```

The `--init` run seeds user `admin` with password `changeme` — change it immediately.
Full instructions, including Docker and Compose, are in
[docs/deployment.md](docs/deployment.md).

The engine listens on `config['port']` (8080 in the template) for HTTP and on
`config['ssl']['port']` (8081) for HTTPS. `http://<host>:8080/` serves the built site
from `site/`, `POST /auth` logs in, and `/api/<module>/<function>` is the REST surface.

## Package layout

| Path | Contents |
| --- | --- |
| `daemon.py` | Entry point: parses arguments, loads the config, optionally seeds the DB, starts `RunTime` |
| `core/engine.py` | `RunTime`, `SessionHandler` (HTTP), `Worker`, `SocketServer`, `HouseKeeping` |
| `core/common.py` | `DB` (thread-safe MySQL wrapper), `rest_call`, `RestException`, `Scheduler`, `InfluxDB` |
| `core/genlib.py` | Small helpers: MAC/IP conversion, ping, hostname lookup |
| `api/` | REST modules — one file per domain (`device`, `ipam`, `dns`, `interface`, `rack`, `system`, …) |
| `api/devices/` | REST modules that talk to a device's own API (Avocent, ESXi, Opengear) |
| `api/services/` | Service implementations (PowerDNS, ISC DHCP, Kea, InfluxDB, Home Assistant, Nibe, Airthings, OUI, …) |
| `devices/` | Device drivers: one module per device type, each with a `Device` class |
| `tools/` | CLI utilities: `api.py` (call the REST API), `erd.py` (schema diagram), `inventory.py` |
| `templates/` | Example scheduled-task definitions to paste into `config['tasks']` |
| `config/` | `rims.json.tmpl` config template and `schema.db` database schema |
| `react/` | React sources for the dynamic part of the site |
| `static/` | Static site assets (served during frontend development) |
| `site/` | Built site served by the engine's own web server |

## Requirements

* Python 3.12 (the image is built on `python:3.12-bookworm`)
* `pymysql`, `pythonping`, `paramiko`, `influxdb_client`, `easysnmp`
  (`easysnmp` needs `libsnmp-dev` to build and `libsnmp-base`/`libsnmp40` at runtime)
* MariaDB or MySQL for the master node
* Optionally InfluxDB 2.x for statistics, Node 20+/yarn for frontend development

The package must be importable as `rims`, because modules are loaded dynamically by
absolute name (`rims.api.device`, `rims.devices.junos`). Check the repository out into
a directory called `rims` and keep its parent on `PYTHONPATH` — `daemon.py` does this
for you.

## License

GPL-3.0 — see [LICENSE](LICENSE).
