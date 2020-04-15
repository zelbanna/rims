import React, { Fragment, Component } from 'react';
import { rest_call, RimsContext } from './infra/Functions.js';
import { NavBar, NavDropDown, NavDropButton } from './infra/Navigation.jsx';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/portal/resources',{type:'tool'}).then(result => {
   Object.assign(this.state,result);
   this.compileNavItems();
  })
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props){
   this.compileNavItems();
  }
 }

 compileNavItems = () => {
  let buttons = []
  for (let [key, panel] of Object.entries(this.state.data)){
   if (panel.type === 'module')
    buttons.push(<NavDropButton key={'mb_'+key} title={key} onClick={() => this.context.changeMain(panel)} />)
   else if (panel.type === 'tab')
    buttons.push(<NavDropButton key={'mb_'+key} title={key} onClick={() => window.open(panel.tab,'_blank')} />)
   else if (panel.type === 'frame')
    buttons.push(<NavDropButton key={'mb_'+key} title={key} onClick={() => this.context.changeMain(<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>)} />)
  }
  this.context.loadNavigation(<NavBar key='resource_navbar'><NavDropDown key='resources' title='Resources'>{buttons}</NavDropDown></NavBar>)
 }

 render(){
  return  <Fragment />
 }
}
Main.contextType = RimsContext;
