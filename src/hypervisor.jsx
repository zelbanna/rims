import React, { Fragment, Component } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { StateMap, RimsContext, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { InfoButton, SyncButton, UiButton } from './infra/Buttons.jsx';
import { NavBar, NavButton } from './infra/Navigation.js';

import { Logs as DeviceLogs } from './device.jsx';

// ************** Main **************
//
export class Main extends Component {
 componentDidMount(){
  this.setState(<List key={'hypervisor_list_'+rnd()} />)
  this.context.loadNavigation(<NavBar key='hypervisor_navbar_empty' />)
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}
Main.contextType = RimsContext;

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/device/list',{field:'base',search:'hypervisor',extra:['type','functions','url'],sort:'hostname'}).then(result => this.setState(result))
 }

 listItem = (row) => {
  const up =  (row.state === 'up');
  return [row.hostname,row.type_name,<StateMap state={row.state} />,<Fragment key={'hypervisor_buttons_'+row.id}>
   {up && row.type_functions === 'manage' && <InfoButton key={'hypervisor_info_'+row.id} onClick={() => this.changeContent(<Manage key={'hypervisor_manage_'+row.id} id={row.id} />)} />}
   {up && row.url && row.url.length > 0 && <UiButton key={'hypervisor_ui_'+row.id} onClick={() => window.open(row.url,'_blank') } />}
   </Fragment>]
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <Fragment key='hyp_fragment'>
   <ContentList key='hyp_cl' header='Hypervisor' thead={['Hostname','Type','','']} trows={this.state.data} listItem={this.listItem}>
    <SyncButton key='hyp_btn_sync' onClick={() => this.changeContent(<Sync />) } />
   </ContentList>
   <ContentData key='hyp_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Sync **************
//
class Sync extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/device/vm_mapping').then(result => {
    let entries = [];
    ["existing","inventory","discovered","database"].forEach(type => {
     if (result.hasOwnProperty(type))
      result[type].forEach(entry => { entry.type = type; entries.push(entry); })
    })
    this.setState({data:entries})
   })
 }

 listItem = (row) => [row.type,row.host_id,row.device_id,row.vm,row.device_uuid,row.config]

 render(){
  return <ContentReport key='hyp_cr' header='VM Mapping' thead={['Status','Host','Device','VM Name','Device UUID','Config']} trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** Manage **************
//
export class Manage extends Component {

 componentDidMount(){
  rest_call('api/device/management',{id:this.props.id})
   .then((result) => {
    //if (result.data.hasOwnProperty(url) && result.data.url.length > 0)
    // navitems.push({title:)
    this.context.loadNavigation(<NavBar key='hypervisor_navbar'><NavButton key='hyp_nav_logs' title='Logs' onClick={() => this.changeContent(<DeviceLogs id={this.props.id} />)} /></NavBar>);
    this.setState(result)
    })
 }

 render(){
  return <div>Manage</div>
 }
}
Manage.contextType = RimsContext;

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
