import React, { Component, Fragment } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, ContentList, ContentData } from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.jsx';
import { SelectInput, TextLine, UrlInput } from './infra/Inputs.jsx';
import { NavBar }   from './infra/Navigation.js';

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

 listItem = (row) => {
  let buttons = [
   <InfoButton key='srv_info'   type='info'   onClick={() => this.changeContent(<Info key={'server_info_'+row.id} id={row.id} />) } />,
   <InfoButton key='srv_delete' type='delete' onClick={() => this.deleteList('api/master/server_delete',row.id,'Are you really sure?')  } />,
  ]
  if (row.hasOwnProperty('ui') && (row.ui.length > 0))
   buttons.push(<InfoButton key='srv_www' type='ui' onClick={() =>  window.open(row.ui,'_blank') } />)
  return [row.node,row.service,row.type,<Fragment key='srv_buttons'>{buttons}</Fragment>]
 }

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='srv_fragment'>
   <ContentList key='srv_cl' header='Servers' thead={['Node','Service','Type','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='srv_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='srv_btn_add' type='add' onClick={() => this.changeContent(<Info key={'srv_new_' + rnd()} id='new' type={this.props.type} />) } />
   </ContentList>
   <ContentData key='srv_cd'>{this.state.content}</ContentData>
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

 onChange = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 changeContent = (elem) => this.setState({content:elem})
 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (!this.state.found)
   return <article>Server with id: {this.props.id} removed</article>
  else if (this.state.data){
   const old = (this.state.data.id !== 'new');
   return (
    <Fragment key='srv_info_fragment'>
    <article className='info'>
     <h1>Server Info</h1>
     <InfoCol2 key='srv_content'>
      <TextLine key='server' id='server' label='ID' text={this.state.data.id} />
      <SelectInput key='node' id='node' value={this.state.data.node} options={this.state.nodes.map(row => ({value:row, text:row}))} onChange={this.onChange} />
      <SelectInput key='type_id' id='type_id' label='Service'  value={this.state.data.type_id} options={this.state.services.map(row => ({value:row, text:`${row.service} (${row.type})`}))} onChange={this.onChange} />
      <UrlInput key='ui' id='ui' label='UI' value={this.state.data.ui} onChange={this.onChange} />
     </InfoCol2>
     <InfoButton key='srv_save' type='save' onClick={() => this.updateInfo('api/master/server_info')} />
     {old && <InfoButton key='srv_sync' type='sync' onClick={() => {      this.changeContent(<Operation key={'srv_op_sync'} id={this.props.id} operation='sync' />) }} />}
     {old && <InfoButton key='srv_restart' type='reload' onClick={() => { this.changeContent(<Operation key={'srv_op_rst'}  id={this.props.id} operation='restart' />) }} />}
     {old && <InfoButton key='srv_status'  type='items'  onClick={() => { this.changeContent(<Operation key={'srv_op_stat'} id={this.props.id} operation='status' />) }} />}
    </article>
    <NavBar key='srv_navbar' />
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
