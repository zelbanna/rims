"""HTML5 Ajax Visualize module"""
__author__= "Zacharias El Banna"
__icon__ = 'icon-visualize.png'
__type__ = 'menuitem'

#
#
def main(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='visualize_list'>Maps</A></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 list(aWeb)
 aWeb.wr("</SECTION><SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")
#
#
def list(aWeb):
 res = aWeb.rest_call("visualize/list")
 aWeb.wr("<ARTICLE><P>Maps</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_left', URL='visualize_list', TITLE='Reload'))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS='th maxed'>Name</DIV><DIV CLASS=th STYLE='width:50px'>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for map in res['maps']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(map['id'],map['name']))
  aWeb.wr(aWeb.button('edit',      DIV='div_content_right', URL='visualize_network?type=map&id=%s'%map['id'],   TITLE='Show and Edit map') )
  aWeb.wr(aWeb.button('network', DIV='div_content_right', URL='visualize_show?id=%s'%map['id'],   TITLE='Show map'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("visualize/delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE>"%res)

#
#
def show(aWeb):
 from json import dumps
 args = {'id':aWeb['id']} if aWeb['id'] else {'name':aWeb['name']}
 res = aWeb.rest_call("visualize/show",args)
 aWeb.wr("<ARTICLE><DIV CLASS='network' ID='div_network'></DIV><SCRIPT>")
 aWeb.wr("var nodes = new vis.DataSet(%s);"%dumps(res['nodes']))
 aWeb.wr("var edges = new vis.DataSet(%s);"%dumps(res['edges']))
 aWeb.wr("var options = %s;"%(dumps(res['options'])))
 aWeb.wr("""
 var data = {nodes:nodes, edges:edges};
 var network = new vis.Network(document.getElementById('div_network'), data, options);
 network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });
 network.on('doubleClick', function(params){
  console.log('DoubleClick',params.nodes);
  if (params.nodes[0]){
   var args = {op:'basics',id:params.nodes[0]};
   $.ajax({ type:"POST", url: '../api/device/info', data: JSON.stringify(args), dataType:'json',success: function(data){
    if (data && data.found){
     if(data.info.url)
      window.open(data.info.url);
     else
      window.open("ssh://" + data.username + "@" + data.ip,"_self");
    }
   }});
  }
 });
 """)
 aWeb.wr("</SCRIPT></ARTICLE>")

#
#
def network(aWeb):
 from json import dumps
 args = aWeb.args()
 res = aWeb.rest_call("visualize/network",args)
 aWeb.wr("<ARTICLE><P>Info for %s</P>"%(res['name']))
 aWeb.wr(aWeb.button('reload', DIV='div_content_right', URL='visualize_network?type=%s&id=%s'%(res['type'],res['id'])))
 aWeb.wr(aWeb.button('trash',  DIV='div_content_right', URL='visualize_delete?id=%s'%res['id'], TITLE='Delete map', MSG='Really delete map?'))
 if aWeb['type'] == 'device':
  aWeb.wr(aWeb.button('back',   DIV='div_content_right', URL='device_info?id=%s'%res['id'], TITLE='Return to device'))
 aWeb.wr(aWeb.button('edit', onclick='network_edit()', TITLE='Enable editor'))
 aWeb.wr(aWeb.button('start',  onclick='network_start()',  TITLE='Enable physics'))
 aWeb.wr(aWeb.button('stop',   onclick='network_stop()',   TITLE='Disable physics'))
 aWeb.wr(aWeb.button('fix',    onclick='network_fixate()', TITLE='Fix node positions'))
 aWeb.wr(aWeb.button('sync',   onclick='network_sync()',   TITLE='Sync graph to config'))
 aWeb.wr(aWeb.button('save',   DIV='div_content_right', URL='visualize_network?op=update', FRM='network_config', TITLE='Save config'))
 aWeb.wr(aWeb.button('network',DIV='div_network', OP='single', SELECTOR='.tab'))
 aWeb.wr(aWeb.button('help', HREF='http://visjs.org/docs/network/', TARGET='_blank', STYLE='float:right;', TITLE='vis.js help for configuring options/nodes/edges'))
 aWeb.wr("<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_options'>Options</A>")
 aWeb.wr("<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_nodes'>Nodes</A>")
 aWeb.wr("<A CLASS='z-op btn small text' OP='single' SELECTOR='.tab' DIV='div_edges'>Edges</A>")
 aWeb.wr("<LABEL FOR=name>Name:</LABEL><FORM ID='network_config'><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' VALUE='%s' NAME=name><SPAN ID=result CLASS=results>%s</SPAN>"%(res['name'],res.get('status',"")))
 aWeb.wr("<DIV CLASS='tab' STYLE='display:none' ID='div_options'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=options NAME=options>%s</TEXTAREA></DIV>"%dumps(res['options'],indent=2))
 aWeb.wr("<DIV CLASS='tab' STYLE='display:none' ID='div_nodes'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=nodes NAME=nodes>%s</TEXTAREA></DIV>"%dumps(res['nodes'],indent=2))
 aWeb.wr("<DIV CLASS='tab' STYLE='display:none' ID='div_edges'><TEXTAREA CLASS=maxed STYLE='height:400px' ID=edges NAME=edges>%s</TEXTAREA></DIV>"%dumps(res['edges'],indent=2))
 aWeb.wr("<INPUT TYPE=HIDDEN VALUE='%s' NAME=id>"%res['id'])
 aWeb.wr("<INPUT TYPE=HIDDEN VALUE='%s' NAME=type>"%res['type'])
 aWeb.wr("</FORM>")
 aWeb.wr("<DIV CLASS='tab network' ID='div_network'></DIV><SCRIPT>")
 aWeb.wr("var nodes = new vis.DataSet(%s);"%dumps(res['nodes']))
 aWeb.wr("var edges = new vis.DataSet(%s);"%dumps(res['edges']))
 aWeb.wr("var options = %s;"%(dumps(res['options'])))
 aWeb.wr("""
 var data = {nodes:nodes, edges:edges};
 var network = new vis.Network(document.getElementById('div_network'), data, options);
 network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });
 network.on('dragEnd',function(params){
  network.storePositions();
  $("#nodes").val(JSON.stringify(nodes.get(),undefined,2));
  $("#result").html('Moved ' + nodes.get(params.nodes[0]).label);
 });

 network.on('doubleClick', function(params){
  if (params.nodes[0]){
   network_node_page(params.nodes[0]);
  }
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
  $("#result").html("Enable edit");
 };

 function network_fixate(){
  nodes.forEach(function(node,id){ nodes.update({id:id,fixed:!(node.fixed)}); });
  $("#result").html("Toggle fix");
 };

 function network_sync(){
  network.storePositions();
  $("#nodes").val(JSON.stringify(nodes.get(),undefined,2));
  $("#edges").val(JSON.stringify(edges.get(),undefined,2));
  $("#result").html("Synced graph to config views");
 };

 function network_node_page(id){
  var url = 'device_info?id=' + id;
  var div = $('#div_content_right');
  $.get(url, result => { load_result(div,result,false,false); });
 };
 """)
 aWeb.wr("</SCRIPT></ARTICLE>")
