import React, { Component } from 'react';

import { read_cookie, rest_call, rest_base, library } from  './infra/Functions.js';
import { InfoCol2 }   from './infra/Info.js';
import { MenuButton } from './infra/Buttons.js';
import { NavBar } from './infra/Navigation.js';

const styleLoginButton = {margin:'10px 10px 10px 10px'};

// CONVERTED ENTIRELY

// ************************* Portal  ****************************
//
class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { active:null, active_name:null, menu:[], navigation:null}
 }

 componentDidMount() {
  rest_call(rest_base + 'api/portal/menu',{id:this.props.cookie.id})
   .then((result) => {
    this.setState(result)
    if (result.start)
     this.changeActive(result.menu[result.start]);
    document.title = result.title
   })
 }

 loadNavigation = (items) => {
  this.setState({navigation:items})
 }

 changeActive = (panel) => {
  if ('module' in panel){
   if ((this.state.active !== null) && (this.state.active.key === panel.module))
    return
   try {
    const parts = panel.module.split('_');
    const module = library[parts[0]];
    const Elem = module[parts[1].charAt(0).toUpperCase() + parts[1].substring(1)];
    this.setState({navigation:[],active:<Elem key={panel.module} {...panel.args} loadNavigation={this.loadNavigation} />})
   } catch(err) {
    console.error("Mapper error: "+panel);
    alert(err);
   }
  }
 }

 Header(props){
  return (
   <header>
    <MenuButton key='logout' className='right warning' onClick={() => {props.eraseCookie()} } title='Log out' />
    <MenuButton key='system_main' className='right'         onClick={() => {props.changeActive({module:'system_main'})}} title='System' icon='images/icon-config.png' />
    <MenuButton key='user_user'   className='right'         onClick={() => {props.changeActive({module:'user_user', args:{id:props.cookie.id}})}}   title='User'   icon='images/icon-users.png' />
    { Object.values(props.menu).map((row) => { return (<MenuButton key={row[row['type']]} {...row} onClick={() => {props.changeActive({module:row.module, args:row.args})}} />); }) }
   </header>
  )
 }

 render() {
  return (
   <React.Fragment key='portal'>
    <link key='userstyle' rel='stylesheet' type='text/css' href={'infra/theme.' + this.props.cookie.theme + '.react.css'} />
    <this.Header key='portal_header' menu={this.state.menu} changeActive={this.changeActive} {...this.props} />
    <NavBar key='portal_navigation' items={this.state.navigation} />
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
  return (this.state.token === null) ?<Login setCookie={this.setCookie}/> : <Portal cookie={this.state} eraseCookie={this.eraseCookie}/>
 }
}

export default App
