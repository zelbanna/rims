import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './infra/system.css';
import { auth_call, rest_call, RimsContext } from './infra/Functions.js';
import { InfoColumns, ErrorBoundary, Theme } from './infra/UI.jsx';
import { TextInput, PasswordInput } from './infra/Inputs.jsx';
import { NavBar } from './infra/Navigation.jsx';
import { Header, MenuButton, MenuSeparator } from './infra/Header.jsx';
import * as serviceWorker from './serviceWorker';

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

// ************************* Portal  ****************************
//
class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { menu:[], navigation:<NavBar key='portal_navigation_empty' />}
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
   try {
    import("./"+panel.module+".jsx").then(lib => {
     var Elem = lib[panel.function];
     this.setState({navigation:<NavBar key='portal_navigation_empty' />,content:<Elem key={panel.module + '_' + panel.function} {...panel.args} />,height:0});
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
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => this.changeContent(panel)} />)
   else if (panel.type === 'tab')
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => window.open(panel.tab,'_blank')} />)
   else if (panel.type === 'frame')
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => this.changeContent(<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>)} />)
  }
  buttons.push(<MenuSeparator key='hs_1' />,
   <MenuButton key='hb_user_info' title='User' onClick={() => this.changeContent({module:'user',function:'User', args:{id:this.context.cookie.id}})} />,
   <MenuButton key='hb_system' title='System' onClick={() => this.changeContent({module:'system',function:'Main'})} />)

  return (
   <React.Fragment key='portal'>
    <Theme key='portal_theme' theme={this.context.cookie.theme} />
    <Header key='portal_header' title={this.state.title} logOut={() => this.context.clearCookie()}>
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
     <button className='login'  onClick={this.handleSubmit} title='Login'><i className='fas fa-sign-in-alt' /></button>
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

 componentDidMount(){
  if(this.state.token){
   auth_call({verify:this.state.token}).then(result => {
    if(result.status !== 'OK')
     this.setState({token:null})
    else
     console.log('Token verified')
   })
  }
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
