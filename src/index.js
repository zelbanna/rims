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

  this.state = this.readCookie();
  this.provider = {}
 }

 componentDidMount(){
  if(this.state.token){
   auth_call({verify:this.state.token}).then(result => {
    if(result.status !== 'OK')
     this.setState({token:null})
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
