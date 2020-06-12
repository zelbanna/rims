import React, { Component, Fragment } from 'react';
import { post_call, rnd } from './infra/Functions.js';
import { RimsContext, Flex, Spinner, InfoArticle, InfoColumns, ContentList, ContentData, Result } from './infra/UI.jsx';
import { AddButton, DeleteButton, ConfigureButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';
import { TextInput, TextLine, PasswordInput, SelectInput } from './infra/Inputs.jsx';

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/master/user_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.alias,row.name,<Fragment>
   <ConfigureButton key={'ul_btn_info_'+row.id}  onClick={() => this.changeContent(<Info key={'user_info_'+row.id} id={row.id} />)} title='Edit user' />
   <DeleteButton key={'ul_btn_del_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete user' />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete user?') && post_call('api/master/user_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment>
   <ContentList key='ul_cl' header='Users' thead={['ID','Alias','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='ul_btn_reload' onClick={() => this.componentDidMount()} />
    <AddButton key='ul_btn_add' onClick={() => this.changeContent(<Info key={'user_new_' + rnd()} id='new' />)} title='Add user' />
   </ContentList>
   <ContentData key='ul_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Info **************
//
export class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 componentDidMount(){
  post_call('api/portal/theme_list').then(result => this.setState({themes:result.data}))
  post_call('api/master/user_info',{id:this.props.id}).then(result => this.setState(result))
 }

 updateInfo = () => {
  this.setState({update:false,password_check:''})
  if(this.context.settings.id === this.state.data.id)
   this.context.changeTheme(this.state.data.theme);
  post_call('api/master/user_info',{op:'update', ...this.state.data},{'X-Log':'false'}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <InfoArticle key='ui_art'>User with id: {this.props.id} removed</InfoArticle>
  else if (this.state.data && this.state.themes){
   let result = (this.state.update) ? 'OK - updated' : '';
   return <InfoArticle key='ui_art' header='User'>
     <InfoColumns key='ui_content'>
      {(this.context.settings.id === this.props.id) ?  <TextLine key='alias' id='alias' text={this.state.data.alias} /> : <TextInput key='alias' id='alias' value={this.state.data.alias} onChange={this.onChange} />}
      <PasswordInput key='password' id='password' placeholder='******' onChange={this.onChange} />
      {this.context.settings.class === 'admin' && <SelectInput key='class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput>}
      <TextInput key='email' id='email' label='E-Mail' value={this.state.data.email} onChange={this.onChange} />
      <TextInput key='name' id='name' label='Full name' value={this.state.data.name} onChange={this.onChange} />
      <SelectInput key='theme' id='theme' value={this.state.data.theme} onChange={this.onChange}>{this.state.themes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='ui_btn_save' onClick={() => this.updateInfo()} title='Save' />
     <Result key='ui_operation' result={result} />
    </InfoArticle>
  } else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// ************** User **************
//
export class User extends Component {
 render() {
  return <Flex key='u_flex' style={{justifyContent:'space-evenly'}}><Info id={this.props.id} /></Flex>
 }
}
