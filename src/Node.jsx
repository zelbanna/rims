import React, { Component, Fragment } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import {Spinner, InfoCol2, ContentList, ContentData } from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.jsx';
import { TextInput, UrlInput } from './infra/Inputs.jsx';
import { NavBar } from './infra/Navigation.js';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {};
 }

 componentDidMount(){
  rest_call('api/master/node_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.url,<Fragment key='node_buttons'>
   <InfoButton key='node_info'   type='info'  onClick={() => this.changeContent(<Info key={'node_info_'+row.id} id={row.id} />)} />
   <InfoButton key='node_delete' type='delete' onClick={() => this.deleteList('api/master/node_delete',row.id,'Really delete node?')} />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='node_fragment'>
   <ContentList key='node_cl' header='Nodes' thead={['Node','URL','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='node_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='node_btn_add' type='add' onClick={() => this.changeContent(<Info key={'node_new_' + rnd()} id='new' />) } />
   </ContentList>
   <ContentData key='node_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// *************** Info ***************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true, content:null};
 }

 componentDidMount(){
  rest_call('api/master/node_info',{id:this.props.id}).then(result => this.setState(result))
 }

 searchInfo = () => {
  rest_call('api/device/search',{node:this.state.data.node}).then(result => result.found && this.setState({data:{...this.state.data, hostname:result.device.hostname, device_id:result.device.id}}))
 }

 changeHandler = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (!this.state.found)
   return <article>Node with id: {this.props.id} removed</article>
  else if (this.state.data) {
   const old = (this.state.data.id !== 'new');
   return (
   <Fragment key='node_info_fragment'>
    <article className='info'>
     <h1>Node Info</h1>
     <InfoCol2 key='node_content'>
      <TextInput key='node' id='node' value={this.state.data.node} changeHandler={this.changeHandler} />
      <UrlInput key='url' id='url' value={this.state.data.url}  changeHandler={this.changeHandler} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} changeHandler={this.changeHandler} />
     </InfoCol2>
     <InfoButton key='node_btn_save' type='save' onClick={() => this.updateInfo('api/master/node_info')} />
     {old && !this.state.data.hostname && <InfoButton key='node_btn_srch' type='search' onClick={this.searchInfo} />}
     {old && <InfoButton key='node_btn_reload' type='reload' onClick={() => this.changeContent(<Reload key={'node_reload'} node={this.state.data.node} />) } />}
     {old && <InfoButton key='node_btn_logs'  type='logs' onClick={() => this.changeContent(<LogShow key={'node_logs'} node={this.state.data.node} />) } />}
     {old && <InfoButton key='node_btn_logc'  title='Clear logs' type='delete' className='info'  onClick={() => this.changeContent(<LogClear key={'node_logc'} node={this.state.data.node} msg='Really clear logs?' />) } />}
    </article>
    <NavBar key='node_navbar' items={null} />
    {this.state.content}
   </Fragment>
   );
  } else
   return <Spinner />
 }
}

// *************** Reload ***************
//
class Reload extends Component {

 componentDidMount(){
  rest_call('system/reload/' + this.props.node).then(result => this.setState(result))
 }

 render(){
  if (!this.state)
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

 componentDidMount(){
  rest_call('api/system/logs_clear?node=' + this.props.node).then(result => this.setState({logs:result.file}))
 }

 render(){
  if (!this.state)
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

 componentDidMount(){
  rest_call('api/system/logs_get?node=' + this.props.node).then(result => this.setState({logs:result}))
 }

 Log = (props) => <Fragment>
   <h1>{props.name}</h1>
   {props.rows.map((line,index) => <span key={props.name + '_row_' + index}>{line}</span> )}
   </Fragment>

 render(){
  if (!this.state)
   return <Spinner />
  else {
   let output = []
   for (let [name, rows] of Object.entries(this.state.logs))
    output.push(<this.Log key={'log_file_' + name} name={name} rows={rows} />)
   return <article className='code'>{output}</article>
  }
 }
}
