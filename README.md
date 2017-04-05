# sdcp
Small or Simple DC Project

- devices: contains modules for device handling 
- utils: various modules including the password container
- site: the web frontent and ajax for driving the web gui
- site_: site support files (jscrip, stylesheets and images)
- templates: template files for various things, to be copied to document root
-- start page (index.html)
-- cgi file to map POST/GET to various functions
-- .jsons for various functions

To start, enter sdcp directory and modify settings.json with appropriate settings
Then run install to write site cgi file

- To get a working MySQL implementation - pip install PyMySql

