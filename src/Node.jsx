import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import {Spinner, InfoCol2 } from './infra/Generic.js';
import { ListBase, InfoBase } from './infra/Base.jsx';
import { TextButton, InfoButton } from './infra/Buttons.jsx';
import { NavBar } from './infra/Navigation.js';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props);
  this.header = 'Nodes'
  this.thead = ['Node','URL','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount()} />,
   <InfoButton key='add'  type='add'  onClick={() => this.changeContent(<Info key={'node_new_' + rnd()} id='new' />)}  />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/node_list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.node,row.url,<Fragment key='node_buttons'>
   <InfoButton key='node_info'   type='info'  onClick={() => this.changeContent(<Info key={'node_info_'+row.id} id={row.id} />)} />
   <InfoButton key='node_delete' type='trash' onClick={() => this.deleteList('api/master/node_delete',row.id,'Really delete node?')} />
  </Fragment>]
}

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/master/node_info',{id:this.props.id})
   .then((result) => {
    if(result.data.hostname === null)
     result.data.hostname = undefined;
    this.setState(result)
   })
 }

 searchInfo = () => {
  rest_call(rest_base + 'api/device/search',{node:this.state.data.node})
   .then((result) => {
   if (result.found)
    this.setState({data:{...this.state.data, hostname:result.device.hostname, device_id:result.device.id}})
  })
 }

 infoItems = () => [
  {tag:'input', type:'text', id:'node', text:'Node', value:this.state.data.node},
  {tag:'input', type:'url',  id:'url',  text:'URL', value:this.state.data.url},
  {tag:'input', type:'text', id:'hostname',  text:'hostname', value:this.state.data.hostname},
 ]

 render() {
  if (this.state.found === false)
   return <article>Node with id: {this.props.id} removed</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   let buttons = [<InfoButton key='node_btn_save' type='save' onClick={() => this.updateInfo('api/master/node_info')} />]
   if (this.state.data.id !== 'new'){
    if (this.state.data.hostname === undefined)
     buttons.push(<InfoButton key='node_btn_srch' type='search' onClick={this.searchInfo} />)
    buttons.push(<InfoButton key='node_btn_reload' type='reload' onClick={() => this.changeContent(<Reload key={'node_reload'} node={this.state.data.node} />) } />)
    buttons.push(<InfoButton key='node_btn_logs'  type='logs' onClick={() => this.changeContent(<LogShow key={'node_logs'} node={this.state.data.node} />) } />)
    buttons.push(<InfoButton key='node_btn_logc'  title='Clear logs' type='trash' className='info'  onClick={() => this.changeContent(<LogClear key={'node_logc'} node={this.state.data.node} msg='Really clear logs?' />) } />)
   }
   return (
   <Fragment key='node_info_fragment'>
    <article className='info'>
     <h1>Node Info</h1>
     <InfoCol2 key='node_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     {buttons}
    </article>
    <NavBar key='node_navbar' items={null} />
    {this.state.content}
   </Fragment>
   );
  }
 }
}

// *************** Reload ***************
//
class Reload extends Component {
 constructor(props){
  super(props)
  this.state = {modules:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'system/reload/' + this.props.node)
   .then((result) =>  this.setState(result) )
 }

 render(){
  if (this.state.modules === null)
   return <Spinner />
  else {
   return (
    <article className='code'>
     <h1>Module</h1>
     {this.state.modules.map((row,index) => <span key={index}>{row}</span> )}
   </article>
   )
  }
 }
}

// *************** LogClear ***************
//
class LogClear extends Component {
 constructor(props){
  super(props)
  this.state = {logs:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/logs_clear?node=' + this.props.node)
   .then((result) => this.setState({logs:result.file}) )
 }

 render(){
  if (this.state.logs === null)
   return <Spinner />
  else {
   let output = []
   for (let [name, res] of Object.entries(this.state.logs))
    output.push(<span key={name}>{name}: {res}</span>)
   return <article className='code'><h1>Cleared</h1>{output}</article>
  }
 }
}

// *************** LogShow ***************
//
export class LogShow extends Component {
 constructor(props){
  super(props)
  this.state = {logs:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/logs_get?node=' + this.props.node)
   .then((result) => this.setState({logs:result}) )
 }

 Log = (props) => <Fragment>
   <h1>{props.name}</h1>
   {props.rows.map((line,index) => <span key={props.name + '_row_' + index}>{line}</span> )}
   </Fragment>

 render(){
  if (this.state.logs === null)
   return <Spinner />
  else {
   let output = []
   for (let [name, rows] of Object.entries(this.state.logs))
    output.push(<this.Log key={'log_file_' + name} name={name} rows={rows} />)
   return <article className='code'>{output}</article>
  }
 }
}
