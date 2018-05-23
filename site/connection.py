"""Module docstring.

HTML5 Ajax Connection module

"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"

################################################## Connections #################################################
#
#
def list(aWeb):
 if   aWeb['op'] == 'delete':
  opres = aWeb.rest_call("connection_delete",{'id':aWeb['id'],'device_id':aWeb['device_id']})
 elif aWeb['op'] == 'discover':
  opres = aWeb.rest_call("connection_discover",{'device_id':aWeb['device_id'],'delete_nonexisting':True})
 elif aWeb['op'] == 'link':
  opres = aWeb.rest_call("connection_link",{'a_id':aWeb['id'],'b_id':aWeb['peer_connection']})
 else:
  opres = ""
 res = aWeb.rest_call("connection_list",{'device_id':aWeb['device_id']})
 print "<ARTICLE><P>Connectivity (%s)</P><DIV CLASS='controls'>"%(res['hostname'])
 print aWeb.button('reload', DIV='div_dev_data',URL='sdcp.cgi?connection_list&device_id=%s'%(aWeb['device_id']))
 print aWeb.button('add',    DIV='div_dev_data',URL='sdcp.cgi?connection_info&device_id=%s&id=new'%aWeb['device_id'])
 print aWeb.button('search', DIV='div_dev_data',URL='sdcp.cgi?connection_list&op=discover&device_id=%s'%(aWeb['device_id']), SPIN='true', MSG='Rediscover connections?')
 print "</DIV><SPAN CLASS=results>%s</SPAN>"%(opres) 
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>Peer Connection</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['id'],row['name'],row['description'],row['snmp_index'],row['peer_connection'] if not row['multipoint'] else 'multipoint')
  print aWeb.button('trash', DIV='div_dev_data',URL='sdcp.cgi?connection_list&op=delete&device_id=%s&id=%s'%(aWeb['device_id'],row['id']), MSG='Delete connection?')
  print aWeb.button('info',  DIV='div_dev_data',URL='sdcp.cgi?connection_info&device_id=%s&id=%s'%(aWeb['device_id'],row['id']))
  print aWeb.button('sync',  DIV='div_dev_data',URL='sdcp.cgi?connection_link_device&device_id=%s&id=%s&name=%s'%(aWeb['device_id'],row['id'],row['name']), TITLE='Connect')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def info(aWeb):
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("connection_info",args)['data']
 print "<ARTICLE CLASS=info STYLE='width:100%;'><P>Connection</P>"
 print "<FORM ID=connection_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=device_id VALUE='%s'>"%(data['device_id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT        NAME=name        VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP Index:</DIV><DIV CLASS=td><INPUT  NAME=snmp_index  VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['snmp_index'])
 print "<DIV CLASS=tr><DIV CLASS=td>Multipoint:</DIV><DIV CLASS=td><INPUT  NAME=multipoint  VALUE=1    TYPE=CHECKBOX %s></DIV></DIV>"%("checked" if data['multipoint'] else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Peer Connection:</DIV><DIV CLASS=td>"
 if data['peer_connection'] and data['peer_device']:
  print "<A CLASS=z-op DIV=div_dev_data URL=sdcp.cgi?connection_list&device_id=%s>%s</A>"%(data['peer_device'],data['peer_connection'])
 else:
  print "None"
 print "</DIV></DIV></DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back', DIV='div_dev_data', URL='sdcp.cgi?connection_list', FRM='connection_info_form')
 print aWeb.button('save', DIV='div_dev_data', URL='sdcp.cgi?connection_info&op=update', FRM='connection_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_dev_data', URL='sdcp.cgi?connection_list&op=delete&device_id=%s&id=%s'%(data['device_id'],data['id']), MSG='Delete connection?')
 print "</DIV></ARTICLE>"

#
#
def link_device(aWeb):
 print "<ARTICLE>"
 print "<FORM ID=connection_link>"
 print "<INPUT TYPE=HIDDEN NAME=device_id VALUE=%s>"%aWeb['device_id']
 print "<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id']
 print "<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name']
 print "Connect '%s' to device id: <INPUT CLASS='background' REQUIRED TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE='%s'>"%(aWeb['name'],aWeb.get('peer','0'))
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',    DIV='div_dev_data', URL='sdcp.cgi?connection_list&device_id=%s'%aWeb['device_id'])
 print aWeb.button('forward', DIV='div_dev_data', URL='sdcp.cgi?connection_link_interface', FRM='connection_link')
 print "</DIV></ARTICLE>"

#
#
def link_interface(aWeb):
 res = aWeb.rest_call("connection_list",{'device_id':aWeb['peer'],'sort':'name'})
 print "<ARTICLE>"
 print "<FORM ID=connection_link>"
 print "<INPUT TYPE=HIDDEN NAME=device_id VALUE=%s>"%aWeb['device_id']
 print "<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id']
 print "<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name']
 print "Connect '%s' to device id: <INPUT CLASS='background' READONLY TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE=%s> on"%(aWeb['name'],aWeb['peer'])
 print "<SELECT NAME=peer_connection>"
 for intf in res.get('data',[]):
  print "<OPTION VALUE=%s>%s (%s)</OPTION>"%(intf['id'],intf['name'],intf['description'])
 print "</SELECT>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',    DIV='div_dev_data', URL='sdcp.cgi?connection_link_device', FRM='connection_link')
 print aWeb.button('forward', DIV='div_dev_data', URL='sdcp.cgi?connection_list&op=link', FRM='connection_link')
 print "</DIV></ARTICLE>"

#
#
def network(aWeb):
 res = aWeb.rest_call("connection_network",{'device_id':aWeb['device_id']})
 nodes = ["{id:%s, label:'%s'}"%(key,val['hostname']) for key,val in res['devices'].iteritems()]
 edges = ["{from:%s, to:%s}"%(con['local_device'],con['peer_device']) for con in res['connections']]
 print "<ARTICLE><P>Device '%s' network</P><DIV CLASS=controls>"%aWeb['hostname']
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?connection_network&device_id=%s&hostname=%s'%(aWeb['device_id'],aWeb['hostname']), TITLE='Reload')
 print aWeb.button('back',   DIV='div_content_right', URL='sdcp.cgi?device_info&id=%s'%aWeb['device_id'], TITLE='Back')
 print "</DIV><DIV ID='device_network' CLASS='network'></DIV><SCRIPT>"
 print "var nodes = new vis.DataSet([%s]);"%(",".join(nodes))
 print "var edges = new vis.DataSet([%s]);"%",".join(edges)
 print "var data  = { nodes: nodes, edges: edges };"
 print "var options = {};"
 print "var network = new vis.Network(document.getElementById('device_network'), data, options);"
 print "</SCRIPT></ARTICLE>"
