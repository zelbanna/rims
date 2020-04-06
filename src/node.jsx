import React, { Component, Fragment } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import {Spinner, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
import { NavBar } from './infra/Navigation.js';
import { TextInput, UrlInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, InfoButton, LogButton, ReloadButton, SaveButton, SearchButton } from './infra/Buttons.jsx';

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
   <InfoButton key={'nl_btn_info'+row.id} onClick={() => this.changeContent(<Info key={'node_info_'+row.id} id={row.id} />)} title='Node information' />
   <DeleteButton key={'nl_btn_delete'+row.id} onClick={() => this.deleteList(row.id)} title='Delete node' />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete node?') && rest_call('api/master/node_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='node_fragment'>
   <ContentList key='node_cl' header='Nodes' thead={['Node','URL','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='nl_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='nl_btn_add' onClick={() => this.changeContent(<Info key={'node_new_' + rnd()} id='new' />)} title='Add node' />
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

 searchInfo = () => rest_call('api/device/search',{node:this.state.data.node}).then(result => result.found && this.setState({data:{...this.state.data, hostname:result.device.hostname, device_id:result.device.id}}))

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () =>  rest_call('api/master/node_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (!this.state.found)
   return <article>Node with id: {this.props.id} removed</article>
  else if (this.state.data) {
   const old = (this.state.data.id !== 'new');
   return (
   <Fragment key='node_info_fragment'>
    <article className='info'>
     <h1>Node</h1>
     <InfoColumns key='node_content'>
      <TextInput key='node' id='node' value={this.state.data.node} onChange={this.onChange} />
      <UrlInput key='url' id='url' value={this.state.data.url}  onChange={this.onChange} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='ni_btn_save' onClick={() => this.updateInfo()} title='Save information' />
     {old && !this.state.data.hostname && <SearchButton key='ni_btn_srch' onClick={this.searchInfo} title='Try to map node to device' />}
     {old && <ReloadButton key='ni_btn_reload' onClick={() => this.changeContent(<Reload key={'node_reload'} node={this.state.data.node} />)} />}
     {old && <LogButton key='ni_btn_logs' onClick={() => this.changeContent(<LogShow key={'node_logs'} node={this.state.data.node} />)} title='View node logs' />}
     {old && <DeleteButton key='ni_btn_logc' onClick={() => this.changeContent(<LogClear key={'node_logc'} node={this.state.data.node} msg='Really clear logs?' />)} title='Clear logs' />}
    </article>
    <NavBar key='node_navigation' id='node_navigation' />
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
  return (!this.state) ? <Spinner /> : <article className='code'><h1>Cleared</h1>{Object.entries(this.state.logs).map(log => <span key={log[0]}>{log[0]}: {log[1]}</span>)}</article>
 }
}

// *************** LogShow ***************
//
export class LogShow extends Component {

 componentDidMount(){
  rest_call('api/system/logs_get?node=' + this.props.node).then(result => this.setState({logs:result}))
 }

 render(){
  return (!this.state) ? <Spinner /> : <article className='code'>{Object.entries(this.state.logs).map(log => <Fragment><h1>{log[0]}</h1>{log[1].map((line,idx) => <span key={log[0]+'_'+idx}>{line}</span> )}</Fragment>)}</article>
 }
}
