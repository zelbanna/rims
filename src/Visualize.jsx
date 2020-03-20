import React, { Fragment, Component } from 'react';
import { rest_call } from './infra/Functions.js';
import { MainBase, ListBase, InfoBase } from './infra/Base.jsx';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { DataSet, Network } from 'vis';
import { Info as DeviceInfo } from './Device.jsx';

// ************** Main **************
//
export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state.content = <List key='viz_list' />
 }
}

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props)
  this.header = 'Maps'
  this.thead = ['ID','Name','']
  this.buttons = [<InfoButton key='viz_reload' type='reload' onClick={() => {this.componentDidMount()}} />]
 }

 componentDidMount(){
  rest_call('api/visualize/list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.id,row.name,<Fragment key='viz_list_buttons'>
  <InfoButton key={'viz_edt_'+row.id} type='edit' onClick={() => { this.changeContent(<Edit key={'viz_edit_'+row.id} id={row.id} changeSelf={this.changeContent} type='map' />)}} title='Show and edit map' />
  <InfoButton key={'viz_net_'+row.id} type='network' onClick={() => { this.changeContent(<Show key={'viz_show_'+row.id} id={row.id} />)}} />
  <InfoButton key={'viz_del_'+row.id} type='delete' onClick={() => { this.deleteList('api/visualize/delete',row.id,'Really delete map?')}} />
 </Fragment>]
}

// ************** Show **************
//
class Show extends Component {

 componentDidMount(){
  var args = (this.props.hasOwnProperty("id")) ? {id:this.props.id}:{name:this.props.name};
  rest_call("api/visualize/show",args)
   .then(result => {
    var nodes = new DataSet(result.data.nodes);
    var edges = new DataSet(result.data.edges);
    var network = new Network(this.refs.show_canvas, {nodes:nodes, edges:edges}, result.data.options);
    network.on('stabilizationIterationsDone', () => network.setOptions({ physics: false }))
    network.on('doubleClick', (params) => this.doubleClick(params))
   })
 }

 doubleClick = (params) => {
  console.log("DoubleClick",params.nodes);
  if (params.nodes[0]){
   rest_call("api/device/management",{id:params.nodes[0]})
   .then(result => {
    if (result && result.status === "OK"){
     if(result.data.url)
      window.open(result.data.url);
     else
      window.open("ssh://" + result.data.username + "@" + result.data.ip,"_self");
    }else
     console.log("Data not ok:" + result)
   })
  }
 }

 render(){
  return <article><div className='network' id='div_network' ref='show_canvas' /></article>
 }
}

// ************** Edit **************
//
class Edit extends InfoBase {
 constructor(props){
  super(props)
  this.state = {edit:false, physics:false, name:"",content:'network', physics_button:'start'}
  this.state.data = {options:{physics:{enabled:false}},nodes:null,edges:null,name:''}
  this.viz = {network:null,nodes:null,edges:null}
 }

 componentDidMount(){
  rest_call("api/visualize/network",{id:this.props.id,type:this.props.type})
   .then((result) => {
    this.viz.nodes = new DataSet(result.data.nodes);
    this.viz.edges = new DataSet(result.data.edges);
    this.viz.network = new Network(this.refs.edit_canvas, {nodes:this.viz.nodes, edges:this.viz.edges}, result.data.options);
    this.viz.network.on('stabilizationIterationsDone', () => this.viz.network.setOptions({ physics: false }))
    this.viz.network.on('doubleClick', (params) => this.doubleClick(params))
    this.viz.network.on('dragEnd', (params) => this.networkSync())
    result.data.options.physics.enabled = false;
    this.setState(result)
  })
 }

 doubleClick = (params) => {
  console.log("DoubleClick",params.nodes[0]);
  this.props.changeSelf(<DeviceInfo id={params.nodes[0]} />)
 }

 togglePhysics = () => {
  const data = this.state.data;
  data.options.physics.enabled = !data.options.physics.enabled;
  this.setState({data:data})
  this.setState({physics_button:(data.options.physics.enabled) ? 'stop':'start'})
  console.log("Vizualize physics: " + data.options.physics.enabled)
  this.viz.network.setOptions({ physics:data.options.physics.enabled })
 }

 toggleEdit = () => {
  this.state.edit = !this.state.edit;
  console.log("Vizualize edit: " + this.state.edit)
  this.viz.network.setOptions({ manipulation:{ enabled:this.state.edit }})
 }

 toggleFix = () => {
  console.log("Fix positions")
  this.viz.nodes.forEach((node,id) => this.viz.nodes.update({id:id,fixed:!(node.fixed)}) );
 }

 networkSync = () => {
  this.viz.network.storePositions();
  this.setState({data:{...this.state.data, nodes:this.viz.nodes.get(), edges:this.viz.edges.get()}})
 }

 jsonHandler = (e) => {
  var data = {...this.state.data}
  try {
   data[e.target.name] = JSON.parse(e.target.value);
   this.setState({data:data})
  } catch {
   console.log("Error converting string to JSON")
  }
 }

 showDiv = (id) => (id === this.state.content) ? 'network show' : 'hidden';

 render(){
  return(
   <article className='network'>
    <h1>Info for {this.state.name}</h1>
    <InfoButton key='viz_reload' type='reload' onClick={() => this.componentDidMount()} />
    <InfoButton key='viz_edit' type='edit' onClick={() => this.toggleEdit()} />
    <InfoButton key='viz_physics' type={this.state.physics_button} onClick={() => this.togglePhysics()} />
    <InfoButton key='viz_fix' type='fix' onClick={() => this.toggleFix()} />
    <InfoButton key='viz_save' type='save' onClick={() => this.updateInfo('api/visualize/network')} />
    <InfoButton key='viz_net' type='network' onClick={() => this.setState({content:'network'})} />
    <TextButton key='viz_opt' text='Options' className='info' onClick={() => this.setState({content:'options'})} />
    <TextButton key='viz_nodes' text='Nodes' className='info' onClick={() => this.setState({content:'nodes'})} />
    <TextButton key='viz_edges' text='Edges' className='info' onClick={() => this.setState({content:'edges'})} />
    <label className='network' htmlFor='name'>Name:</label><input type='text' id='name' name='name' value={this.state.data.name} onChange={this.changeHandler} />
    <div id='div_network' className={this.showDiv('network')} ref='edit_canvas' />
    <div id='div_options' className={this.showDiv('options')}><textarea id='options' name='options' value={JSON.stringify(this.state.data.options,undefined,2)} onChange={this.jsonHandler}/></div>
    <div id='div_nodes'   className={this.showDiv('nodes')}><textarea id='nodes' name='nodes' value={JSON.stringify(this.state.data.nodes,undefined,2)} onChange={this.jsonHandler} /></div>
    <div id='div_edges'   className={this.showDiv('edges')}><textarea id='edged' name='edges' value={JSON.stringify(this.state.data.edges,undefined,2)} onChange={this.jsonHandler} /></div>
   </article>
  )
 }
}
