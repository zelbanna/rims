"""Module docstring.

HTML5 Ajax Visualize module

"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
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
  print aWeb.button('edit',  DIV='div_content_right', URL='sdcp.cgi?visualize_info&type=map&id=%s'%map['id'],   TITLE='Show and Edit map') 
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
 res = aWeb.rest_call("visualize_show",{'id':aWeb['id']})
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
def info(aWeb):
 from json import dumps
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("visualize_info",args)
 print "<ARTICLE><P>Info for %s</P><DIV CLASS=controls>"%(res['name'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?visualize_info&type=%s&id=%s'%(res['type'],res['id']))
 print aWeb.button('trash',  DIV='div_content_right', URL='sdcp.cgi?visualize_delete&id=%s'%res['id'], TITLE='Delete map') 
 print aWeb.button('document', onclick='network_edit()', TITLE='Enable editor')
 print aWeb.button('start',  onclick='network_start()', TITLE='Enable physics')
 print aWeb.button('stop',   onclick='network_stop()', TITLE='Disable physics')
 print aWeb.button('sync',   onclick='network_sync()',TITLE='Sync graph to config')
 print aWeb.button('save',   DIV='div_content_right', URL='sdcp.cgi?visualize_info&op=update', FRM='network_config', TITLE='Save config')
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_network'><IMG SRC='images/btn-network.png'></A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_options'>Options</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_nodes'>Nodes</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_edges'>Edges</A>"
 print "</DIV><LABEL FOR=name>Name:</LABEL><FORM ID='network_config'><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' VALUE='%s' NAME=name><SPAN ID=result CLASS=results>%s</SPAN>"%(res['name'],res.get('result'))
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_options'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=options NAME=options>%s</TEXTAREA></DIV>"%dumps(res['options'],indent=4)
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_nodes'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=nodes NAME=nodes>%s</TEXTAREA></DIV>"%dumps(res['nodes'],indent=4)
 print "<DIV CLASS='tab' STYLE='display:none' ID='div_edges'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=edges NAME=edges>%s</TEXTAREA></DIV>"%dumps(res['edges'],indent=4)
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

 function network_start(){ 
  network.setOptions({ physics:true  });
 };

 function network_stop(){
  network.setOptions({ physics:false });
 };

 function network_edit(){
  network.setOptions({ manipulation:{ enabled:true }});
 };

 function network_sync(){
  network.storePositions();
  var sync = { edges:[],nodes:[]};
  Object.entries(network.body.data.nodes._data).forEach(([key,value]) => {
   var node = value;
   node.x   = value.x;
   node.y   = value.y;
   sync.nodes.push(node);
  });
  Object.entries(network.body.data.edges._data).forEach(([key,value]) => {
   var edge   = {};
   edge.from  = value.from;
   edge.to    = value.to;
   edge.title = value.title;
   sync.edges.push(edge);
  });
  $("#options").val(JSON.stringify(options,undefined,4));
  $("#nodes").val(JSON.stringify(sync.nodes,undefined,4));
  $("#edges").val(JSON.stringify(sync.edges,undefined,4));
 };
 """
 print "</SCRIPT></ARTICLE>"
