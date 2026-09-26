"""Service backend package.

A service is an infrastructure function - a nameserver, a DHCP server, a time-series
database, a telemetry poller - that RIMS drives through a harmonised REST surface.
Each module here implements one backend and is reached as
'/api/services/<module>/<function>'.

Module contract:

 __type__   Service kind: NAMESERVER, RECURSOR, DHCP, TSDB, TELEMETRY or INFO.
            'RunTime.reinit()' scans this package and upserts these into the
            'service_types' table, keyed by the module filename.

Service instances are rows in the 'servers' table binding a service type to a node.
Backend credentials and endpoints come from aRT.config['services'][<name>].

Functions the engine and the UI expect, so that different backends are
interchangeable:

 start / stop   Lifecycle control.
 close          Called for every locally bound service during engine shutdown -
                flush buffers and drop sessions here.
 status         Health and runtime state.
 parameters     Expected configuration versus what the backend actually has.
 sync           Push RIMS state into the backend.
 restart        Reload the backend.
 process        The periodic work unit, usually scheduled from config['tasks'].

See docs/development.md for the full walkthrough of adding a service.
"""
