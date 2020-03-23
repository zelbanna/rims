import React, { Fragment, Component } from 'react';
import { rest_call } from './infra/Functions.js';
import { ContentData, ContentList } from './infra/Generic.js';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { DataSet, Network } from 'vis';
import { Info as DeviceInfo } from './Device.jsx';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <List key='viz_list' />
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
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

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='viz_fragment'>
   <ContentList key='viz_cl' header='Maps' thead={['ID','NAme','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='viz_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
   </ContentList>
   <ContentData key='viz_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
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
   rest_call("api/device/management",{id:params.nodes[0]}).then(result => {
    if (result && result.status === "OK"){
     if(result.data.url && result.data.url.length > 0)
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
export class Edit extends Component {
 constructor(props){
  super(props)
  this.state = {content:'network', physics_button:'start', found:true, data:{name:'N/A'}}
  this.viz = {network:null,nodes:null,edges:null}
  this.results = React.createRef();
  this.edit = false;
 }

 componentDidMount(){
  rest_call("api/visualize/network",{id:this.props.id,type:this.props.type})
   .then((result) => {
    this.viz.nodes = new DataSet(result.data.nodes);
    this.viz.edges = new DataSet(result.data.edges);
    result.data.options.physics.enabled = true;
    this.viz.network = new Network(this.refs.edit_canvas, {nodes:this.viz.nodes, edges:this.viz.edges}, result.data.options);
    this.viz.network.on('stabilizationIterationsDone', () => this.viz.network.setOptions({ physics: false }))
    this.viz.network.on('doubleClick', (params) => this.doubleClick(params))
    this.viz.network.on('dragEnd', (params) => this.networkSync(params))
    result.data.options.physics.enabled = false;
    this.setState(result)
  })
 }

 changeHandler = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data})
 }

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 doubleClick = (params) => {
  console.log("DoubleClick",params.nodes[0]);
  if(this.props.changeSelf)
   this.props.changeSelf(<DeviceInfo key={'di_' + params.nodes[0]} id={params.nodes[0]} changeSelf={this.props.changeSelf} />)
 }

 togglePhysics = () => {
  const data = this.state.data;
  data.options.physics.enabled = !data.options.physics.enabled;
  this.viz.network.setOptions({ physics:data.options.physics.enabled })
  this.results.current.textContent="Physics:"+data.options.physics.enabled;
  this.setState({data:data,physics_button:(data.options.physics.enabled) ? 'stop':'start'})
 }

 toggleEdit = () => {
  this.edit = !this.edit;
  this.results.current.textContent="Edit:"+!this.edit;
  this.viz.network.setOptions({ manipulation:{ enabled:this.edit }})
 }

 toggleFix = () => {
  this.viz.nodes.forEach((node,id) => this.viz.nodes.update({id:id,fixed:!(node.fixed)}) );
  this.results.current.textContent="Fix/Unfix positions";
  this.setState({data:{...this.state.data, nodes:this.viz.nodes.get()}})
 }

 networkSync = (params) => {
  this.viz.network.storePositions();
  this.results.current.textContent="Moved " + this.viz.nodes.get(params.nodes[0]).label;
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
    <h1>Network Map</h1>
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
    <span ref={this.results} className='results'></span>
    <div className={this.showDiv('network')} ref='edit_canvas' />
    <div className={this.showDiv('options')}><textarea id='options' name='options' value={JSON.stringify(this.state.data.options,undefined,2)} onChange={this.jsonHandler}/></div>
    <div className={this.showDiv('nodes')}><textarea id='nodes' name='nodes' value={JSON.stringify(this.state.data.nodes,undefined,2)} onChange={this.jsonHandler} /></div>
    <div className={this.showDiv('edges')}><textarea id='edged' name='edges' value={JSON.stringify(this.state.data.edges,undefined,2)} onChange={this.jsonHandler} /></div>
   </article>
  )
 }
}
