"""Device-native REST API package.

Modules here expose a device's own API (or SNMP interface) as RIMS endpoints, reached
as '/api/devices/<module>/<function>'. They follow the same contract as the rest of
the api package - 'function(aRT, aArgs)' returning a JSON-serialisable dict - and
take the managed device as a 'device_id' argument.

This is the complement to the 'rims.devices' package: modules there are drivers
loaded by device type for internal use (SNMP polling, power control, configuration
rendering), while modules here are the REST surface for device-specific operations
such as ESXi VM control or Avocent PDU slots.
"""
