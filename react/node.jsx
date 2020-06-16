import React, { Component } from 'react'
import { post_call, rnd } from './infra/Functions.js';
import {Spinner, CodeArticle, InfoArticle, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
import { NavBar } from './infra/Navigation.jsx';
import { TextInput, UrlInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, InfoButton, LogButton, ReloadButton, SaveButton, SearchButton } from './infra/Buttons.jsx';

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {};
 }

 componentDidMount(){
  post_call('api/master/node_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.url,<>
   <InfoButton key='info' onClick={() => this.changeContent(<Info key={'node_info_'+row.id} id={row.id} />)} title='Node information' />
   <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete node' />
  </>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete node?') && post_call('api/master/node_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <>
   <ContentList key='node_cl' header='Nodes' thead={['Node','URL','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<Info key={'node_new_' + rnd()} id='new' />)} title='Add node' />
   </ContentList>
   <ContentData key='node_cd'>{this.state.content}</ContentData>
  </>
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
  post_call('api/master/node_info',{id:this.props.id}).then(result => this.setState(result))
 }

 searchInfo = () => post_call('api/device/search',{node:this.state.data.node}).then(result => result.found && this.setState({data:{...this.state.data, hostname:result.data.hostname, device_id:result.data.id}}))

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () =>  post_call('api/master/node_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (!this.state.found)
   return <InfoArticle key='node_art'>Node with id: {this.props.id} removed</InfoArticle>
  else if (this.state.data) {
   const old = (this.state.data.id !== 'new');
   return <>
    <InfoArticle key='node_art' header='Node'>
     <InfoColumns key='node_content'>
      <TextInput key='node' id='node' value={this.state.data.node} onChange={this.onChange} />
      <UrlInput key='url' id='url' value={this.state.data.url}  onChange={this.onChange} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save information' />
     {old && !this.state.data.hostname && <SearchButton key='search' onClick={this.searchInfo} title='Try to map node to device' />}
     {old && <ReloadButton key='reload' onClick={() => this.changeContent(<Reload key={'node_reload'} node={this.state.data.node} />)} />}
     {old && <LogButton key='logs' onClick={() => this.changeContent(<LogShow key={'node_logs'} node={this.state.data.node} />)} title='View node logs' />}
     {old && <DeleteButton key='logc' onClick={() => this.changeContent(<LogClear key={'node_logc'} node={this.state.data.node} />)} title='Clear logs' />}
    </InfoArticle>
    <NavBar key='node_navigation' id='node_navigation' />
    {this.state.content}
   </>
  } else
   return <Spinner />
 }
}

// *************** Reload ***************
//
class Reload extends Component {

 componentDidMount(){
  post_call('api/system/reload',{},{'X-Route':this.props.node}).then(result => this.setState(result))
 }

 render(){
  return (!this.state) ? <Spinner /> : <CodeArticle key='nr_code' header='Module'>{this.state.modules.join('\n')}</CodeArticle>
 }
}

// *************** LogClear ***************
//
class LogClear extends Component {

 componentDidMount(){
  post_call('api/system/logs_clear',{},{'X-Route':this.props.node}).then(result => this.setState({logs:result.file}))
 }

 render(){
  return (!this.state) ? <Spinner /> : <CodeArticle key='nc_code' header='Cleared'>{(Object.entries(this.state.logs).map(log => `${log[0]}: ${log[1]}`)).join('\n')}</CodeArticle>
 }
}

// *************** LogShow ***************
//
export class LogShow extends Component {

 componentDidMount(){
  post_call('api/system/logs_get',{},{'X-Route':this.props.node}).then(result => this.setState({logs:result}))
 }

 render(){
  return (!this.state) ? <Spinner /> : <div>{Object.entries(this.state.logs).map((log,idx) => <CodeArticle key={idx} header={log[0]}>{log[1].join('\n')}</CodeArticle>)}</div>
 }
}
