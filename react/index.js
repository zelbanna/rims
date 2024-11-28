import React, { useEffect, Component } from 'react';
import { createRoot } from 'react-dom/client';
import { auth_call } from './infra/Functions.js';
import { Portal, Login, RimsContext } from './infra/UI.jsx';
import * as serviceWorker from './serviceWorker';

//import '@fortawesome/fontawesome-free/js/fontawesome'
//import '@fortawesome/fontawesome-free/js/solid'
import '@fortawesome/fontawesome-free/css/fontawesome.css'
import '@fortawesome/fontawesome-free/css/solid.css'

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

// ************************** App *************************

class RIMS extends Component {
 constructor(props) {
  super(props);

  this.state = {token:null, theme:undefined}
  const cookies = document.cookie.split("; ");
  for(let i=0;i < cookies.length;i++) {
   let c = cookies[i];
   if (c.indexOf("rims=") === 0)
    this.state.token = c.substring(5,c.length);
   if (c.indexOf("rims_theme=") === 0)
    this.state.theme = c.substring(11,c.length);
  }
  this.provider = {}
 }

 componentDidMount(){
  if(this.state.token){
   auth_call({verify:this.state.token}).then(result => {
    if(result.status === 'OK')
     this.setState({node:result.node,token:result.token,id:result.id,expires:result.expires,class:result.class});
    else
     this.setState({token:null})
   })
  }
 }

 changeTheme = (theme) => {
  document.cookie = "rims_theme="+ theme + "; Path=/; expires=" + this.state.expires + "; Path=/";
  this.setState({theme:theme})
 }

 logOut = () => {
  auth_call({destroy:this.state.token,id:this.state.id})
  document.cookie = "rims=; Path=/; SameSite=Strict; expires=Thu, 01 Jan 1970 00:00:00 UTC";
  document.cookie = "rims_theme=; Path=/; SameSite=Strict; expires=Thu, 01 Jan 1970 00:00:00 UTC";
  document.documentElement.removeAttribute("style");
  this.setState({token:null})
 }

 logIn = (settings) => {
  document.cookie = "rims=" + settings.token + "; expires=" + settings.expires + "; Path=/; SameSite=Strict";
  document.cookie = "rims_theme="+ settings.theme + "; expires=" + settings.expires + "; Path=/; SameSite=Strict";
  this.setState(settings)
 }

 providerMounting = (options) => {
  Object.assign(this.provider,options);
  this.forceUpdate();
 }

 render(){
  return <RimsContext.Provider value={{settings:this.state,logIn:this.logIn,logOut:this.logOut,changeTheme:this.changeTheme,...this.provider}}>
    {(this.state.token === null) ?<Login /> : <Portal providerMounting={this.providerMounting} />}
   </RimsContext.Provider>
 }
}

// New root compatible renderer
function RenderRIMS() {
 useEffect(() => {
  console.log("Rendered RIMS 8.x");
 });

 return <RIMS tab="home" />
}

const container = document.getElementById('root')
const root = createRoot(container);
root.render(<RenderRIMS />);
