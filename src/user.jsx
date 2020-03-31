import React, { Component, Fragment } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoColumns, RimsContext, ContentList, ContentData } from './infra/UI.jsx';
import { AddButton, DeleteButton, ConfigureButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';
import { TextInput, PasswordInput, SelectInput } from './infra/Inputs.jsx';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/user_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.alias,row.name,<Fragment key={'ul_buttons_'+row.id}>
   <ConfigureButton key={'ul_btn_info_'+row.id}  onClick={() => this.changeContent(<Info key={'user_info_'+row.id} id={row.id} />)} />
   <DeleteButton key={'ul_btn_del_'+row.id} onClick={() => this.deleteList(row.id)} />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete user?') && rest_call('api/master/user_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='ul_fragment'>
   <ContentList key='ul_cl' header='Users' thead={['ID','Alias','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='ul_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='ul_btn_add' onClick={() => this.changeContent(<Info key={'user_new_' + rnd()} id='new' />) } />
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
  rest_call('api/system/theme_list').then(result => this.setState({themes:result}))
  rest_call('api/master/user_info',{id:this.props.id}).then(result => this.setState(result))
 }

 updateInfo = (api) => {
  if(this.context.cookie.id === this.state.data.id)
   this.context.setCookie({...this.context.cookie, theme:this.state.data.theme});
  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <article>User with id: {this.props.id} removed</article>
  else if (this.state.data && this.state.themes){
   return (
    <article className='info'>
     <h1>User</h1>
     <InfoColumns key='ui_content'>
      <TextInput key='alias' id='alias' value={this.state.data.alias} onChange={this.onChange} />
      <PasswordInput key='password' id='password' placeholder='******' onChange={this.onChange} />
      <TextInput key='email' id='email' label='E-Mail' value={this.state.data.email} onChange={this.onChange} />
      <TextInput key='name' id='name' label='Full name' value={this.state.data.name} onChange={this.onChange} />
      <SelectInput key='theme' id='theme' value={this.state.data.theme} onChange={this.onChange}>{this.state.themes.map(row => <option key={'ui_theme_'+row} value={row}>{row}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='ui_btn_save' onClick={() => this.updateInfo('api/master/user_info') } />
    </article>
   );
  } else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// ************** User **************
//
export class User extends Component {
 render() {
  return <div className='flexdiv centered'><Info id={this.props.id} /></div>
 }
}
