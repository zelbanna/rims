import React, { Fragment, Component } from 'react';
import { post_call } from './infra/Functions.js';
import { NavBar, NavDropDown, NavDropButton } from './infra/Navigation.jsx';
import { RimsContext } from './infra/UI.jsx';
import styles from './infra/ui.module.css';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/portal/resources',{type:'resource'}).then(result => {
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
    buttons.push(<NavDropButton key={'mb_'+key} title={key} onClick={() => this.context.changeMain(<iframe className={styles.frame} title={key} src={panel.frame} />)} />)
   else
    console.log("Unknown panel type:"+JSON.stringify(panel))
  }
  this.context.loadNavigation(<NavBar key='resource_navbar'><NavDropDown key='resources' title='Resources'>{buttons}</NavDropDown></NavBar>)
 }

 render(){
  return  <Fragment />
 }
}
Main.contextType = RimsContext;
