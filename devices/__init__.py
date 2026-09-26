"""Device driver package.

One module per device type, loaded dynamically by name: given a device's type from
the 'device_types' table, callers do 'import_module(f"rims.devices.{type}")' and
instantiate its 'Device' class. Nothing in the engine hard-codes a vendor.

Module contract:

 __type__   Base class of device: network, os, hypervisor, pdu, console, storage,
            wifi_controller, controlplane or generic.
 __icon__   Icon used by the visualiser, relative to site/images.
 __oid__    SNMP enterprise OID, used for auto-detection.
 Device     The driver class, normally subclassing devices.generic.Device.

'RunTime.reinit()' ('/api/system/reinit') imports every module here, reads those
attributes plus 'Device.get_functions()' and upserts the 'device_types' table - so a
module that omits __type__ is skipped and its type can never be assigned to a device.

Device class contract:

 __init__(self, aRT, aID, aIP = None)  Resolves the management IP through
                                       'device.management' when aIP is None.
 get_functions()    classmethod. Operations the UI may offer. Each name must exist
                    as a zero-argument method, since 'api/device.function' calls it
                    as getattr(dev, op)() - except the reserved name 'manage', which
                    is a UI sentinel: react/device.jsx renders a Manage button
                    routing to the React module named by __type__, and filters the
                    name out of the per-function navigation.
 get_data_points()  classmethod. SNMP statistics to collect, as
                    (measurement, tags, name, oid) tuples - inserted into
                    'device_statistics' by 'api/statistics.lookup'.
 operation(aType)   Power and reboot control; hypervisors add vm_operation().
 configuration(aData)  Renders a configuration template for the device from the
                    row passed in and config['netconf'].

Device is a context manager, so drivers holding an SSH or SNMP session release it on
exit:

 with getattr(module,'Device')(aRT, id, ip) as dev:
  result = dev.operation('reboot')

'detector.py' is not a driver: it maps an SNMP enterprise OID plus system description
onto a type, model and version for device discovery.
"""
