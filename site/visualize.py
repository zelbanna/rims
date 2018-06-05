"""Module docstring.

HTML5 Ajax Visualize module

"""
__author__= "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"

#
#
def list(aWeb):
 res = aWeb.rest_call("visualize_list")
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Maps</P><DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?visualize_list', TITLE='Reload')
 print "</DIV><DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS='th maxed'>Name</DIV><DIV CLASS=th STYLE='width:50px'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for map in res['maps']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS='z-op' DIV='div_content_right' URL='sdcp.cgi?visualize_show&id=%s'>%s</A></DIV><DIV CLASS=td><DIV CLASS='controls'>"%(map['id'],map['id'],map['name'])
  print aWeb.button('configure',  DIV='div_content_right', URL='sdcp.cgi?visualize_network&type=map&id=%s'%map['id'],   TITLE='Show and Edit map') 
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("visualize_delete",{'id':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE>"%res

#
#
def show(aWeb):
 from json import dumps
 args = {'id':aWeb['id']} if aWeb['id'] else {'name':aWeb['name']}
 res = aWeb.rest_call("visualize_show",args)
 print "<ARTICLE><DIV CLASS='network' ID='div_network'></DIV><SCRIPT>"
 print "var nodes = new vis.DataSet(%s);"%dumps(res['nodes'])
 print "var edges = new vis.DataSet(%s);"%dumps(res['edges'])
 print "var options = %s;"%(dumps(res['options']))
 print "var data = {nodes:nodes, edges:edges};"
 print "var network = new vis.Network(document.getElementById('div_network'), data, options);"
 print "network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });"
 print "</SCRIPT></ARTICLE>"

#
#
def network(aWeb):
 from json import dumps
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("visualize_network",args)
 print "<ARTICLE><P>Info for %s</P><DIV CLASS=controls>"%(res['name'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?visualize_network&type=%s&id=%s'%(res['type'],res['id']))
 print aWeb.button('trash',  DIV='div_content_right', URL='sdcp.cgi?visualize_delete&id=%s'%res['id'], TITLE='Delete map', MSG='Really delete map?')
 if aWeb['type'] == 'device':
  print aWeb.button('back',   DIV='div_content_right', URL='sdcp.cgi?device_info&id=%s'%res['id'], TITLE='Return to device')
 print aWeb.button('document', onclick='network_edit()', TITLE='Enable editor')
 print aWeb.button('start',  onclick='network_start()',  TITLE='Enable physics')
 print aWeb.button('stop',   onclick='network_stop()',   TITLE='Disable physics')
 print aWeb.button('fix',    onclick='network_fixate()', TITLE='Fix node positions')
 print aWeb.button('sync',   onclick='network_sync()',   TITLE='Sync graph to config')
 print aWeb.button('save',   DIV='div_content_right', URL='sdcp.cgi?visualize_network&op=update', FRM='network_config', TITLE='Save config')
 print aWeb.button('network',DIV='div_network', OP='single', SELECTOR='.tab')
 print aWeb.button('help', HREF='http://visjs.org/docs/network/', TARGET='_blank', STYLE='float:right;', TITLE='vis.js help for configuring options/nodes/edges')
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_options'>Options</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_nodes'>Nodes</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_edges'>Edges</A>"
 print "</DIV><LABEL FOR=name>Name:</LABEL><FORM ID='network_config'><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' VALUE='%s' NAME=name><SPAN ID=result CLASS=results>%s</SPAN>"%(res['name'],res.get('result',""))
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_options'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=options NAME=options>%s</TEXTAREA></DIV>"%dumps(res['options'],indent=2)
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_nodes'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=nodes NAME=nodes>%s</TEXTAREA></DIV>"%dumps(res['nodes'],indent=2)
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_edges'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=edges NAME=edges>%s</TEXTAREA></DIV>"%dumps(res['edges'],indent=2)
 print "<INPUT TYPE=HIDDEN VALUE='%s' NAME=id>"%res['id']
 print "<INPUT TYPE=HIDDEN VALUE='%s' NAME=type>"%res['type']
 print "</FORM>"
 print "<DIV CLASS='tab network' ID='div_network'></DIV><SCRIPT>"
 print "var nodes = new vis.DataSet(%s);"%dumps(res['nodes'])
 print "var edges = new vis.DataSet(%s);"%dumps(res['edges'])
 print "var options = %s;"%(dumps(res['options']))
 print """
 var data = {nodes:nodes, edges:edges};
 var network = new vis.Network(document.getElementById('div_network'), data, options);
 network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });
 network.on('dragEnd',function(params){ 
  network.storePositions();
  $("#nodes").val(JSON.stringify(nodes.get(),undefined,2));
  $("#result").html('Moved ' + nodes.get(params.nodes[0]).label);
 });

 function network_start(){ 
  network.setOptions({ physics:true  });
  $("#result").html("Enable physics");
 };

 function network_stop(){
  network.setOptions({ physics:false });
  $("#result").html("Diable physics");
 };

 function network_edit(){
  network.setOptions({ manipulation:{ enabled:true }});
 };

 function network_fixate(){
  nodes.forEach(function(node,id){ nodes.update({id:id,fixed:!(node.fixed)}); });
  $("#result").html("Toggle fix");
 };

 function network_sync(){
  network.storePositions();
  $("#nodes").val(JSON.stringify(nodes.get(),undefined,2));
  $("#edges").val(JSON.stringify(edges.get(),undefined,2));
  $("#result").html("Synced config");
 };
 """
 print "</SCRIPT></ARTICLE>"
