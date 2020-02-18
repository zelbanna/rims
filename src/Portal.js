import React, { Component } from 'react';

import { read_cookie, rest_call, rest_base, mapper } from  './Functions.js';
import { DivInfoCol2, MenuButton } from './UI.js';

const styleLoginButton = {fontSize:'18px', margin:'10px 10px 10px 10px'};

// ************************* Portal  ****************************

class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { active:null, menu:[]}
 }

 componentDidMount() {
  rest_call(rest_base + 'api/portal/react_menu',{id:this.props.cookie.id})
   .then((result) => {
    this.setState(result)
    console.log(result)
    if (result.start){
     this.changeActive(result.menu[0]);
    }
    document.title = result.title
    // TODO: add start to active here...
   })
 }

 changeActive = (panel) => {
  var elem = null;
  if ('module' in panel) {
   elem = mapper(panel)
  }
  this.setState(() => { return {active:elem} })
 }

 render() {
  const styleSheet = 'theme.' + this.props.cookie.theme + '.css'
  const active = this.state.active;
  const menuitems = this.state.menu.map((row,index) => {
   return (<MenuButton key={index} {...row} onClick={() => {this.changeActive({module:row.module, args:row.args})}} />);
  });

  return (
   <React.Fragment key='portal'>
    <link key='userstyle' rel='stylesheet' type='text/css' href={styleSheet} />
    <header>
     <MenuButton key='logout' className='right warning' onClick={() => {this.props.eraseCookie()} } title='Log out' />
     <MenuButton key='system' className='right'         onClick={() => {this.changeActive({module:'system_main'})}} title='System' icon='images/icon-config.png' />
     <MenuButton key='user'   className='right'         onClick={() => {this.changeActive({module:'user_user', args:{id:this.props.cookie.id}})}}   title='User'   icon='images/icon-users.png' />
     {menuitems}
    </header>
    <main>{active}</main>
   </React.Fragment>
  )
 }
}

// ************************ Login ************************
class Login extends Component {
 constructor(props){
  super(props)
  this.state = {message:'',username:'username',password:'password'}
 }

 componentDidMount() {
  rest_call(rest_base + 'api/portal/application')
   .then((result) => {
    this.setState(result)
    document.title = result.title
   })
 }

 handleChange = (event) => {
  this.state[event.target.name] = event.target.value
 }

 handleSubmit = (event) => {
  event.preventDefault();
  rest_call(rest_base + 'auth',{username:this.state.username,password:this.state.password})
   .then((result) => {
    if (result.status === 'OK'){
     this.props.setCookie({node:result.node,token:result.token,id:result.id,theme:result.theme},result.expires);
    } else {
     document.getElementById("password").value = "";
     this.setState(prevState => ({ ...prevState,   password : '' }))
    }
   })
 }

 render() {
  const message = this.state.message
  const griditems = [{element:'input', type:'text', id:'username', text:'Username'},{element:'input', type:'password', id:'password', text:'Password'}]
  return (
   <div className='background overlay'>
    <article className='login'>
     <h1 className='centered'>{message}</h1>
     <form>
      <DivInfoCol2 griditems={griditems} changeHandler={this.handleChange} className={'left'}/>
     </form>
     <MenuButton icon='images/icon-start.png' title='Start' style={styleLoginButton} onClick={this.handleSubmit}/>
    </article>
   </div>
  )
 }
}

// ************************** App *************************

class App extends Component {
 constructor(props) {
  super(props);

  const cookie = read_cookie('rims');
  this.state = (cookie) ? cookie : {token:null}
 }

 eraseCookie = () => {
  document.cookie = "rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  this.setState(() => { return {token:null}})
 }

 setCookie = (cookie,expires) => {
  const encoded = btoa(JSON.stringify(cookie));
  document.cookie = "rims=" + encoded + "; expires=" + expires + "; Path=/";
  this.setState(() => { return cookie; })
 }

 render() {
  return ((this.state.token === null) ?<Login setCookie={this.setCookie}/> : <Portal cookie={this.state} setCookie={this.setCookie} eraseCookie={this.eraseCookie}/>);
 }
}

export default App
