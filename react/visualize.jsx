import React, { Fragment, Component } from 'react';
import { post_call } from './infra/Functions.js';
import { Article, ContentData, ContentList, Result } from './infra/UI.jsx';
import { BackButton, DeleteButton, EditButton, FixButton, ReloadButton, SaveButton, StartButton, StopButton, TextButton, NetworkButton } from './infra/Buttons.jsx';
import { TextInput } from './infra/Inputs.jsx';
import styles from './infra/ui.module.css';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <List key='viz_list' />
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment>{this.state}</Fragment>
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
  post_call('api/visualize/list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.id,row.name,<Fragment>
  <EditButton key={'vl_btn_edt_'+row.id} onClick={() => this.changeContent(<Edit key={'viz_edit_'+row.id} id={row.id} changeSelf={this.changeContent} type='map' />)} title='Show and edit map' />
  <NetworkButton key={'vl_btn_net_'+row.id} onClick={() => window.open(`viz.html?id=${row.id}`,'_blank')} title='Show resulting map' />
  <DeleteButton key={'vl_btn_del_'+row.id}  onClick={() => this.deleteList(row.id)} />
 </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Delete map?') && post_call('api/visualize/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment>
   <ContentList key='vl_cl' header='Maps' thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='vl_btn_reload' onClick={() => this.componentDidMount() } />
   </ContentList>
   <ContentData key='vl_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Edit **************
//
export class Edit extends Component {
 constructor(props){
  super(props)
  this.state = {content:'network', physics_button:StartButton, found:true, data:{name:'N/A'}, result:''}
  this.viz = {network:null,nodes:null,edges:null}
  this.canvas = React.createRef()
  this.edit = false;
 }

 componentDidMount(){
  import('vis-network/standalone/esm/vis-network').then(vis => {
   post_call('api/visualize/network',{id:this.props.id,type:this.props.type}).then((result) => {
    this.viz.nodes = new vis.DataSet(result.data.nodes);
    this.viz.edges = new vis.DataSet(result.data.edges);
    result.data.options.physics.enabled = true;
    result.data.options.clickToUse = true;
    this.viz.network = new vis.Network(this.canvas.current, {nodes:this.viz.nodes, edges:this.viz.edges}, result.data.options);
    this.viz.network.on('stabilizationIterationsDone', () => this.viz.network.setOptions({ physics: false }))
    this.viz.network.on('doubleClick', (params) => this.doubleClick(params))
    this.viz.network.on('dragEnd', (params) => this.networkSync(params))
    result.data.options.physics.enabled = false;
    this.setState(result)
   })
  })
 }

 changeImport = (dev) => import('./device.jsx').then(lib => this.props.changeSelf(<lib.Info key={'di_'+dev} id={dev} />));

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 jsonHandler = (e) => {
  var data = {...this.state.data}
  try {
   data[e.target.name] = JSON.parse(e.target.value);
   this.setState({data:data})
  } catch {
   console.log('Error converting string to JSON')
  }
 }

 updateInfo = () => post_call('api/visualize/network',{op:'update', ...this.state.data}).then(result => this.setState(result))

 doubleClick = (params) => {
  console.log('DoubleClick',params.nodes[0]);
  this.props.changeSelf && this.changeImport(params.nodes[0]);
 }

 toggleEdit = () => {
  this.edit = !this.edit;
  this.viz.network.setOptions({ manipulation:{ enabled:this.edit }})
  this.setState({result:'Edit:'+this.edit});
 }

 toggleFix = () => {
  this.viz.nodes.forEach((node,id) => this.viz.nodes.update({id:id,fixed:!(node.fixed)}) );
  this.setState({data:{...this.state.data, nodes:this.viz.nodes.get()}, result:'Fix/Unfix positions'})
 }

 togglePhysics = () => {
  const data = this.state.data;
  data.options.physics.enabled = !data.options.physics.enabled;
  this.viz.network.setOptions({ physics:data.options.physics.enabled })
  this.setState({data:data, physics_button:(data.options.physics.enabled) ? StopButton:StartButton, result:'Physics:'+data.options.physics.enabled})
 }

 networkSync = (params) => {
  this.viz.network.storePositions();
  this.setState({data:{...this.state.data, nodes:this.viz.nodes.get(), edges:this.viz.edges.get()}, result:'Moved ' + this.viz.nodes.get(params.nodes[0]).label})
 }

 showDiv = (id) => (id === this.state.content) ? {display:'block'} : {display:'none'}

 render(){
  const PhysicsButton = this.state.physics_button;
  return(
   <Article key='viz_art' header='Network Map'>
    {(this.props.type === 'device') && (this.props.changeSelf) && <BackButton key='viz_back' onClick={() => this.changeImport(this.props.id)} />}
    <ReloadButton key='viz_reload' onClick={() => this.componentDidMount()} />
    <EditButton key='viz_edit' onClick={() => this.toggleEdit()} />
    <PhysicsButton key='viz_physics' onClick={() => this.togglePhysics()} />
    <FixButton key='viz_fix' onClick={() => this.toggleFix()} />
    <SaveButton key='viz_save' onClick={() => this.updateInfo()} />
    <NetworkButton key='viz_net' onClick={() => this.setState({content:'network'})} />
    <TextButton key='viz_opt' text='Options' onClick={() => this.setState({content:'options'})} />
    <TextButton key='viz_nodes' text='Nodes' onClick={() => this.setState({content:'nodes'})} />
    <TextButton key='viz_edges' text='Edges' onClick={() => this.setState({content:'edges'})} />
    <TextInput key='viz_name' id='name' value={this.state.data.name} onChange={this.onChange} />
    <Result key='viz_result' result={this.state.result} />
    <div className={styles.network} style={this.showDiv('network')} ref={this.canvas} />
    <div className={styles.network} style={this.showDiv('options')}><textarea id='options' name='options' value={JSON.stringify(this.state.data.options,undefined,2)} onChange={this.jsonHandler}/></div>
    <div className={styles.network} style={this.showDiv('nodes')}><textarea id='nodes' name='nodes' value={JSON.stringify(this.state.data.nodes,undefined,2)} onChange={this.jsonHandler} /></div>
    <div className={styles.network} style={this.showDiv('edges')}><textarea id='edges' name='edges' value={JSON.stringify(this.state.data.edges,undefined,2)} onChange={this.jsonHandler} /></div>
   </Article>
  )
 }
}
