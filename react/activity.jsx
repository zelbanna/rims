import React, { Fragment, Component } from 'react';
import { post_call, rnd } from './infra/Functions.js';
import { RimsContext, Result, InfoArticle, InfoColumns, Spinner, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextLine, TextAreaInput, TextInput, SelectInput, DateInput, TimeInput, SearchInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, ConfigureButton, HrefButton, InfoButton, ReloadButton, SaveButton, SyncButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton } from './infra/Navigation.jsx';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <Daily key='activity_daily' />
 }

 componentDidMount(){
  this.compileNavItems()
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props){
   this.compileNavItems()
  }
 }

 compileNavItems = () => this.context.loadNavigation(<NavBar key='activity_navbar'>
   <NavDropDown key='act_nav' title='Activities'>
   <NavDropButton key='act_nav_new' title='New' onClick={() => this.changeContent(<Info key='activity_info' id='new' />)} />
   <NavDropButton key='act_nav_day' title='Daily' onClick={() => this.changeContent(<Daily key='activity_daily' changeSelf={this.changeContent} />)} />
   <NavDropButton key='act_nav_list' title='List' onClick={() => this.changeContent(<List key='activity_list' />)} />
   </NavDropDown>
   <NavButton key='act_nav_types' title='Types' onClick={() => this.changeContent(<TypeList key='activity_type_list' />)} />
   <NavButton key='act_nav_report' title='Report' onClick={() => this.changeContent(<Report key='activity_report' />)} />
  </NavBar>)

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
  this.state = {searchfield:''}
 }

 componentDidMount(){
  post_call('api/master/activity_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.date + ' - ' + row.time,<HrefButton key={'al_btn_hinfo_'+row.id} onClick={() => this.changeContent(<Info key={'activity_info_'+row.id} id={row.id} />)} text={row.type} />,<Fragment key={'activity_buttons_'+row.id}>
   <InfoButton key={'al_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'activity_'+row.id} id={row.id} />) } title='Activity information' />
   <DeleteButton key={'al_btn_delete_'+row.id} onClick={() => this.deleteList(row.id) } title='Delete activity' />
   </Fragment>
  ]

 searchHandler = (e) => { this.setState({searchfield:e.target.value}) }

 changeContent = (elem) => this.setState({content:elem})

 deleteList = (id) => (window.confirm('Delete activity') && post_call('api/master/activity_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  if (this.state.data) {
   let activity_list = this.state.data.filter(row => row.type.includes(this.state.searchfield));
   return <Fragment key='al_fragment'>
    <ContentList key='al_cl' header='Activities' thead={['Date','Type','']} trows={activity_list} listItem={this.listItem}>
     <ReloadButton key='al_btn_reload' onClick={() => this.componentDidMount() } />
     <AddButton key='al_btn_add' onClick={() => this.changeContent(<Info key={'activity_new_' + rnd()} id='new' />) } title='Add activity' />
     <SearchInput key='al_search' searchHandler={this.searchHandler} value={this.state.searchfield} placeholder='Search activities' />
    </ContentList>
    <ContentData key='al_cd'>{this.state.content}</ContentData>
   </Fragment>
  } else
   return <Spinner />
 }
}

// *************** Info ***************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = () => {
  post_call('api/master/activity_info',{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 componentDidMount(){
  post_call('api/master/activity_info',{id:this.props.id, extras:['types','users']}).then(result => {
   if (result.data.user_id === null)
    result.data.user_id = this.context.settings.id;
   this.setState(result);
  })
 }

 render() {
  if (this.state.data)
   return <InfoArticle key='ai_art' header='Activity'>
     <InfoColumns key='ai_content'>
      <TextLine key='ai_id' id='id' label='ID' text={this.state.data.id} />
      <SelectInput key='ai_user_id' id='user_id' label='User' value={this.state.data.user_id} onChange={this.onChange}>{this.state.users.map((row,idx) => <option key={'ai_u_'+idx} value={row.id}>{row.alias}</option>)}</SelectInput>
      <SelectInput key='ai_type_id' id='type_id' label='Type' value={this.state.data.type_id} onChange={this.onChange}>{this.state.types.map((row,idx) => <option key={'ai_t_'+idx} value={row.id}>{row.type}</option>)}</SelectInput>
      <DateInput key='ai_date' id='date' value={this.state.data.date} onChange={this.onChange} />
      <TimeInput key='ai_time' id='time' value={this.state.data.time} onChange={this.onChange} />
     </InfoColumns>
     <TextAreaInput key='ai_event' id='event' value={this.state.data.event} onChange={this.onChange} />
     <SaveButton key='ai_btn_save' onClick={() => this.updateInfo()} title='Save' />
     <Result key='ai_result' result={JSON.stringify(this.state.update)} />
    </InfoArticle>
  else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// *************** Daily ***************
//
class Daily extends Component {
 constructor(props){
  super(props);
  const date = new Date(Date.now());
  this.state = {data:[], date:date.toISOString().substring(0,10), user_id:undefined, users:{}}
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 componentDidMount(){
  post_call('api/master/activity_daily',{extras:['users']}).then(result => this.setState({...result, user_id:this.context.settings.id}));
 }

 deleteList = (activity_id) => (window.confirm('Delete activity') && post_call('api/master/activity_delete', {id:activity_id}).then(result => {
  if(result.deleted){
   const idx = this.state.data.findIndex(obj => obj.act_id === activity_id);
   const data = this.state.data[idx];
   Object.assign(data,{user_id:null, event:null, act_id:null});
   this.setState({data:this.state.data})
  }
 }))

 onChange = (e) => {
  const field = e.target.name;
  const value = e.target.value;
  const args = {date:(field === 'date') ? value : this.state.date};
  post_call('api/master/activity_daily',args).then(result => this.setState({...result, [field]:value}));
 }

 syncEvent = (type_id,activity_id) =>
  post_call('api/master/activity_info',{op:'update', id:(activity_id) ? activity_id : 'new', user_id:this.state.user_id, type_id:type_id, event:'auto', date:this.state.date}).then(result => {
   if(result.update){
    const idx = this.state.data.findIndex(obj => obj.id === type_id);
    const data = this.state.data[idx];
    Object.assign(data,{user_id:this.state.user_id, event:'auto', act_id:result.data.id});
    this.setState({data:this.state.data})
   }
  })

 listItem = (row) => {
  return [row.type, (row.user_id) ? this.state.users[row.user_id].alias : '-', (row.event) ? row.event : '-',<Fragment key={'ad_btn_'+row.id}>
  {!row.user_id && <AddButton key={'ad_add_'+row.id} onClick={() => this.syncEvent(row.id,row.act_id)} />}
  {row.user_id && row.user_id !== parseInt(this.state.user_id) && <SyncButton key={'ad_sync_'+row.id} onClick={() => this.syncEvent(row.id,row.act_id)} />}
  {row.act_id && <InfoButton key={'ad_info'} onClick={() => this.changeContent(<Info key={'activity_'+row.act_id} id={row.act_id} />)} />}
  {row.act_id && <DeleteButton key={'ad_del'} onClick={() => this.deleteList(row.act_id)} />}
  </Fragment>]
 }

 render(){
  if (this.state.data)
   return <ContentReport key='ad_cr' header='Activities' thead={['Type','User','Event','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='ad_reload_btn' onClick={() => this.componentDidMount()} />
    <SelectInput key='ad_user_id' id='user_id' label='User' value={this.state.user_id} onChange={this.onChange}>{Object.values(this.state.users).map((row,idx) => <option key={'ai_u_'+idx} value={row.id}>{row.alias}</option>)}</SelectInput>
    <DateInput key='ad_date' id='date' value={this.state.date} onChange={this.onChange} />
   </ContentReport>
  else
   return <Spinner />
 }
}
Daily.contextType = RimsContext;

// ************** Report **************
//
export class Report extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/master/activity_list',{group:'month',mode:'full'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.date + ' - ' + row.time,row.user,row.type,row.class,row.event]

 render(){
  return <ContentReport key='act_cr' header='Activities' thead={['Time','User','Type','Class','Event']} trows={this.state.data} listItem={this.listItem} />
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
  post_call('api/master/activity_type_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.type,row.class,<Fragment key='activity_buttons'>
   <ConfigureButton key='act_tp_info' onClick={() => this.changeContent(<TypeInfo key={'activity_type_'+row.id} id={row.id} />) } title='Edit type information' />
   <DeleteButton key='act_tp_delete' onClick={() => this.deleteList(row.id) } title='Delete type' />
  </Fragment>
 ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete type?') && post_call('api/master/activity_type_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='act_tp_fragment'>
   <ContentList key='act_tp_cl' header='Activity Types' thead={['ID','Type','Class','']} trows={this.state.data} listItem={this.listItem}>
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
  this.state = {data:null, content:null};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () =>  post_call('api/master/activity_type_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  post_call('api/master/activity_type_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return (
    <InfoArticle key='at_art' header='Activity Type'>
     <InfoColumns key='at_content'>
      <TextLine key='id' id='id' text={this.state.data.id} />
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} placeholder='name' />
      <SelectInput key='class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={'at_class_'+row} value={row}>{row}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='at_save' onClick={() => this.updateInfo()} title='Save' />
    </InfoArticle>
   )
  else
   return <Spinner />
 }
}
