# Development

## Code conventions

The tree has a consistent, deliberate style. `.pylintrc` encodes it; match it rather
than reformatting.

| Convention | Detail |
| --- | --- |
| Indentation | **one space per level** (`indent-string=' '` in `.pylintrc`) |
| Line length | up to 200 characters; long SQL stays on one line |
| Arguments | `a`-prefixed CamelCase for function parameters: `aRT`, `aArgs`, `aID`, `aIP`, `aNode` |
| Module locals | plain lowercase; `ret` is the conventional name for the returned dict |
| Privates | `_leading_underscore` on `RunTime` internals, `__name` for module-local helpers |
| Module metadata | `__author__`, and where relevant `__type__`, `__icon__`, `__oid__`, `__add_globals__` |
| Strings | f-strings in newer code, `%`-formatting in older; both are in use |

Run the linter with the repository configuration:

```bash
pylint --rcfile=.pylintrc core api devices tools
```

There is no test suite in this revision; `api/system.rest_explore` plus
`tools/api.py` are the practical smoke test — they import every API module and report
import errors per module.

## The `aRT` runtime object

Every API function receives the runtime as its first argument. What it offers:

| Member | Use |
| --- | --- |
| `aRT.db` | thread-safe database handle; always `with aRT.db as db:` |
| `aRT.config` | the parsed config file |
| `aRT.node`, `aRT.nodes`, `aRT.services` | cluster state |
| `aRT.log(msg)` | system log |
| `aRT.rest_call(url, **kwargs)` | outbound REST |
| `aRT.node_function(node, module, function, **kwargs)` | call a function locally or on another node, transparently |
| `aRT.queue_api / queue_function / queue_semaphore / queue_block` | hand work to the pool |
| `aRT.schedule_api / schedule_api_task / schedule_api_periodic / schedule_function` | schedule work |
| `aRT.influxdb` | time-series writer (a no-op dummy when InfluxDB is not configured) |
| `aRT.cache` | shared dict for cross-call state |
| `aRT.semaphore(size)` | bounded semaphore for fan-out |
| `aRT.report()`, `aRT.reinit()`, `aRT.module_reload()` | engine operations |

Database usage pattern:

```python
def list(aRT, aArgs):
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT id, name FROM locations ORDER BY name")
  ret['data'] = db.get_rows()
 return ret
```

`query()` returns the row count and buffers the result; `get_row()`, `get_rows()`,
`get_dict(key)` and `get_val(field)` read it. `execute()` returns affected rows and
marks the connection dirty so the context manager commits on exit. `insert_dict()` and
`update_dict()` build statements from a dict — prefer them over hand-built SQL for
writes.

Be aware that most existing SQL interpolates arguments into the statement text. That
pattern is a standing injection risk (see [code review](code-review.md)); new code
should validate or cast arguments (`int(aArgs['id'])`) rather than copy it.

## Adding an API module

1. Create `api/<name>.py`:

   ```python
   """<Name> API module. One line on what this module covers"""
   __author__ = "…"
   __add_globals__ = lambda x: globals().update(x)

   #
   #
   def list(aRT, aArgs):
    """ Function returns all <things>

    Args:
     - search (optional)

    Output:
     - count
     - data. list of <things>
    """
    ret = {}
    with aRT.db as db:
     ret['count'] = db.query("SELECT id, name FROM things")
     ret['data'] = db.get_rows()
    return ret
   ```

2. That is the whole registration step — `POST /api/<name>/list` now works, because
   `SessionHandler.api()` imports the module by name at call time.

Keep the docstring shape (`Args:` with `- name (required|optional)`, then `Output:`):
`api/system.rest_information` serves those docstrings to the UI, and
[docs/api.md](api.md) is generated from them.

Write side effects behind an `op` argument rather than a separate endpoint — the
existing modules use `info(id, op='update')` and `delete(id)`, and the React frontend
expects that shape.

## Adding a device driver

1. Create `devices/<type>.py`:

   ```python
   """<Type> Device"""
   __author__  = "…"
   __type__    = "network"          # base class: network|os|hypervisor|pdu|console|storage|…
   __icon__    = "viz-generic.png"  # visualiser icon in site/images
   __oid__     = 12345              # SNMP enterprise OID, for auto-detection

   from rims.devices.generic import Device as GenericDevice

   class Device(GenericDevice):

    @classmethod
    def get_functions(cls):
     return ['interface_list','system_info']

    @classmethod
    def get_data_points(cls):
     return [('chassis','cpu=cpu','CPU free','.1.3.6.1.4.1.…')]

    def __init__(self, aRT, aID, aIP = None):
     GenericDevice.__init__(self, aRT, aID, aIP)
   ```

2. Run `tools/api.py system/reinit` so `device_types` picks up the type, its icon, its
   OID and the function list.

Inherit from `devices/generic.py` — it resolves the management IP through
`device.management` when none is passed, provides `log()`, `ping_device()`,
`operation()`, the configuration-template renderer and the context-manager protocol.
Override `operation(aType)` for power and reboot control, and add `vm_operation()` on
hypervisors. Anything named in `get_functions()` must exist as a zero-argument method,
since `api/device.function` calls it as `getattr(dev, op)()`. The one reserved name is
`manage`: `react/device.jsx` treats it as a sentinel — it renders a Manage button that
routes to the React module named by the type's `__type__`, and filters the name out of
the generic per-function navigation — so drivers that declare it (`avocent`, `esxi`,
`opengear`, `proxmox`) implement no `manage` method.

To make a new device detectable, add a handler to `devices/detector.py` named after the
vendor and OID (`ubnt8072`, `juniper2636`, …); it receives the SNMP session, the info
dict to fill in and the split system description, and sets `type`, `model` and
`version`.

## Adding a service

1. Create `api/services/<name>.py` with `__type__` set to the service kind
   (`NAMESERVER`, `RECURSOR`, `DHCP`, `TSDB`, `TELEMETRY`, `INFO`).
2. Implement the common vocabulary so the UI can drive it generically: `start`,
   `stop`, `close`, `status`, `parameters`, `sync`, `restart` and — if it polls —
   `process`.
3. Read backend credentials from `aRT.config['services']['<name>']`.
4. Run `tools/api.py system/reinit` to register the type, then create a row in
   `servers` binding the service to a node (through the UI or `api/master.server_info`).
5. If it needs to run periodically, add it to `config['tasks']`:
   `{"module":"services.<name>","function":"process","frequency":300}`.

`close()` matters: the engine calls it for every locally bound service during
shutdown, which is where a poller flushes buffers or drops sessions.

## Working with the running engine

| Action | How |
| --- | --- |
| Reload code without restarting | `kill -USR1 <pid>` or `tools/api.py system/reload` |
| Re-register drivers and services | `tools/api.py system/reinit` |
| Inspect stack traces of all threads | `tools/api.py system/traceback` |
| Find stuck workers | `tools/api.py system/state_queue '{"timeout":30,"log":true}'` |
| Run an API function as a background task | `tools/api.py system/worker '{"module":"ipam","function":"check"}'` |
| Tail the logs through the API | `tools/api.py system/logs_get '{"count":50}'` |

`system/reload` re-imports modules in place, which picks up changed function bodies. It
does not re-read the config file or re-create the worker pool — those need a restart.

## Frontend

React sources live in `react/`, shared components in `react/infra/`. Each `menuitem` or
`resource` in `config['site']` names a module and a component (`{"module": "device",
"function": "Main"}`), which maps to `react/device.jsx` exporting `Main`. `yarn start`
runs a dev server that proxies API calls to the engine (see
[deployment](deployment.md#frontend)); `yarn build` produces the bundle that belongs in
`site/`.

Bump `__build__` in `core/engine.py` when shipping site changes: it is the `ETag` for
static assets, so without a bump clients may keep serving the previous bundle from
cache.

## Versioning

`core/engine.py` carries `__version__` and `__build__`. `RunTime.load()` compares the
local build against the master's and logs a mismatch; nodes in one cluster should run
the same build. `package.json` carries the frontend version independently.
