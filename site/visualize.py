"""Module docstring.

HTML5 Ajax Visualize module

"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"

#
#
def device(aWeb):
 from json import dumps
 res = aWeb.rest_call("visualize_device",{'id':aWeb['id']})
 edges = ["{'from':%s, 'to':%s, title:'%s:%s <-> %s:%s' }"%(con['a_device'],con['b_device'],res['nodes'][str(con['a_device'])]['label'],con['a_name'],res['nodes'][str(con['b_device'])]['label'],con['b_name']) for con in res['edges']]
 opts  = res['options']
 print "<ARTICLE><P>Device '%s':s network</P><DIV CLASS=controls>"%(aWeb['hostname'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?visualize_device&id=%s&hostname=%s'%(aWeb['id'],aWeb['hostname']), TITLE='Reload')
 print aWeb.button('back',   DIV='div_content_right', URL='sdcp.cgi?device_info&id=%s'%aWeb['id'], TITLE='Back')
 print aWeb.button('start',  onclick='network_start()')
 print aWeb.button('stop',   onclick='network_stop()')
 print aWeb.button('save',   onclick='network_save()')
 print "</DIV><LABEL FOR=network_name>Name:</LABEL><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' ID=network_name><SPAN CLASS='results' ID=network_result></SPAN>"
 print "<DIV ID='device_network' CLASS='network'></DIV><SCRIPT>"
 print "var nodes = new vis.DataSet(%s);"%dumps(res['nodes'].values())
 print "var edges = new vis.DataSet([%s]);"%",".join(edges)
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

 function network_save(){
  var output = { options:options,edges:[],nodes:{},name:$("#network_name").val()};
  positions = network.getPositions();
  Object.entries(nodes._data).forEach(([key,value]) => {
   var node = value;
   node.x   = positions[key].x;
   node.y   = positions[key].y;
   output.nodes[key] = node;
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
