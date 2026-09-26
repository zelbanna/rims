"""REST API package.

Every module in this package is a REST endpoint namespace: a request for
'/api/<module>/<function>' is served by importing 'rims.api.<module>' and calling
'<function>(aRT, aArgs)'. There is no registration step - adding a function to a
module publishes it.

Contract for an API function:

 def function(aRT, aArgs):
  '''One line on what this does

  Args:
   - id (required)
   - op (optional)

  Output:
   - status
   - data
  '''

- aRT is the engine RunTime (database, config, cluster state, queue, scheduler).
- aArgs is a dict decoded from the request body (POST) or query string (GET, where
  every value is a list).
- The return value is JSON encoded as the response body. By convention it holds
  'status' ('OK'/'NOT_OK'), 'data', 'count' and 'info' where applicable.
- Read/write functions take an 'op' argument ('update', 'delete', ...) rather than
  having a separate endpoint, and accept the literal id 'new' when creating a row.
- Docstrings are part of the product: '/api/system/rest_information' serves them to
  the UI and docs/api.md is generated from them.

Sub-packages: 'devices' for device-native APIs, 'services' for service backends.
See docs/api.md and docs/development.md.
"""
