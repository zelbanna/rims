import React from 'react';
import { rest_call } from './infra/Functions.js';
import { MainBase } from './infra/Base.jsx';
import { MenuButton } from './infra/Buttons.jsx';
import { RimsContext } from './infra/Generic.js';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends MainBase {

 componentDidMount(){
  rest_call('api/portal/resources',{type:'tool'})
   .then((result) => {
   let buttons = []
   for (let [key, panel] of Object.entries(result.data)){
    let click = null
    if (panel.type === 'module')
     click = () => this.context.changeMain(panel)
    else if (panel.type === 'tab')
     click = () => window.open(panel.tab,'_blank')
    else if (panel.type === 'frame')
     click = () => this.setState({content:<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>})
    panel.title = key
    buttons.push(<MenuButton key={'mb_'+key} {...panel} onClick={click} />)
   }
   this.setState({content:<div className='flexdiv centered'>{buttons}</div>})
  })
 }
}
Main.contextType = RimsContext;
