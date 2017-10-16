# sdcp
Small or Simple DC Project

- devices: contains modules for device handling 
- core: Generic stuff
- tools: various modules 
- site: the web frontend (pane) and ajax for driving the web gui
- site_: site support files (jscrip, stylesheets and images)
- templates: template files for various things, to be copied to document root

To start, enter sdcp directory and copy template/settings.json (with appropriate settings)

Then run install to write site cgi files into doc-root, finally enter mysql structure (from mysql.txt) into database

- Don't forgets:
-- to be able to reload different services, please add something similar to /etc/sudoers (actually limit for pdns and isc-dhcp-server):
www-data ALL=(ALL) NOPASSWD: /bin/systemctl
-- For Apache2 - update index files, e.g.: DirectoryIndex index.cgi index.html

- Backup DB structure:
mysqldump --no-data -u xyz -p sdcp 2>&1 | grep -vE "\/\*" > mysql.txt

