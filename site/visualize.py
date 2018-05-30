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
 print "<ARTICLE><P>Networks</P><DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?visualize_list', TITLE='Reload')
 print "</DIV><DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS='th maxed'>Name</DIV><DIV CLASS=th STYLE='width:50px'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for map in res['maps']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS='z-op' DIV='div_content_right' URL='sdcp.cgi?visualize_network&type=network&id=%s'>%s</A></DIV><DIV CLASS=td><DIV CLASS='controls'>"%(map['id'],map['id'],map['name'])
  print aWeb.button('document', DIV='div_content_right', URL='sdcp.cgi?visualize_info&id=%s'%map['id'],   TITLE='Show config') 
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"


#
#
def info(aWeb):
 from json import dumps
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("visualize_info",args)
 print "<ARTICLE><P>Info for %s</P><DIV CLASS=controls>"%(res['name'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?visualize_info&id=%s'%aWeb['id'])
 print aWeb.button('trash',  DIV='div_content_right', URL='sdcp.cgi?visualize_delete&id=%s'%aWeb['id'], TITLE='Delete map') 
 print aWeb.button('save',   DIV='div_content_right', URL='sdcp.cgi?visualize_info&op=update', FRM='network_config')
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.config' DIV='div_options'>Options</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.config' DIV='div_nodes'>Nodes</A>"
 print "<A CLASS='z-op btn small text' OP='single' SELECTOR='.config' DIV='div_edges'>Edges</A>"
 print "</DIV><SPAN CLASS=results>%s</SPAN><FORM ID='network_config'><INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(res.get('result'),aWeb['id'])
 print "<DIV CLASS='config' ID='div_options'><TEXTAREA CLASS=maxed STYLE='height:400px' NAME=options>%s</TEXTAREA></DIV>"%dumps(res['options'],indent=4)
 print "<DIV CLASS='config' STYLE='display:none' ID='div_nodes'><TEXTAREA CLASS=maxed STYLE='height:400px' NAME=nodes>%s</TEXTAREA></DIV>"%dumps(res['nodes'],indent=4)
 print "<DIV CLASS='config' STYLE='display:none' ID='div_edges'><TEXTAREA CLASS=maxed STYLE='height:400px' NAME=edges>%s</TEXTAREA></DIV>"%dumps(res['edges'],indent=4)
 print "</FORM>"
 print "</ARTICLE>"
#
#
def delete(aWeb):
 res = aWeb.rest_call("visualize_delete",{'id':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE>"%res

#
#
def network(aWeb):
 from json import dumps
 id = aWeb['id']
 res = aWeb.rest_call("visualize_%s"%aWeb['type'],{'id':id})
 print "<ARTICLE><P>'%s' network</P><DIV CLASS=controls>"%(res['name'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?visualize_network&type=%s&id=%s'%(aWeb['type'],id), TITLE='Reload')
 if aWeb['type'] == 'device':
  print aWeb.button('back',   DIV='div_content_right', URL='sdcp.cgi?device_info&id=%s'%id, TITLE='Back')
 print aWeb.button('start',  onclick='network_start()')
 print aWeb.button('stop',   onclick='network_stop()')
 print aWeb.button('save',   onclick='network_save()')
 print "</DIV><LABEL FOR=network_name>Name:</LABEL><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' VALUE='%s' ID=network_name><SPAN CLASS='results' ID=network_result></SPAN>"%res['name']
 print "<INPUT TYPE=HIDDEN VALUE=%s ID=network_id>"%id
 print "<INPUT TYPE=HIDDEN VALUE=%s ID=network_type>"%aWeb['type']
 print "<DIV ID='device_network' CLASS='network'></DIV><SCRIPT>"
 print "var nodes = new vis.DataSet(%s);"%dumps(res['nodes'])
 print ""
 print "var edges = new vis.DataSet(%s);"%dumps(res['edges'])
 print ""
 print "var options = %s;"%(dumps(res['options']))
 print """
 var data = {nodes:nodes, edges:edges};
 var network = new vis.Network(document.getElementById('device_network'), data, options);
 network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });

 function network_start(){ 
  network.setOptions({ physics:true  });
 };

 function network_stop(){
  network.setOptions({ physics:false });
 };

 function network_edit(){
  network.enableEditMode();
 };

 function network_save(){
  network.storePositions();
  var output = { options:options,edges:[],nodes:[],name:$('#network_name').val(),id:$('#network_id').val(), type:$('#network_type').val()};
  Object.entries(nodes._data).forEach(([key,value]) => {
   var node = value;
   node.x   = value.x;
   node.y   = value.y;
   output.nodes.push(node);
  });
  Object.entries(edges._data).forEach(([key,value]) => {
   var edge   = {};
   edge.from  = value.from;
   edge.to    = value.to;
   edge.title = value.title;
   output.edges.push(edge);
  });
  $.post('rest.cgi?visualize_save',JSON.stringify(output), result => { $('#network_result').html(JSON.stringify(result)); console.log(result);});
 };
 """
 print "</SCRIPT></ARTICLE>"
