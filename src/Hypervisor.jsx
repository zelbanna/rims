import React, { Fragment } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { StateMap } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';

import { Logs as DeviceLogs } from './Device.jsx';

// ************** Main **************
//

export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state.content = <List key={'hypervisor_list_'+rnd()} changeSelf={this.changeMain} loadNavigation={this.props.loadNavigation} />
  this.props.loadNavigation([{ onClick:() => this.changeMain(<List key={'hypervisor_list_'+rnd()} changeSelf={this.changeMain} />), className:'reload right'}])
 }
}

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props)
  this.thead = ['Hostname','Type','','']
  this.header = 'Hypervisor'
  this.buttons = [<InfoButton key='hypervisor_sync' type='sync' onClick={() => this.changeContent(<Sync />) } />]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/list',{field:'base',search:'hypervisor',extra:['type','functions','url'],sort:'hostname'})
   .then((result) => this.setState(result) )
 }

 listItem = (row) => {
  let buttons = []
  if (row.state === 'up')
   if (row.type_functions === 'manage')
    buttons.push(<InfoButton key={'hypervisor_info_'+row.id} type='info' onClick={() => this.props.changeSelf(<Manage key={'hypervisor_manage_'+row.id} loadNavigation={this.props.loadNavigation} id={row.id} />) } />)
   if (row.url && row.url.length > 0)
    buttons.push(<InfoButton key={'hypervisor_ui_'+row.id} type='ui' onClick={() => window.open(row.url,'_blank') } />)
  return [row.hostname,row.type_name,<StateMap key={'hypervisor_state_'+row.id} state={row.state} />,<Fragment key={'hypervisor_buttons_'+row.id}>{buttons}</Fragment>]
 }

}

// ************** Sync **************
//

class Sync extends ReportBase{
 constructor(props){
  super(props)
  this.thead = ['Status','Host','Device','VM Name','Device UUID','Config']
  this.header= 'VM Mapping'
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/vm_mapping')
   .then((result) => {
    let entries = [];
    ["existing","inventory","discovered","database"].forEach(type => {
     if (result.hasOwnProperty(type))
      result[type].forEach(entry => {
       entry.type = type
       entries.push(entry)
      })
    })
    this.setState({data:entries})
   })
 }

 listItem = (row) => [row.type,row.host_id,row.device_id,row.vm,row.device_uuid,row.config]

}

// ************** Manage **************
//
class Manage extends ListBase {

 componentDidMount(){
  rest_call(rest_base + 'api/device/management',{id:this.props.id})
   .then((result) => {
    var navitems = [{title:'Logs', onClick:() => this.changeContent(<DeviceLogs id={this.props.id} />)}];
    //if (result.data.hasOwnProperty(url) && result.data.url.length > 0)
    // navitems.push({title:)
    this.props.loadNavigation(navitems);
    this.setState(result)
    })
 }

 render(){
  return <div>Manage</div>
 }
}

/*
def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device/management",{'id':id})
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_right  URL='device_logs?id=%s'>Logs</A></LI>"%id)
 if data['data']['url']:
  aWeb.wr("<LI><A CLASS=z-op HREF='%s'     target=_blank>UI</A></LI>"%(data['data']['url']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='esxi_manage?id=%s'></A></LI>"%(id))
 aWeb.wr("<LI CLASS='right navinfo'><A>{}</A></LI>".format(data['data']['hostname']))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 list(aWeb)
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
*/
