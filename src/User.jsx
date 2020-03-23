import React, { Component, Fragment } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, RimsContext, ContentList, ContentData } from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.jsx';
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

 listItem = (row) => [row.id,row.alias,row.name,<Fragment key={'user_buttons_'+row.id}>
   <InfoButton key={'user_info_'+row.id} type='info' onClick={() => { this.changeContent(<Info key={'user_info_'+row.id} id={row.id} />)}} />
   <InfoButton key={'user_del_'+row.id} type='delete' onClick={() => { this.deleteList('api/master/user_delete',row.id,'Really delete user?')}} />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='usr_fragment'>
   <ContentList key='usr_cl' header='Users' thead={['ID','Alias','Name','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='usr_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='usr_btn_add' type='add' onClick={() => this.changeContent(<Info key={'user_new_' + rnd()} id='new' />) } />
   </ContentList>
   <ContentData key='usr_cd'>{this.state.content}</ContentData>
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

 changeHandler = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

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
     <h1>User Info</h1>
     <InfoCol2 key='user_content'>
      <TextInput key='alias' id='alias' value={this.state.data.alias} changeHandler={this.changeHandler} />
      <PasswordInput key='password' id='password' placeholder='******' changeHandler={this.changeHandler} />
      <TextInput key='email' id='email' label='E-Mail' value={this.state.data.email} changeHandler={this.changeHandler} />
      <TextInput key='name' id='name' label='Full name' value={this.state.data.name} changeHandler={this.changeHandler} />
      <SelectInput key='theme' id='theme' value={this.state.data.theme} options={this.state.themes.map(row => ({value:row, text:row}))} changeHandler={this.changeHandler} />
     </InfoCol2>
     <InfoButton key='usr_btn_save' type='save' onClick={() => this.updateInfo('api/master/user_info') } />
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
