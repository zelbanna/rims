import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { auth_call } from './infra/Functions.js';
import { Portal, Login, RimsContext } from './infra/UI.jsx';
import * as serviceWorker from './serviceWorker';

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
     this.setState({node:result.node,token:result.token,id:result.id,expires:result.expires});
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
  document.cookie = "rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  document.cookie = "rims_theme=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
  document.documentElement.removeAttribute("style");
  this.setState({token:null})
 }

 logIn = (settings) => {
  document.cookie = "rims=" + settings.token + "; expires=" + settings.expires + "; Path=/";
  document.cookie = "rims_theme="+ settings.theme + "; Path=/; expires=" + settings.expires + "; Path=/";
  this.setState(settings)
 }

 providerMounting = (options) => {
  Object.assign(this.provider,options);
  this.forceUpdate();
 }

 render(){
  return (
   <RimsContext.Provider value={{settings:this.state,logIn:this.logIn,logOut:this.logOut,changeTheme:this.changeTheme,...this.provider}}>
    {(this.state.token === null) ?<Login /> : <Portal providerMounting={this.providerMounting} />}
   </RimsContext.Provider>
  )
 }
}
ReactDOM.render(<RIMS />, document.getElementById('root'))
