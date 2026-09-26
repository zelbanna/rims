# Deployment

## Prerequisites

* MariaDB or MySQL reachable from the master node
* Python 3.12 with `pymysql`, `pythonping`, `paramiko`, `influxdb_client`, `easysnmp`
* `libsnmp-dev` to build `easysnmp`, `libsnmp-base` and `libsnmp40` at runtime
* Optionally InfluxDB 2.x for statistics
* Optionally Node 20+ and yarn for frontend development

## The database comes first

**The engine assumes an existing, running database.** It does not create one, it does
not create tables, and it does not carry migrations. Nothing in RIMS bootstraps
storage — `config/schema.db` has to be applied out of band before the engine is
started for the first time, and the database server has to be up and reachable
whenever the master node is running.

What that means in practice:

| Situation | What the engine does |
| --- | --- |
| Database up, schema applied | `RunTime.load()` succeeds and the engine starts |
| Database up, schema missing or incomplete | `load()` fails on the missing table, `daemon.py` writes `Load environment error: …` and **retries every 10 seconds forever** — it never bootstraps the schema, so this spins until someone applies it |
| Database not reachable yet | the same retry loop, which resolves on its own once the server answers |
| `--init` against a missing schema | fails immediately with exit code 2 — `--init` only inserts three rows, it does not create tables |
| Database dies while the engine runs | the engine stays up; every call that touches storage raises and returns `X-Code: 600` until the server is back. There is no reconnect or health check in `DB` (see [code review C13](code-review.md)) |

So the engine tolerates a database that is merely *late*, but not one that is
*missing*. Ordering matters only for the schema.

A satellite node — one with no `database` block — needs no database of its own, but it
needs a reachable master, and it behaves the same way: `load()` retries every 10
seconds until the master answers.

Neither `docker-compose.yaml` nor the image ships a database service; both assume a
MariaDB or MySQL server you run yourself, reachable from the engine's network. If you
want one in the same Compose project, add it as a service and point `config['database']
['host']` at it — then let the engine's retry loop handle the startup ordering, since
it will wait for the server on its own.

## Database

Create the schema from the packaged file. It starts with `DROP DATABASE IF EXISTS
rims`, so never run it against a populated instance:

```bash
mysql -h <db-host> -u root -p < config/schema.db
```

Then grant the engine's user access to it:

```sql
CREATE USER 'rims'@'%' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON rims.* TO 'rims'@'%';
FLUSH PRIVILEGES;
```

The schema file creates the database itself, so it needs an account that may
`CREATE DATABASE`; the engine's own user only needs rights on `rims`.

Seed the three rows the engine needs with the init pass. It requires the schema to be
in place already — it only inserts into `users`, `nodes` and `device_types`:

```bash
./daemon.py -c /etc/rims/rims.json --init
```

It inserts user `admin` with the password `changeme`, the master node row from
`config['id']` and `config['master']`, and the `generic` device type. **Change the
admin password immediately** — log in and use `api/master.user_info`, or update
`users.password` with a SHA-256 hex digest of the new password.

The pass is written to be idempotent (`ON DUPLICATE KEY UPDATE`), so it is safe to
re-run against an existing schema — with one caveat: it *resets* the admin password
back to `changeme` every time, so do not use it as a routine start-up step.

Two more steps populate the type tables from the code on disk, and should be repeated
after adding a driver or a service:

```bash
tools/api.py system/reinit     # upserts device_types and service_types
tools/api.py device/model_sync # aligns device_models with observed models
```

Schema upgrades are supported directly by the API: `api/mysql.diff` compares the live
schema against a schema file and `api/mysql.patch` applies the difference.
`api/system.database_backup` dumps to a file and is scheduled daily in the template
config.

## Bare metal

The package must be importable as `rims`, because modules are loaded by absolute name
(`rims.api.device`). Check the repository out into a directory called `rims`:

```bash
git clone git@github.com:zelbanna/rims.git /usr/local/sbin/rims
cp /usr/local/sbin/rims/config/rims.json.tmpl /etc/rims/rims.json
# edit /etc/rims/rims.json
mkdir -p /var/log/rims
/usr/local/sbin/rims/daemon.py -c /etc/rims/rims.json
```

`daemon.py` puts the parent directory on `sys.path` itself, so no `PYTHONPATH` is
needed as long as the directory name is `rims`.

Arguments:

| Flag | Effect |
| --- | --- |
| `-c`, `--config` | config file, default `/etc/rims/rims.json` |
| `-i`, `--init` | run the database init pass before starting |
| `-d`, `--debug` | debug mode: log to stderr, per-worker timing, tracebacks in response headers |
| `-k`, `--hard` | on shutdown, skip draining the worker queue |

Exit codes: `1` no config or failed start, `2` init or runtime construction failed,
`3` loading the environment failed. `load()` is retried every 10 seconds until it
succeeds, so a node started before its master or database will catch up on its own.

Signals: `SIGTERM`/`SIGINT` shut down gracefully (services closed, queue drained,
sockets closed); `SIGUSR1` reloads all `rims.*` modules in place.

### systemd

```ini
[Unit]
Description=RIMS engine
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/sbin/rims/daemon.py -c /etc/rims/rims.json
ExecReload=/bin/kill -USR1 $MAINPID
Restart=on-failure
KillSignal=SIGTERM

[Install]
WantedBy=multi-user.target
```

## Docker

The image bundles the package at `/rims` and the config template at `/etc/rims`, with
`daemon.py` as the entry point:

```bash
docker build -t zelbanna/rims:latest .
docker run -d --name rims \
  -p 8080:8080 -p 8081:8081 \
  -v rims:/etc/rims -v /var/log/rims:/var/log/rims \
  zelbanna/rims:latest -c /etc/rims/rims.json
```

Anything after the image name is appended to the entry point, which is how the config
path (and `--init` or `--debug`) is passed. Mount a volume at `/etc/rims` holding your
`rims.json`; the template shipped in the image is only a starting point. Ports 8080
(HTTP) and 8081 (HTTPS) are exposed, matching the template config.

## Compose

`docker-compose.yaml` runs the engine on a pre-existing external network called
`infra_net` with a fixed address, alongside the optional frontend development
container:

```bash
docker network create --subnet 172.18.0.0/16 infra_net   # once, if it does not exist
docker compose up -d daemon
```

The engine keeps its config in the named volume `rims` (mounted at `/etc/rims`) and
writes logs to the host's `/var/log/rims`. The `frontend` service is a development
convenience and is not started by `up -d daemon`; it expects the repository at
`/usr/local/sbin/rims` on the host, since it bind-mounts `react/`, `site/` and
`static/` into the container.

`docker-compose.ui.yaml` contains the frontend service on its own, for running the UI
against an engine that lives elsewhere.

## Frontend

The engine serves the pre-built site from `site/` — deploying the Python package is
enough to get the UI. Rebuild it only when changing the React sources in `react/`:

```bash
yarn install
yarn build      # emits the bundle that belongs in site/
```

`package.json` proxies API calls during `yarn start` to `http://172.18.0.80:8080`, the
engine's address in the Compose network; change it to match your engine. The
containerised alternative avoids installing Node locally:

```bash
docker build -f Dockerfile.ui -t zelbanna/rims-frontend:latest .
docker compose -f docker-compose.ui.yaml up
```

That container mounts `react/` as `src`, `static/` as `public` and `site/` as `build`,
then runs `yarn start` on port 3000 with hot reload.

Note that the engine's `ETag` for static assets is the build number in
`core/engine.py`. A new frontend bundle served by an engine whose build has not changed
can be answered with `304 Not Modified` from a client cache — bump `__build__` when
shipping site changes.

## Adding a node

1. Give the new node a config with its own `id`, the shared `token`, `master` pointing
   at the master's URL, and **no** `database` block.
2. Start it. On `load()` it fetches nodes, services and active tokens from the master.
3. Register it so the master learns its URL:

   ```bash
   curl -X POST -H "X-Token: <shared token>" \
        -d '{"id":"site-b","port":8080}' http://<master>:8080/register
   ```

   Alternatively add the row through `api/master.node_info`.

From then on any client can reach it through any node by sending `X-Route: site-b`.

## Verifying a deployment

```bash
tools/api.py system/report          # uptime, versions, workers, queue, counters
tools/api.py system/task_list       # scheduled tasks
tools/api.py system/state_queue     # workers stuck over a threshold
tools/api.py master/node_list       # what the master knows about the cluster
tools/api.py system/logs_get '{"count":30}'
```

A build mismatch between a node and its master is logged at startup
(`Build mismatch between master and node`); keep the cluster on one build, since nodes
share the API surface.
