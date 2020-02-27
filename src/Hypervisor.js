import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { StateMap } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase } from './infra/Base.js';
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

class Sync extends ReportBase{

 componentDidMount(){
  rest_call(rest_base + 'api/device/vm_mapping')
   .then((result) => {
    let entries = []
    for (let [type,rows] of Object.entries(result)){
     rows.forEach(row => {
      row.type = type;
      entries.push(row)
     })
    }
    this.setState(entries)
   })
 }

 listItem = (row) => [row.type,row.host_id,row.device_id,row.device_uuid,row.config]

}

/*
def sync(aWeb):
 res = aWeb.rest_call("device/vm_mapping")
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Status</DIV><DIV>Host</DIV><DIV>Device</DIV><DIV>VM Name</DIV><DIV>Device UUID</DIV><DIV>Config</DIV></DIV><DIV CLASS=tbody>")
 for type in ['existing','inventory','discovered','database']:
  for row in res.get(type):
   aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(type.upper(),row['host_id'],row.get('device_id','-'),row['vm'],row['device_uuid'],row['config']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
*/
