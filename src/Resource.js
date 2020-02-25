import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, read_cookie, library } from './infra/Functions.js';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 componentDidMount(){ this.compileNavItems() }

 content = (elem) => { this.setState({content:elem}) }

 compileNavItems = () => {
  this.props.loadNavigation([{title:'Resources', type:'dropdown', className:'right', items:[
   {title:'Menuitems', onClick:() => { this.content(<View key='menuitem' type='menuitem'/>)}},
   {title:'Tools',     onClick:() => { this.content(<View key='tool' type='tool'/>)}}
   ]}
  ])
 }

 render() { return <Fragment key='resource_main'>{this.state.content}</Fragment> }
}

// ************** Main **************
//
class View extends Component{

 componentDidMount(){
  rest_call(rest_base + 'api/portal/resources',{type:this.props.type})
   .then((result) => { this.setState(result) })
 }

 render(){
  if (this.state === null)
   return <Spinner />
  else { 

   return (<div>View: {JSON.stringify(this.props)}</div>)
  }
 }
}
