# Code review

Review of RIMS engine `9.5.0` build `413` (`master` at `b5d734d`), covering `core/`,
`api/`, `devices/`, `tools/`, `daemon.py` and the packaging files. Line references are
against that revision.

Four items are fixed in the branch that carries this document; they are marked
**[fixed]** and the rest are reported as-is for you to triage. That branch also adds
the `docs/` set this file belongs to and package docstrings to the previously empty
`__init__.py` files, which is where the API, device-driver and service contracts are
now written down.

## Summary

The architecture holds up well. The dynamic-dispatch design — a URL path resolving to
a module and function, device types resolving to driver modules, service types
resolving to service modules — means new devices, services and endpoints are added
without touching the engine, and `X-Route` plus `node_function()` make local and remote
execution genuinely interchangeable. The threading model is small and consistent:
clone the runtime, give each thread its own database connection, serialise statements
with a re-entrant lock. Scheduling, queueing and graceful shutdown are all handled
deliberately, and `system/report`, `system/traceback` and `system/state_queue` give
real operational insight.

The weak spots are concentrated and mostly not architectural:

* **Input reaches SQL as text.** Roughly 170 statements interpolate arguments into the
  statement string, including the unauthenticated login path. This is the most serious
  issue in the tree.
* **Static file serving is not path-constrained**, so the site handler can read files
  outside `site/`.
* **Error paths are thinner than the happy paths.** Several of them fail with a
  different exception than intended (`daemon.py` init, satellite login, `rest_call`'s
  content-type guard), so a failure surfaces as a crash or a dropped connection rather
  than the intended message.
* **The database is assumed, not managed.** The engine creates no database, no tables
  and no migrations, and its handle has no reconnect. Worse, the retry loop that waits
  for a slow database leaks a lock acquisition per attempt (C13), so the ordinary cold
  start leaves the master's handle holding a connection it will never close.
* **48 docstrings are `TBD` placeholders.** Since `system/rest_information` serves
  docstrings to the UI, they are user-visible documentation, not just comments.

## Security

### S1 — SQL injection in the unauthenticated login path (`core/engine.py:786`)

```python
if db.query(f"SELECT id, class, theme FROM users WHERE alias = '{username}' and password = '{passcode}'"):
```

`username` comes straight from the `POST /auth` JSON body, before any authentication.
`passcode` is a hex digest and safe, but `username` is not: a crafted alias closes the
quote and rewrites the statement. This is reachable by anyone who can reach the port.

The same pattern runs through the API modules — about 170 `db.query`/`db.execute`
calls build their statement with `%` or an f-string, e.g.
`"... WHERE devices.id = %s"%id` in `api/device.py:353`. Those sit behind a token, but
any authenticated user reaches them.

Fix: use `pymysql`'s parameter binding. `DB.query`/`DB.execute` already wrap
`cursor.execute`, so they can accept an argument tuple and pass it through, letting
call sites migrate incrementally. Start with `/auth`, then the endpoints that take
free-text arguments (`device.search`, `device.list`, `dns.record_*`, `ipam.address_*`).
Where binding is awkward, cast (`int(aArgs['id'])`) rather than interpolating a string.

### S2 — Path traversal in static file serving (`core/engine.py:600`)

```python
path,_,query = unquote(self.path[1:]).rpartition('/')
...
fullpath = ospath.join(self._rt.site,path,file)
```

Nothing rejects `..`, and `unquote` runs first, so `%2e%2e` works too. `GET
/../../etc/passwd` resolves outside `site/` and the handler streams whatever it finds
readable. The `files` branches (`:602`, `:606`) join user-controlled path segments the
same way under a configured directory.

Fix: resolve the candidate with `ospath.realpath` and serve it only when it is inside
the intended root:

```python
fullpath = ospath.realpath(ospath.join(self._rt.site,path,file))
if not fullpath.startswith(self._rt.site + ospath.sep):
 self.header(403,'Forbidden',0)
 return
```

### S3 — Password storage (`core/engine.py:80`, `:782`, `daemon.py:42`)

Passwords are a bare SHA-256 digest of the password with no salt and no work factor,
so the `users` table is trivially attackable with rainbow tables and identical
passwords are visible as identical hashes. `config['salt']` is defaulted into the
config at `engine.py:80` and then never read — the intent is there, unimplemented.

The init pass also seeds `admin`/`changeme` and nothing forces a change. Since
`--init` uses `ON DUPLICATE KEY UPDATE … password = '<changeme hash>'`, re-running it
on an existing installation silently resets the admin password back to the default.

Fix: move to a salted KDF (`hashlib.scrypt` or `pbkdf2_hmac` with a per-user salt
column), verify with `hmac.compare_digest`, and support the old format during
migration. Separately, make `--init` skip an existing admin row rather than resetting
its password.

### S4 — Failed login echoes the submitted password hash (`core/engine.py:805`)

```python
output['info'] = {'authentication':'…not found','username':username,'passcode':passcode}
```

The 401 body returns the SHA-256 of what the client sent. Given S3, that value *is*
the stored credential format, so it is a verifier handed to whoever sent the request —
including anyone able to read the response from a log or proxy. Drop `passcode` (and
ideally `username`) from the response.

### S5 — `/vizmap` deliberately bypasses authentication (`core/engine.py:668`)

The comment says so explicitly (`# Bypass auth for visualize`). The endpoint exposes
`visualize.show` and `device.management` — the latter returns a device's management IP,
URL, hostname and username — to unauthenticated callers, enumerable by integer id.
If it exists to let the visualiser load without a session, scope it to a signed or
read-only token rather than to no token at all.

### S6 — TLS verification disabled for outbound calls (`core/common.py:36`)

`ssl_context()` sets `check_hostname = False` and `verify_mode = CERT_NONE`, and that
context is what `RunTime.ssl` hands to outbound calls. Reasonable for appliances with
self-signed certificates, but it should be a config choice rather than the only
behaviour, and it is worth stating in the config documentation so operators know the
guarantee they do not have.

## Correctness

### C1 — Init failure path raises `NameError` **[fixed]** (`daemon.py:49`)

```python
except Exception as e:
 stderr.write(f"daemon: Init failed: {str(err)}\n")
```

`err` is undefined, so any failure during `--init` (a bad database password, an
unreachable host) is replaced by `NameError: name 'err' is not defined` and the real
cause is lost. Changed to `str(e)`.

### C2 — Init success message raises `KeyError` **[fixed]** (`daemon.py:52`)

`res['maste']` is a typo for `res['master']`. A *successful* init therefore ends in an
unhandled `KeyError` — the rows are committed, but the daemon dies before starting the
engine, so init looks like it failed. Changed to `res['master']`.

### C3 — `docker-compose.yaml` is invalid **[fixed]**

The `frontend:` block sits at column 0, making it a sibling of `services:` instead of a
service. Compose rejects the file, so `docker compose up` does not work at all.
Indented under `services:`, with the rest of the file left alone.

While there: `restart: no` parses as the boolean `false` in YAML, not the string
Compose expects, in both `docker-compose.yaml` and `docker-compose.ui.yaml`. Quoted as
`restart: "no"`.

### C4 — Failed login on a satellite node returns no response (`core/engine.py:819`)

```python
except Exception as e:
 output = {'info':e.args[0]}
 self._headers['X-Code'] = e.args[0]['code']
```

When the proxied `/auth` call to the master fails, `rest_call` raises `RestException`
whose `args[0]` is the integer code, so `e.args[0]['code']` raises `TypeError`. Nothing
catches it: it unwinds out of `auth()` and `do_POST()` into
`SocketServer.run`'s bare `except`, which drops the connection. A user typing a wrong
password on a non-master node gets a dropped connection instead of a 401.

Fix: `except RestException as e: self._headers['X-Code'] = e.code` (with the
attributes the class already provides), and keep a generic handler that still writes a
response.

### C5 — `system/active_sync` calls a method that does not exist (`api/system.py:129`)

```python
return {'function':'system_active_sync','users':aRT.auth_sync()}
```

`RunTime` has no `auth_sync`; the endpoint always fails with `X-Code: 600`. Either
implement the sync (push `self.tokens` to the services that need it) or remove the
endpoint — as it stands it is a documented capability that cannot work.

### C6 — Unrecognised content type raises the wrong exception (`core/common.py:57`)

`raise RestException(f"No recognized application type …")` passes one argument, but
`RestException.__init__` reads `args[1]`, `args[2]` and `args[3]`, so constructing it
raises `IndexError`. That is caught by the same function's generic handler and
reported as `IndexError` with code 600 — the diagnostic message never reaches the
caller. Either give the class defaults for the optional fields or raise it with the
full four-tuple.

### C7 — Missing `site` config raises instead of degrading (`core/engine.py:108`, `:672`)

`RunTime.__init__` logs `No site defined` and carries on, but three places then index
the key unconditionally:

* `:108` — `len(self.config['site'])` → `KeyError` for
  `POST /api/system/environment` without a `node` argument
* `:672` — `config['site'].get('portal')` returning `None` is passed to `dict.update`
  → `TypeError` on `POST /front`
* `api/portal.py:16`, `:29`, `:60` — same pattern for the portal endpoints

Since a node may legitimately run headless, use `config.get('site',{})` and
`.get('portal',{})` in these paths.

### C8 — API calls over GET are attributed to user 0 (`core/engine.py:589`)

`do_GET` resolves the caller's token into `token_id` and then hard-codes `0` when
calling `self.api(mod,args,0)`, so the REST log and the `X-User-ID` header credit every
GET to user 0. `do_POST` passes the real value. Pass `token_id`.

### C9 — Satellite token cache loses the user class (`core/engine.py:812`)

After a proxied login the satellite stores `{'id','alias','expires','ip'}` — no
`class`, unlike both the master's own insert (`:801`) and the entries the master ships
in `environment()`. Any code that reads `tokens[…]['class']` on a satellite (the verify
branch at `:771` does) sees a `KeyError`, and a local login silently downgrades
an entry the master supplied with a class. Add `'class': output['class']`.

### C10 — Unknown `files` key drops the connection (`core/engine.py:602`, `:606`)

`self._rt.config['files'][file]` raises `KeyError` for a name that is not configured
(and for any `/files/…` request when `files` is absent). As in C4, the exception
escapes `do_GET` and the client gets no response instead of a 404. Guard with `.get()`
and answer 404.

### C11 — `devices/ipmi.py` cannot be registered (`devices/ipmi.py`)

It defines a `Device` class but no `__type__`, `__icon__` or `__oid__`, so
`RunTime.reinit()` prints `reinit ISSUE -> ipmi` and skips it: the type never reaches
`device_types`, so no device can be given the `ipmi` type through the UI. Every other
driver declares the three attributes. (`devices/detector.py` and `devices/__init__.py`
are correctly skipped — they are helpers, not drivers.)

### C12 — Kea reads a config key that matches neither its module nor the template

`api/services/keadhcp.py:18` reads `config['services']['isckea']`, while the module is
`keadhcp` and `config/rims.json.tmpl` documents neither name. Nothing errors until the
service is used, at which point it raises `KeyError`. Pick one name (`keadhcp`, for
consistency with the `servers`/`service_types` rows built from the filename) and add it
to the template.

### C13 — `DB.connect()` failure leaks the connection lock (`core/common.py:271`)

```python
def __enter__(self):
 self.connect()
 return self

def connect(self):
 with self._wait_lock:
  self._conn_waiting += 1
 self._conn_lock.acquire()
 self.count['CONNECT'] += 1
 if not self._conn:
  self._conn = self._mods[0](host=…)
```

`connect()` increments `_conn_waiting` and acquires `_conn_lock` *before* it opens the
connection. When `pymysql.connect` raises, `__enter__` never returns, so Python does
not call `__exit__` — and `close()`, which is the only thing that decrements the
counter and releases the lock, never runs. Each failed attempt therefore leaks one
count and one un-released acquire. Reproduced with the real control flow and a stub
driver:

```
attempt 1: Can't connect to MySQL server  -> waiting=1 lock_held=True
attempt 2: Can't connect to MySQL server  -> waiting=2 lock_held=True
attempt 3: Can't connect to MySQL server  -> waiting=3 lock_held=True
after success: waiting=3 lock_held=True conn_open=True
```

This is exactly the path a normal cold start takes: `daemon.py` retries `load()` every
10 seconds while the database comes up, and each retry leaks another count on
`RunTime.db`. Once the server answers, `_conn_waiting` can never return to zero, so
`close()` stops closing the connection: that handle holds one connection open for the
life of the process and keeps the re-entrant lock owned at depth ≥ 1. Since the lock is
re-entrant and the affected handle belongs to the main thread, work continues — but the
connection is never recycled, and there is no ping or reconnect anywhere in `DB`, so
when the server eventually drops it on `wait_timeout` every statement on that handle
fails until the process restarts. A database outage after 100 failed retries also leaves
a handle whose counter needs 100 matching closes.

Fix: only account for a connection once it exists, and unwind on failure:

```python
def connect(self):
 with self._wait_lock:
  self._conn_waiting += 1
 self._conn_lock.acquire()
 self.count['CONNECT'] += 1
 try:
  if not self._conn:
   self._conn = self._mods[0](host=…)
   self._curs = self._conn.cursor()
 except Exception:
  with self._wait_lock:
   self._conn_waiting -= 1
  self._conn_lock.release()
  raise
```

Run against the same stub harness, that version keeps `waiting=0` and the lock
unowned across failures, and still closes the connection exactly once after nested
re-entry — so the re-entrancy the class relies on is preserved. It is left unapplied
here because it changes locking discipline and could not be exercised against a real
server in this environment.

A `self._conn.ping(reconnect=True)` on an existing connection would also close the gap
on dropped connections.

### C14 — Storage is assumed, never bootstrapped (`daemon.py:35`, `core/engine.py:133`)

Nothing in the tree creates a database or its tables. `--init` inserts three rows and
assumes `users`, `nodes` and `device_types` exist; `config/schema.db` has to be applied
by hand; `api/mysql.patch` can apply a schema *diff* but only to a database that is
already there. Combined with the retry loop in `daemon.py:64`, a first start against an
empty database does not fail loudly — it writes `Load environment error: …` every 10
seconds indefinitely, which reads like a connectivity problem rather than a missing
schema.

This is a documentation and operability gap rather than a defect, and it is now written
down in [deployment](deployment.md#the-database-comes-first). Two cheap improvements if
you want the engine to be more self-sufficient:

* Have `--init` detect an empty or missing schema and apply `config/schema.db` itself
  (it already holds the credentials and `CREATE DATABASE`), or at least exit with a
  message naming the missing table.
* Distinguish "cannot connect" from "connected but schema missing" in `load()`, so the
  retry loop only retries the first and fails fast on the second.

Neither `docker-compose.yaml` nor the image includes a database service, so a Compose
deployment needs an external server on `infra_net` — worth stating in the compose file
itself, since that is where an operator looks first.

### C15 — `Device.ping_device()` reads an attribute that does not exist (`devices/generic.py:57`)

```python
def ping_device(self):
 return ping(self.ip, verbose=False, count=1, timeout=1).success()
```

The management address is `self._ip` throughout the class (and exposed as `get_ip()`);
`self.ip` is defined nowhere in `devices/`, so this method raises `AttributeError` for
every driver. Latent rather than live — nothing in the tree calls it today, and
`core/genlib.ping_os()` is likewise unused — but it is published as part of the driver
base class, so the first caller inherits the bug. `self._ip` fixes it; alternatively
drop both helpers, since liveness is currently established elsewhere.

## Robustness and clarity

### R1 — `queue_block` concurrency is the opposite of its comment (`core/engine.py:455`)

```python
""" Apply function on list elements and have at most 20 concurrent workers """
nworkers = max(20,int(self.config['workers']) - 5)
```

`max` gives *at least* 20. With the template's `workers: 100` the semaphore admits 95
concurrent tasks, and since the caller then blocks acquiring all of them, a fan-out can
occupy the entire pool — including the threads that would serve HTTP work queued
behind it. `min(20, workers - 5)` matches the documented intent.

### R2 — Scheduler wake-up race (`core/common.py:214`)

```python
while not self._abort.is_set():
 self._signal.wait()
 self._internal.run()
 self._signal.clear()
```

A `set()` from `add_delayed`/`add_periodic` that lands after `run()` returns but before
`clear()` is lost, and the new event waits for the next `add_*` call to wake the
thread. Clear the signal *before* running the queue, or use a `Condition` with the
next-deadline timeout.

### R3 — 70 bare `except:` clauses

They swallow `KeyboardInterrupt` and `SystemExit` alongside real errors and hide the
cause of failures — `module_reload()` (`engine.py:318`) silently skips modules that
fail to re-import, and `SocketServer.run` discards every handler exception, which is
what turns C4 and C10 into dropped connections. Prefer `except Exception` and log at
least the exception type where the outcome is "ignore and continue".

### R4 — Diagnostics lost on the error path (`core/engine.py:739`, `:741`)

`X-Args` is set to the argument *dict*, so the header carries a Python repr, and
`X-Info` for a generic exception is `','.join(map(str,e.args))`, which can contain
characters that are not valid in a header value. `header()` catches the failure and
substitutes `X-Header-Error`, so the client loses the detail exactly when it is needed.
JSON-encode both values.

### R5 — Cosmetic: unbalanced thread name (`core/engine.py:898`)

`self.name = f"SocketServer({aName}"` — missing closing parenthesis. It shows up in
`system/report` and in log lines about stuck workers.

### R6 — `reservation.delete` docstring describes a different function **[fixed]** (`api/reservation.py:48`)

The docstring read "Function creates a new reservation" and listed `user_id
(required)`, which the function never reads. Since `system/rest_information` serves
docstrings to the UI, this was wrong documentation in the product, not just in the
source. Rewritten to describe the deletion and to list only `device_id`.

### R7 — 48 placeholder docstrings

`grep -rn TBD api core devices` finds 48 `Function docstring for … TBD` bodies,
including `ipam.network_delete`, `device.discover`, `device.function`,
`device.configuration_template`, `dns.*` and `system.rest_explore`. They are served to
the UI and are the source for the generated inventory in [api.md](api.md). Filling in
the ones on endpoints the UI calls is the cheapest documentation win in the tree.

### R8 — Config template drift (`config/rims.json.tmpl`)

* `template` is in the file but nothing reads it.
* `esxi` (`devices/esxi.py`, `devices/proxmox.py`), `ipmi` (`devices/ipmi.py`),
  `multimedia` (`api/multimedia.py`), `hass`, `airthings` and `isckea` are read by code
  but absent from the template.

Both directions are documented in [configuration.md](configuration.md), but the
template is what operators copy, so it is worth correcting there too.

### R9 — `daemon.py` shadows the `input` builtin (`daemon.py:17`)

`input = parser.parse_args()`. Harmless today, surprising later; `opts` or `args` reads
better.

### R10 — No automated tests

There is no test suite and no CI configuration. The dynamic dispatch means a typo in a
module name or a missing attribute only surfaces when the endpoint is called — C5 and
C11 are exactly that class of defect. A cheap first step needs no database: import
every module under `api/` and `devices/`, assert each driver declares `__type__`,
`__icon__` and `__oid__` and that `Device.get_functions()` names methods that exist
(excluding the reserved `manage` sentinel — a static version of this check run while
reviewing flags `avocent`, `esxi`, `opengear` and `proxmox` otherwise), and assert that
every function named in `config['tasks']` resolves. `pylint --rcfile=.pylintrc`
in CI would catch the `NameError`/`KeyError` class of bug in C1 and C2 directly.

### R11 — Root `__all__` names packages that do not exist (`__init__.py:1`)

```python
__all__ = ['api','core','device','site','tools']
```

The package is `devices`, not `device`, and `site` is a directory of built assets with
no `__init__.py`. `from rims import *` fails on both. Only a cosmetic problem today
because nothing does that, but it misdescribes the package layout — `['api','core','devices','tools']`
is the accurate list.

### R12 — `rest_explore` cannot see the sub-packages (`api/system.py:155`)

```python
restdir = ospath.abspath(ospath.join(ospath.dirname(__file__)))
for restfile in listdir(restdir):
 if restfile[-3:] == '.py':
  ret['data'].append(__analyze(restfile[0:-3]))
```

The scan is flat, so the 12 modules under `api/services/` and the 3 under
`api/devices/` never appear in the API explorer — roughly a third of the REST surface
is invisible to the tool meant to enumerate it. (`rest_information` handles them fine
when asked directly, e.g. `{"api":"services.hass","function":"status"}`.) Walking one
level deeper and reporting the dotted name would close the gap.

### R13 — `--init` never updates the master node URL (`daemon.py:46`)

```sql
INSERT nodes (node,url) VALUES('…','…') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
```

The conflict branch touches only `id`, so re-running `--init` after changing
`config['master']` leaves the old URL in the table — every node that fetches its
environment then keeps pointing at the previous address. `/register` does update the
URL on conflict (`engine.py:707`), so the two paths disagree. `ON DUPLICATE KEY UPDATE
url = '<url>'` would make init match.

### R14 — `mac_bin_to_hex` is copied five times

Identical bodies in `core/genlib.py:18`, `devices/generic.py:18`,
`devices/detector.py:7`, `devices/esxi.py:13` and `devices/unifi_switch.py:10`. The
helper already lives in `core/genlib.py`, which the drivers import from for
`strToHex`, so the four copies can import it instead.

### R15 — Dead accumulator in house keeping (`core/engine.py:964`)

`house_keeping()` builds a `remain` list of unexpired tokens and never reads it. Either
report it (a token count per pass would be useful in the log line it already writes) or
drop it.

### R16 — `environment()` docstring inverts its own condition (`core/engine.py:106`)

"…for a certain node, or itself if node is given" — the local-summary branch is the one
taken when `aNode` is *falsy*, and passing a node name goes to the database or the
master. Worth correcting since this is the method that defines what "environment" means
for the whole cluster.

### R17 — Task template disagrees with the config template

`templates/task.database_backup.json` writes to `/var/log/rims.backup` while the same
task in `config/rims.json.tmpl` uses `/var/log/rims/rims.backup` — the directory the
Compose file mounts. Copying the template as-is puts the backup somewhere the container
does not persist.

## Suggested order of work

1. S1 and S2 — the two remotely exploitable issues. S1 is pre-authentication.
2. S3 and S4 — credential handling, and the `--init` password reset.
3. C13 — the connection-lock leak, which every cold start against a slow database hits.
4. C4, C7, C10 — error paths that drop connections or crash on legitimate configurations.
5. C5, C11, C12 — endpoints and registrations that cannot work as shipped.
6. R1 — pool starvation under fan-out.
7. R7 and R8 — documentation that the product itself serves.
8. C14 and R10 — schema bootstrap and the import/attribute smoke test, to keep 5 from
   recurring.
9. The rest of the R list, cheapest first: R12 and R16 (introspection and a docstring
   that describe the system wrongly), R13 and R17 (bootstrap and template drift), then
   C15, R5, R14 and R15 as cleanups.
