import React, { Component } from 'react';

import { read_cookie, rest_call, rest_base, mapper } from  './infra/Functions.js';
import { InfoCol2 }   from './infra/Info.js';
import { MenuButton } from './infra/Buttons.js';

const styleLoginButton = {fontSize:'18px', margin:'10px 10px 10px 10px'};

// CONVERTED ENTIRELY

// ************************* Portal  ****************************
//
class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { active:null, menu:[]}
 }

 componentDidMount() {
  rest_call(rest_base + 'api/portal/menu',{id:this.props.cookie.id})
   .then((result) => {
    this.setState(result)
    if (result.start){
     this.changeActive(result.menu[0]);
    }
    document.title = result.title
   })
 }

 changeActive = (panel) => {
  var elem = null;
  if ('module' in panel) {
   elem = mapper(panel)
  }
  this.setState({active:elem})
 }

 render() {
  return (
   <React.Fragment key='portal'>
    <link key='userstyle' rel='stylesheet' type='text/css' href={'infra/theme.' + this.props.cookie.theme + '.react.css'} />
    <header>
     <MenuButton key='logout' className='right warning' onClick={() => {this.props.eraseCookie()} } title='Log out' />
     <MenuButton key='system' className='right'         onClick={() => {this.changeActive({module:'system_main'})}} title='System' icon='images/icon-config.png' />
     <MenuButton key='user'   className='right'         onClick={() => {this.changeActive({module:'user_user', args:{id:this.props.cookie.id}})}}   title='User'   icon='images/icon-users.png' />
     { this.state.menu.map((row,index) => { return (<MenuButton key={index} {...row} onClick={() => {this.changeActive({module:row.module, args:row.args})}} />); }) }
    </header>
    <main>{this.state.active}</main>
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

 handleChange = (e) => {
  this.setState({[e.target.name]:e.target.value});
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
  const griditems = [{tag:'input', type:'text', id:'username', text:'Username'},{tag:'input', type:'password', id:'password', text:'Password'}]
  return (
   <div className='background overlay'>
    <article className='login'>
     <h1 className='centered'>{this.state.message}</h1>
     <form>
      <InfoCol2 griditems={griditems} changeHandler={this.handleChange} className={'left'}/>
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
  return (this.state.token === null) ?<Login setCookie={this.setCookie}/> : <Portal cookie={this.state} setCookie={this.setCookie} eraseCookie={this.eraseCookie}/>
 }
}

export default App
