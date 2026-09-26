"""Engine core package.

 engine  RunTime (the engine and the context passed to every API function),
         SessionHandler (HTTP), Worker, SocketServer and HouseKeeping threads.
         Carries __version__ and __build__ for the whole system.
 common  DB (thread-safe MySQL wrapper), rest_call, RestException, Scheduler and
         the InfluxDB writer.
 genlib  Small helpers: MAC and IP conversion, ping, hostname lookup.

See docs/architecture.md.
"""
