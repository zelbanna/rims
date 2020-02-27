import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { MainBase, ListBase, StateMap } from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.js';

// ************** Main **************
//

export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state.content = <List key={'hypervisor_list_'+rnd()} changeMain={this.changeMain} />
  this.props.loadNavigation([{ onClick:() => { this.changeMain(<List key={'hypervisor_list_'+rnd()} changeMain={this.changeMain} />) }, className:'reload right'}])
 }
}

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props)
  this.thead = ['Hostname','Type','','']
  this.header = 'Hypervisor'
  this.buttons = [<InfoButton key='hypervisor_sync' type='sync' onClick={() => { this.changeList(<Sync />) }} />]

 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/list',{field:'base',search:'hypervisor',extra:['type','functions','url'],sort:'hostname'})
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => {
  let buttons = []
  if (row.state === 'up')
   buttons.push(<InfoButton key={'hypervisor_info_'+row.id} type='info' onClick={() => { this.changeList(<Sync key={'hypervisor_info_'+row.id} id={row.id} />)}} />)
  if (row.url && row.url.length > 0)
   buttons.push(<InfoButton key={'hypervisor_info_'+row.id} type='info' onClick={() => { window.open(row.url,'_blank') }} />)
  return [row.hostname,row.type_name,<StateMap key='hypervisor_state' state={row.state} />,<Fragment key={'hypervisor_buttons_'+row.id}>{buttons}</Fragment>]
 }

}

// ************** Sync **************
//

class Sync extends Component{
 render(){
  return(<div>Sync</div>)
 }
}

