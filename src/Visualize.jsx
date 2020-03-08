import React, { Fragment, Component } from 'react';
import { rest_call, rest_base } from './infra/Functions.js';
import { MainBase, ListBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';
import { Spinner } from './infra/Generic.js';
import { DataSet, Network } from 'vis';
import { Info as DeviceInfo } from './Device.jsx'

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
  rest_call(rest_base + 'api/visualize/list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.id,row.name,<Fragment key='viz_list_buttons'>
  <InfoButton key={'viz_edt_'+row.id} type='edit'    onClick={() => { this.changeContent(<Edit key={'viz_edit_'+row.id} id={row.id} changeSelf={this.props.changeContent} type='map' title='Show and edit map' />)}} />
  <InfoButton key={'viz_net_'+row.id} type='network' onClick={() => { this.changeContent(<Show key={'viz_show_'+row.id} id={row.id} />)}} />
  <InfoButton key={'viz_del_'+row.id} type='trash'   onClick={() => { this.deleteList('api/visualize/delete',row.id,'Really delete map?')}} />
 </Fragment>]
}

// ******************** VizNetwork *********************
//
class VizNetwork extends Component {

 componentDidMount(){
  var nodes = new DataSet(this.props.nodes);
  var edges = new DataSet(this.props.edges);
  var data = {nodes:nodes, edges:edges};
  var network = new Network(this.refs.network_canvas, data, this.props.options);
  network.on('stabilizationIterationsDone', () => network.setOptions({ physics: false }))
  network.on('doubleClick', (params) => this.props.doubleClick(params))
 }

 render(){
  return <div className='network' id='div_network' ref='network_canvas' />
 }
}

// ************** Show **************
//
class Show extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 componentDidMount(){
  var args = (this.props.hasOwnProperty("id")) ? {id:this.props.id}:{name:this.props.name};
  rest_call(rest_base + "api/visualize/show",args)
   .then(result => {
    this.setState({content:<VizNetwork key='vizualize' nodes={result.nodes} edges={result.edges} options={result.options} doubleClick={this.doubleClick} />})
   })
 }

 doubleClick = (params) => {
  console.log("DoubleClick",params.nodes);
  if (params.nodes[0]){
   rest_call(rest_base + "api/device/management",{id:params.nodes[0]})
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
  if (this.state.content === null)
   return <Spinner />
  else {
   return <article>{this.state.content}</article>
  }
 }
}

// ************** Edit **************
//
// TODO: All buttons
//
class Edit extends Component {
 constructor(props){
  super(props)
  this.state = {content:null,result:null,edit:false}
 }

 componentDidMount(){
  rest_call(rest_base + "api/visualize/network",{id:this.props.id,type:this.props.type})
   .then((result) => {
    this.setState({name:result.name, content:<VizNetwork key='vizualize' nodes={result.nodes} edges={result.edges} options={result.options} doubleClick={this.doubleClick} op={this.networkOp} />})
  })
 }

 doubleClick = (params) => {
  console.log("DoubleClick",params.nodes);
 }


 networkOp = (params) => {
  if (params.op == 'edit'){
   this.content.network.setOptions({ manipulation:{ enabled:true }});
  }
 }

 render(){
  if (this.state.content === null)
   return <Spinner />
  else {
   return(
    <article>
     <h1>Info for {this.state.name}</h1>
     <InfoButton key='viz_reload' type='reload' onClick={() => this.componentDidMount()} />
     {this.state.content}
    </article>
   )
  }
 }
}

/*
 aWeb.wr(aWeb.button('edit', onclick='network_edit()', TITLE='Enable editor'))
 aWeb.wr(aWeb.button('start',  onclick='network_start()',  TITLE='Enable physics'))
 aWeb.wr(aWeb.button('stop',   onclick='network_stop()',   TITLE='Disable physics'))
 aWeb.wr(aWeb.button('fix',    onclick='network_fixate()', TITLE='Fix node positions'))
 aWeb.wr(aWeb.button('sync',   onclick='network_sync()',   TITLE='Sync graph to config'))
 aWeb.wr(aWeb.button('save',   DIV='div_content_right', URL='visualize_network?op=update', FRM='visualize_network', TITLE='Save config'))
*/
