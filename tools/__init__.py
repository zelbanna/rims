"""Command line tools.

 api.py        Call any REST endpoint from a shell, reading the node token from the
               config file: 'tools/api.py device/info '{"id":42}''.
 erd.py        Render an entity-relationship diagram of the live database schema
               into static/erd.pdf.
 inventory.py  Import inventory data from a CSV file into the database.

These are scripts, not a library; they are run directly and add the package parent
to sys.path themselves.
"""
