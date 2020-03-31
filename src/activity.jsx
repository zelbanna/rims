import React, { Fragment, Component } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { InfoColumns, Spinner, RimsContext, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextInput, SelectInput, DateInput, TimeInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, ConfigureButton, InfoButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';
import { NavBar, NavButton } from './infra/Navigation.js';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends Component {
 componentDidMount(){
  this.context.loadNavigation(<NavBar key='activity_navbar'>
   <NavButton key='act_nav_list' title='Activities' onClick={() => this.changeContent(<List key='activity_list' />)} />
   <NavButton key='act_nav_types' title='Types' onClick={() => this.changeContent(<TypeList key='activity_type_list' />)} />
   <NavButton key='act_nav_report' title='Report' onClick={() => this.changeContent(<Report key='activity_report' />)} />
  </NavBar>)
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }

}
Main.contextType = RimsContext;

// ************** List **************
//
class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/activity_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.date + ' - ' + row.time,row.type,<Fragment key={'activity_buttons_'+row.id}>
   <InfoButton key={'act_info_'+row.id} onClick={() => this.changeContent(<Info key={'activity_'+row.id} id={row.id} />) } title='Activity information' />
   <DeleteButton key={'act_delete_'+row.id} onClick={() => this.deleteList(row.id) } title='Delete activity' />
   </Fragment>
  ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Delete activity') && rest_call('api/master/activity_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='act_fragment'>
   <ContentList key='act_cl' header='Activities' thead={['Date','Type','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='act_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='act_btn_add' onClick={() => this.changeContent(<Info key={'activity_new_' + rnd()} id='new' />) } title='Add activity' />
   </ContentList>
   <ContentData key='act_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// *************** Info ***************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/master/activity_info',{id:this.props.id}).then(result => {
   if (result.data.user_id === null)
    result.data.user_id = this.context.cookie.id;
   this.setState(result);
  })
 }

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Activity</h1>
     <InfoColumns key='activity_content'>
      <SelectInput key='user_id' id='user_id' label='User' value={this.state.data.user_id} onChange={this.onChange}>{this.state.users.map((row,idx) => <option key={'ai_u_'+idx} value={row.id}>{row.alias}</option>)}</SelectInput>
      <SelectInput key='type_id' id='type_id' label='Type' value={this.state.data.type_id} onChange={this.onChange}>{this.state.types.map((row,idx) => <option key={'ai_t_'+idx} value={row.id}>{row.type}</option>)}</SelectInput>
      <DateInput key='date' id='date' value={this.state.data.date} onChange={this.onChange} />
      <TimeInput key='time' id='time' value={this.state.data.time} onChange={this.onChange} />
     </InfoColumns>
     <label htmlFor='event'>Info</label><textarea id='event' name='event' onChange={this.onChange} value={this.state.data.event} />
     <SaveButton key='activity_save' onClick={() => this.updateInfo('api/master/activity_info')} title='Save' />
    </article>
   );
  else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// ************** Report **************
//
export class Report extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/activity_list',{group:'month',mode:'full'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.date + ' - ' + row.time,row.user,row.type,row.event]

 render(){
  return <ContentReport key='act_cr' header='Activities' thead={['Time','User','Type','Event']} trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** TypeList **************
//
class TypeList extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/activity_type_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.type,<Fragment key='activity_buttons'>
   <ConfigureButton key='act_tp_info' onClick={() => this.changeContent(<TypeInfo key={'activity_type_'+row.id} id={row.id} />) } title='Edit type information' />
   <DeleteButton key='act_tp_delete' onClick={() => this.deleteList(row.id) } title='Delete type' />
  </Fragment>
 ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete type?') && rest_call('api/master/activity_type_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='act_tp_fragment'>
   <ContentList key='act_tp_cl' header='Activity Types' thead={['ID','Type','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='act_tp_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='act_tp_btn_add' onClick={() => this.changeContent(<TypeInfo key={'act_tp_new_' + rnd()} id='new' />) } title='Add activity type' />
   </ContentList>
   <ContentData key='act_tp_cd'>{this.state.content}</ContentData>
  </Fragment>
 }

}

// *************** TypeInfo ***************
//
class TypeInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true, content:null};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/master/activity_type_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Activity Type</h1>
     <InfoColumns key='activity_type_content'>
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} placeholder='name' />
     </InfoColumns>
     <SaveButton key='activity_type_save' onClick={() => this.updateInfo('api/master/activity_type_info')} title='Save' />
    </article>
   );
  else
   return <Spinner />
 }
}
