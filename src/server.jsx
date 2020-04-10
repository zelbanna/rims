import React, { Component, Fragment } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
import { NavBar }   from './infra/Navigation.jsx';
import { SelectInput, TextLine, UrlInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, InfoButton, ItemsButton, ReloadButton, SaveButton, SyncButton, UiButton } from './infra/Buttons.jsx';

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/server_list',{type:this.props.type}).then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.service,row.type,<Fragment key='sl_buttons'>
   <InfoButton key={'sl_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'server_info_'+row.id} id={row.id} />)} title='Service information' />
   <DeleteButton key={'sl_btn_delete'+row.id} onClick={() => this.deleteList(row.id)} title='Delete service' />
   {row.hasOwnProperty('ui') && row.ui.length > 0 && <UiButton key={'sl_btn_ui'+row.id} onClick={() =>  window.open(row.ui,'_blank')} title='Server UI' />}
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete service?') && rest_call('api/master/server_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='sl_fragment'>
   <ContentList key='sl_cl' header='Servers' thead={['Node','Service','Type','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='sl_btn_reload' onClick={() => this.componentDidMount()} />
    <AddButton key='sl_btn_add' onClick={() => this.changeContent(<Info key={'sl_new_' + rnd()} id='new' type={this.props.type} />)} title='Add service' />
   </ContentList>
   <ContentData key='sl_cd'>{this.state.content}</ContentData>
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
  rest_call('api/master/server_info',{id:this.props.id}).then(result => {
   if (!result.data.node)
    result.data.node = result.nodes[0];
   if (!result.data.type_id)
    result.data.type_id = result.services[0].id;
   this.setState(result);
   })
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => rest_call('api/master/server_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (!this.state.found)
   return <article>Server with id: {this.props.id} removed</article>
  else if (this.state.data){
   const old = (this.state.data.id !== 'new');
   return (
    <Fragment key='si_info_fragment'>
    <article className='info'>
     <h1>Server</h1>
     <InfoColumns key='si_content'>
      <TextLine key='server' id='server' label='ID' text={this.state.data.id} />
      <SelectInput key='node' id='node' value={this.state.data.node} onChange={this.onChange}>{this.state.nodes.map((row,idx) => <option key={'si_node_'+idx} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='type_id' id='type_id' label='Service' value={this.state.data.type_id} onChange={this.onChange}>{this.state.services.map((row,idx) => <option key={'si_svc_'+idx} value={row.id}>{`${row.service} (${row.type})`}</option>)}</SelectInput>
      <UrlInput key='ui' id='ui' label='UI' value={this.state.data.ui} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='si_btn_save' onClick={() => this.updateInfo()} title='Save' />
     {old && <SyncButton key='si_sync' onClick={() => this.changeContent(<Operation key={'srv_op_sync'} id={this.props.id} operation='sync' />)} title='Sync service' />}
     {old && <ReloadButton key='si_restart' onClick={() => this.changeContent(<Operation key={'srv_op_rst'}  id={this.props.id} operation='restart' />)} title='Restart service' />}
     {old && <ItemsButton key='si_status' onClick={() => this.changeContent(<Operation key={'srv_op_stat'} id={this.props.id} operation='status' />)} title='Service status' />}
    </article>
    <NavBar key='server_navigation' id='server_navigation' />
    {this.state.content}
    </Fragment>
   );
  } else
   return <Spinner />
 }
}

// *************** Operation ***************
//
class Operation extends Component {
 componentDidMount(){
  rest_call('api/master/server_' + this.props.operation,{id:this.props.id}).then(result => this.setState(result))
 }

 render(){
  return (this.state) ? <article className='code'><pre>{JSON.stringify(this.state,null,2)}</pre></article> : <Spinner />
 }
}
