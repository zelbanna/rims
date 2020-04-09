import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './infra/system.css';
import { rest_call } from  './infra/Functions.js';
import { InfoColumns, RimsContext, Header, Theme } from './infra/UI.jsx';
import { TextInput, TextLine, PasswordInput } from './infra/Inputs.jsx';
import { CloseButton, MenuButton, FontAwesomeMenuButton } from './infra/Buttons.jsx';
import { NavBar } from './infra/Navigation.js';
import * as serviceWorker from './serviceWorker';

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

// ************************* Portal  ****************************
//

class ErrorBoundary extends React.Component {
 constructor(props) {
  super(props);
  this.state = { hasError: false, error: undefined, info:[] };
 }

 static getDerivedStateFromError(error) {
  return {hasError: true};
 }

 componentDidCatch(error, errorInfo) {
  this.setState({error:error.toString(),info:errorInfo.componentStack.split('\n')})
 }

 render() {
  if (this.state.hasError)
   return <div className='overlay' style={{top:0}}>
    <article className='error'>
     <CloseButton key='error_close' onClick={() => this.setState({hasError: false, error: undefined, info:[]})} />
     <h1>UI Error</h1>
     <InfoColumns key='error_ic'>
      <TextLine key='error_type' id='type' text={this.state.error} />
      <label htmlFor='info' className='info'>Info:</label><div id='info'>{this.state.info.map((row,idx) => <p key={'error_line'+idx}>{row}</p>)}</div>
     </InfoColumns>
    </article>
   </div>
  else
   return this.props.children;
 }
}
// ************************* Portal  ****************************
//
class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { menu:[], navigation:<NavBar key='portal_navigation_empty' /> }
 }

 componentDidMount() {
  this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation});
  rest_call('api/portal/menu',{id:this.context.cookie.id}).then(result => {
    this.setState(result);
    result.start && this.changeContent(result.menu[result.start]);
    document.title = result.title;
   })
 }

 loadNavigation = (navbar) => this.setState({navigation:navbar})

 changeContent = (panel) => {
  // Native RIMS or something else?
  if (panel.hasOwnProperty('module')) {
   if (this.state.content && (this.state.content.key === `${panel.module}_${panel.function}`))
    return
   try {
    import("./"+panel.module+".jsx").then(lib => {
     var Elem = lib[panel.function];
     this.setState({navigation:<NavBar key='portal_navigation_empty' />,content:<Elem key={panel.module + '_' + panel.function} {...panel.args} />});
    })
   } catch(err) {
    console.error("Mapper error: "+panel);
    alert(err);
   }
  } else
   this.setState({navigation:<NavBar key='portal_navigation_empty' />,content:panel})
 }

 render() {
  let buttons = []
  for (let [key, panel] of Object.entries(this.state.menu)){
   if (panel.type === 'module')
    buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => this.changeContent(panel)} />)
   else if (panel.type === 'tab')
    buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => window.open(panel.tab,'_blank')} />)
   else if (panel.type === 'frame')
    buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => this.changeContent(<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>)} />)
  }
  return (
   <React.Fragment key='portal'>
    <Theme key='portal_theme' theme={this.context.cookie.theme} />
    <Header key='portal_header'>
     <FontAwesomeMenuButton key='mb_btn_logout' style={{float:'right', backgroundColor:'var(--high-color)'}} onClick={() => { this.context.clearCookie()}} title='Log out' type='fas fa-sign-out-alt' />
     <FontAwesomeMenuButton key='mb_btn_system_Main' style={{float:'right'}} onClick={() => {this.changeContent({module:'system',function:'Main'})}} title='System information' type='fas fa-cogs' />
     <FontAwesomeMenuButton key='mb_btn_user_User' style={{float:'right'}} onClick={() => {this.changeContent({module:'user',function:'User', args:{id:this.context.cookie.id}})}} title='User' type='fas fa-user' />
     {buttons}
    </Header>
    {this.state.navigation}
    <ErrorBoundary key='portal_error'>
     <main>{this.state.content}</main>
    </ErrorBoundary>
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
     <h1>{this.state.message}</h1>
     <InfoColumns className='left'>
      <TextInput key='username' id='username' onChange={this.onChange} />
      <PasswordInput key='password' id='password' onChange={this.onChange} />
     </InfoColumns>
     <FontAwesomeMenuButton key='login_btn_login' onClick={this.handleSubmit} title='Login' type='fas fa-sign-in-alt' />
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

ReactDOM.render(<RIMS />, document.getElementById('root'))
