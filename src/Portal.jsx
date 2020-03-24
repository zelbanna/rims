import React, { Component } from 'react';
import { rest_call } from  './infra/Functions.js';
import Library from './infra/Mapper.js'
import { InfoCol2, RimsContext } from './infra/Generic.js';
import { TextInput, PasswordInput } from './infra/Inputs.jsx';
import { MenuButton } from './infra/Buttons.jsx';
import { NavBar } from './infra/Navigation.js';

// CONVERTED ENTIRELY

// ************************* Header ****************************
//
const Header = (props) => <header>{props.children}</header>

// ************************* Portal  ****************************
//
class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { content:null, menu:[], navigation:null, cookie:null}
 }

 componentDidMount() {
  this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation});
  rest_call('api/portal/menu',{id:this.context.cookie.id}).then(result => {
    this.setState(result)
    result.start && this.changeContent(result.menu[result.start]);
    document.title = result.title;
   })
 }

 loadNavigation = (items) => this.setState({navigation:items})

 changeContent = (panel) => {
  if (panel.hasOwnProperty('module')) {
   if (this.state.content && (this.state.content.key === `${panel.module}_${panel.function}`))
    return
   try {
    var Elem = Library[panel.module][panel.function]
    this.setState({navigation:[],content:<Elem key={panel.module + '_' + panel.function} {...panel.args} />})
   } catch(err) {
    console.error("Mapper error: "+panel);
    alert(err);
   }
  } else
   this.setState(panel)
 }

 render() {
  let buttons = []
  for (let [key, panel] of Object.entries(this.state.menu)){
   let click = null
   if (panel.type === 'module')
    click = () => this.changeContent(panel)
   else if (panel.type === 'tab')
    click = () => window.open(panel.tab,'_blank')
   else if (panel.type === 'frame')
    click = () => this.changeContent({content:<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>,navigation:null})
   panel.title = key
   buttons.push(<MenuButton key={'mb_'+key} {...panel} onClick={click} />)
  }
  return (
   <React.Fragment key='portal'>
    <link key='userstyle' rel='stylesheet' type='text/css' href={'infra/theme.' + this.context.cookie.theme + '.react.css'} />
    <Header key='portal_header'>
     <MenuButton key='mb_Logout' className='right warning' onClick={() => { this.context.clearCookie()}} title='Log out' />
     <MenuButton key='mb_System_Main' className='right' onClick={() => {this.changeContent({module:'System',function:'Main'})}} title='System' icon='images/icon-config.png' />
     <MenuButton key='mb_User_User' className='right' onClick={() => {this.changeContent({module:'User',function:'User', args:{id:this.context.cookie.id}})}} title='User' icon='images/icon-users.png' />
     {buttons}
    </Header>
    <NavBar key='portal_navigation'>{this.state.navigation}</NavBar>
    <main>{this.state.content}</main>
  </React.Fragment>
  )
 }
}
Portal.contextType = RimsContext;

// ************************ Login ************************
class Login extends Component {
 constructor(props){
  super(props)
  this.state = {message:'',username:'username',password:'password'}
 }

 componentDidMount() {
  rest_call('front').then(result => {
   this.setState(result)
   document.title = result.title
  })
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 handleSubmit = (event) => {
  event.preventDefault();
  rest_call('auth',{username:this.state.username,password:this.state.password})
   .then((result) => {
    if (result.status === 'OK')
     this.props.setCookie({node:result.node,token:result.token,id:result.id,theme:result.theme,expires:result.expires});
    else {
     document.getElementById("password").value = "";
     this.setState(prevState => ({ ...prevState,   password : '' }))
    }
   })
 }

 render() {
  return (
   <div className='login'>
    <article className='login'>
     <h1 className='centered'>{this.state.message}</h1>
     <InfoCol2 className={'left'}>
      <TextInput key='username' id='username' onChange={this.onChange} />
      <PasswordInput key='password' id='password' onChange={this.onChange} />
     </InfoCol2>
     <MenuButton icon='images/icon-start.png' title='Start' onClick={this.handleSubmit}/>
    </article>
   </div>
  )
 }
}

// ************************** App *************************

class RIMS extends Component {
 constructor(props) {
  super(props);

  this.state = this.readCookie();
  this.provider = {}
 }

 readCookie = () => {
  var cookies = document.cookie.split("; ");
  for(var i=0;i < cookies.length;i++) {
   var c = cookies[i];
   if (c.indexOf("rims=") === 0)
    // Parse from 5th letter to end
    return JSON.parse(atob(c.substring(5,c.length)));
  }
  return {token:null};
 }

 clearCookie = () => {
  document.cookie = "rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  this.setState({token:null})
 }

 setCookie = (cookie) => {
  const encoded = btoa(JSON.stringify(cookie));
  document.cookie = "rims=" + encoded + "; expires=" + cookie.expires + "; Path=/";
  this.setState(cookie)
 }

 providerMounting = (options) => {
  Object.assign(this.provider,options);
  this.forceUpdate();
 }

 render(){
  return (
   <RimsContext.Provider value={{setCookie:this.setCookie,clearCookie:this.clearCookie,cookie:this.state,...this.provider}}>
    {(this.state.token === null) ?<Login setCookie={this.setCookie}/> : <Portal providerMounting={this.providerMounting} />}
   </RimsContext.Provider>
  )
 }
}

export default RIMS
