import React from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
import { MainBase } from './infra/Base.js'
import { MenuButton } from './infra/Buttons.js'
import Library from './infra/Mapper.js'

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends MainBase {

 componentDidMount(){
  this.props.loadNavigation([{ onClick:() => { this.componentDidMount() }, className:'reload right'}])
  rest_call(rest_base + 'api/portal/resources',{type:'tool'})
   .then((result) => {
   let buttons = []
   for (let [key, panel] of Object.entries(result.data)){
    let click = null
    if (panel.type === 'module')
     click = () => this.changeMain(panel)
    else if (panel.type === 'tab')
     click = () => window.open(panel.tab,'_blank')
    else if (panel.type === 'frame')
     click = () => this.setState({content:<iframe id='resource_frame' name='resource_frame' title={key} src={panel.frame}></iframe>})
    panel.title = key
    buttons.push(<MenuButton key={'mb_'+key} {...panel} onClick={click} />)
   }
   this.setState({content:<div className='centered'>{buttons}</div>})
  })
 }

 changeMain = (panel) => {
  if ((this.state.content !== null) && (this.state.content.key === `${panel.module}_${panel.function}`))
   return
  try {
   const Elem = Library[panel.module][panel.function]
   this.setState({content:<Elem key={panel.module + '_' + panel.function} {...panel.args} loadNavigation={this.props.loadNavigation} />})
  } catch(err) {
   console.error("Mapper error: "+panel);
   alert(err);
  }
 }

}
