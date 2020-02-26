import React, { Component, Fragment } from 'react';
import { List as ReservationList } from './Reservation.js';
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { InfoButton, ButtonGenerator } from './infra/Buttons.js';
import { ContentMain } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:null, id:null, name:null}
 }

 componentDidMount(){
  const cookie = read_cookie('rims');
  rest_call(rest_base + 'api/master/user_info',{id:cookie.id})
   .then((result) => {
    this.setState({name:result.data.name, id:cookie.id})
    this.compileNavItems()
   })
 }

 content = (elem) => {
  this.setState({content:elem})
 }

 compileNavItems = () => {
  this.props.loadNavigation([
   {title:'Users', onClick:() => { this.content(<List key='user_list' />)}},
   {title:'Reservations', onClick:() => { this.content(<ReservationList key='reservation_list' />)}},
   {title:this.state.name, className:'right navinfo'}
  ])
 }

 render() {
  return <Fragment key='user_main'>{this.state.content}</Fragment>
 }
}

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, content:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/user_list')
   .then((result) => { this.setState(result); })
 }

 changeContent = (elem) => { this.setState({content:elem}) }

 deleteItem = (id,msg) => {
  if (window.confirm(msg)){
   rest_call(rest_base + 'api/master/user_delete',{id:id})
    .then((result) => {
     if(result.deleted)
      this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id),content:null})
    })
  }
 }

 listItem = (row) => {
  return [row.id,row.alias,row.name,<Fragment key={'user_buttons_'+row.id}>
   <InfoButton key={'user_info_'+row.id} type='info' onClick={() => { this.changeContent(<Info key={'user_info_'+row.id} id={row.id} />)}} />
   <InfoButton key={'user_del_'+row.id} type='trash' onClick={() => { this.deleteItem(row.id,'Really delete user?')}} />
  </Fragment>]
 }

 render() {
  return <ContentMain key='user_content' base='user' header='Users' thead={['ID','Alias','Name','']}
    trows={this.state.data} content={this.state.content} listItem={this.listItem} buttons={<Fragment key='user_header_buttons'>
      <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />
      <InfoButton key='add'    type='add'    onClick={() => {this.changeContent(<Info key={'user_new_'+Math.floor(Math.random() * 10)} id='new' />)}} />
    </Fragment>} />
 }
}

// ************** Info **************
//
export class Info extends Component {
 constructor(props) {
  super(props)
  const cookie = read_cookie('rims');
  this.state = {data:null, found:true, cookie_id:cookie.id, themes:null}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/theme_list')
   .then((result) => {
    this.setState({themes:result});
   })
  rest_call(rest_base + 'api/master/user_info',{id:this.props.id})
   .then((result) => { this.setState(result); })
 }

 updateInfo = (event) => {
  rest_call(rest_base + 'api/master/user_info',{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => {
  return [
    {tag:'input', type:'text', id:'alias', text:'Alias', value:this.state.data.alias},
    {tag:'input', type:'password', id:'password', text:'Password',placeholder:'******'},
    {tag:'input', type:'text', id:'email', text:'e-mail', value:this.state.data.email},
    {tag:'input', type:'text', id:'name', text:'Full name', value:this.state.data.name},
    {tag:'select', id:'theme', text:'Theme', value:this.state.data.theme, options:this.state.themes.map((row) => { return ({value:row, text:row})})}
   ]
 }

 render() {
  if (this.state.found === false)
   return <article>User with id: {this.props.id} removed</article>
  else if ((this.state.data === null) || (this.state.themes === null))
   return <Spinner />
  else {
   const className = (this.props.hasOwnProperty('className')) ? `info ${this.props.className}` : 'info';
   return (
    <article className={className}>
     <h1>User Info ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='user_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='user_save' type='save' onClick={this.updateInfo} />
    </article>
   );
  }
 }
}

// ************** User **************
//
export class User extends Component {
 render() {
  return (
   <Fragment key='user_user'>
    <Info className='centered' id={this.props.id} />
   </Fragment>
  )
 }
}
