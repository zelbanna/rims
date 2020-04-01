import React, { Component } from 'react';
import { rest_call } from './infra/Functions.js';
import { MenuButton } from './infra/Buttons.jsx';
import { RimsContext } from './infra/UI.jsx';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 changeContent = (elem) => this.setState(elem)

 componentDidMount(){
  rest_call('api/portal/resources',{type:'tool'}).then((result) => {
   let buttons = []
   for (let [key, panel] of Object.entries(result.data)){
    if (panel.type === 'module')
     buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => this.context.changeMain(panel)} />)
    else if (panel.type === 'tab')
     buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => window.open(panel.tab,'_blank')} />)
   else if (panel.type === 'frame')
    buttons.push(<MenuButton key={'mb_'+key} title={key} {...panel} onClick={() => this.context.changeMain(<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>)} />)
   }
   this.setState({content:buttons})
  })
 }

 render(){
  return  <div className='flexdiv centered'>{this.state.content}</div>
 }
}
Main.contextType = RimsContext;
