import React, { Component, Fragment } from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner, StateMap, InfoCol2, RimsContext } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton, TextButton } from './infra/Buttons.jsx';

import { List as ReservationList } from './Reservation.jsx';
import { List as LocationList } from './Location.jsx';
import { List as ServerList } from './Server.jsx';
import { NetworkList as IPAMNetworkList } from './IPAM.jsx';
import { DomainList as DNSDomainList } from './DNS.jsx';
import { List as VisualizeList } from './Visualize.jsx';
import { List as RackList, Inventory as RackInventory, Infra as RackInfra } from './Rack.jsx';

/*

def search(aWeb):
def list(aWeb):
def delete(aWeb):

def oui_search(aWeb):
def oui_list(aWeb):

def info(aWeb):
def extended(aWeb):
def control(aWeb):
def function(aWeb):

def model_info(aWeb):

def logs(aWeb):
def to_console(aWeb):
def conf_gen(aWeb):

def new(aWeb):
def discover(aWeb):

def interface_list(aWeb):
def interface_lldp(aWeb):
def interface_info(aWeb):
def interface_ipam(aWeb):
def interface_connect(aWeb):
def connection_info(aWeb):

*/

// **************** Main ****************
//
export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state = {pduinfo:[], coninfo:[], rack_name:'N/A'}
 }

 componentDidMount(){
/*
 if aWeb['rack']:
  data = aWeb.rest_call("rack/inventory",{'id':aWeb['rack']})
  for type in ['pdu','console']:
   if len(data[type]) > 0:
    aWeb.wr("<LI CLASS='dropdown'><A>%s</A><DIV CLASS='dropdown-content'>"%(type.title()))
    for row in data[type]:
     aWeb.wr("<A CLASS=z-op DIV=div_content_left SPIN=true URL='%s_inventory?id=%s'>%s</A>"%(row['type'],row['id'],row['hostname']))
    aWeb.wr("</DIV></LI>")
  if data.get('name'):
   aWeb.wr("<LI><A CLASS='z-op' DIV=div_content_right  URL='rack_inventory?rack=%s'>'%s'</A></LI>"%(aWeb['rack'],data['name']))

*/
  this.compileNavItems();
 }

 compileNavItems = () => {
  const navitems = [
   {title:'Devices', type:'dropdown', items:[
    {title:'List', onClick:() => this.changeContent(<List key='device_list' />)},
    {title:'Search', onClick:() => this.changeContent(<Search key='device_search' />)},
    {title:'Types', onClick:() => this.changeContent(<TypeList key='device_type_list' changeSelf={this.changeContent} />)},
    {title:'Models', onClick:() => this.changeContent(<ModelList key='device_model_list' />)}
   ]},
   {title:'Reservations', className:'right', onClick:() => this.changeContent(<ReservationList key='reservation_list' />)},
   {title:'Locations', className:'right', onClick:() => this.changeContent(<LocationList key='location_list' />)},
   {title:'IPAM', type:'dropdown',  className:'right', items:[
    {title:'Servers', onClick:() => this.changeContent(<ServerList key='ipam_server_list' type='DHCP' />)},
    {title:'Networks', onClick:() => this.changeContent(<IPAMNetworkList key='ipam_network_list' />)}
   ]},
   {title:'DNS', type:'dropdown',  className:'right', items:[
    {title:'Servers', onClick:() => this.changeContent(<ServerList key='dns_server_list' type='DNS' />)},
    {title:'Domains', onClick:() => this.changeContent(<DNSDomainList key='dns_domain_list' />)}
   ]},
   {title:'Rack', type:'dropdown', className:'right', items:[
    {title:'Racks',    onClick:() => this.changeContent(<RackList key='rack_list' />)},
    {title:'PDUs',     onClick:() => this.changeContent(<RackInfra key='pdu_list' type='pdu' />)},
    {title:'Consoles', onClick:() => this.changeContent(<RackInfra key='console_list' type='console' />)}
   ]},
   {title:'Maps',  onClick:() => this.changeContent(<VisualizeList key='visualize_list' />)},
   {title:'OUI', type:'dropdown', items:[
    {title:'Search',  onClick:() => this.changeContent(<OUISearch key='oui_search' />)},
    {title:'List',  onClick:() => this.changeContent(<OUIList key='oui_list' />)}
   ]}
  ]
  if (this.state.pduinfo.length > 0)
   navitems.push({title:'PDUs', type:'dropdown', items:this.state.pduinfo})
  if (this.state.coninfo.length > 0)
   navitems.push({title:'Consoles', type:'dropdown', items:this.state.coninfo})
  if (this.props.rack_id)
   navitems.push({title:this.state.rack_name, onClick:() => this.changeContent(<RackInventory key='rack_inventory' id={this.props.rack_id} />)})
  navitems.push({ onClick:() => this.setState({content:null}), className:'reload' })
  this.context.loadNavigation(navitems)
 }

}
Main.contextType = RimsContext;

// ************** Report **************
//
export class Report extends ReportBase {
 constructor(props){
  super(props)
  this.header = 'Devices'
  this.thead = ['ID','Hostname','Class','IP','MAC','OUI','Model','OID','Serial','State']
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/list', { extra:['system','type','mac','oui','class']})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => [row.id,row.hostname,row.class,row.ip,row.mac,row.oui,row.model,row.oid,row.serial,StateMap({state:row.state})]
}

// ************** Type List **************
//
class TypeList extends ListBase {
 constructor(props){
  super(props)
  this.header = 'Type List'
  this.thead = ['Class','Name','Icon'];
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/type_list')
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => [row.base,<TextButton text={row.name} onClick={() => this.props.changeSelf(<List key='device_list' field='type' search={row.name} />)} />,row.icon]
}

// ************** Model List **************
//
class ModelList extends ListBase {
 constructor(props){
  super(props)
  this.header = 'Model List'
  this.thead = ['ID',' Model','Type',''];
  this.buttons = [
   <InfoButton key='model_reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='model_sync'   type='sync' onClick={() => this.syncModels() } title='Resync models' />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/model_list')
   .then((result) => { this.setState({...result,result:'OK'}) })
 }

 syncModels = () => {
  rest_call(rest_base + 'api/device/model_list',{op:'sync'})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => [row.id,row.name,row.type,<Fragment key={'ml_' + row.id}>
  <InfoButton type='info' onClick={() => this.changeContent(<ModelInfo key={'model_info_'+row.id} id={row.id} />)} />
  <InfoButton type='trash' onClick={() => this.deleteList('api/device/model_delete',row.id,'Really delete model?') } />
 </Fragment>]
}

// ************** Model Info **************
//
export class ModelInfo extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/device/model_info',{id:this.props.id})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => [
    {tag:'span', id:'name', text:'Name', value:this.state.data.name},
    {tag:'span', id:'type', text:'Type', value:this.state.extra.type},
    {tag:'input', type:'text', id:'defaults_file', text:'Defaults File', value:this.state.data.defaults_file},
    {tag:'input', type:'text', id:'image_file', text:'Image File', value:this.state.data.image_file}
   ]

 render() {
  if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Device Model</h1>
     <InfoCol2 key='device_model_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <label htmlFor='parameters'>Parameters:</label>
     <textarea id='parameters' name='parameters' className='info' onChange={this.changeHandler} value={this.state.data.parameters} />
     <InfoButton key='device_model_save' type='save' onClick={() => this.updateInfo('api/device/model_info')} />
    </article>
   );
  }
 }
}

// ************** TODO **************
//
export class Logs extends Component {

 render() {
  return (<div>Device Logs (TODO)</div>);
 }
}

class List extends ListBase {

 render() {
  return (<div>Device List (TODO)</div>);
 }
}

class Search extends Component {

 render() {
  return (<div>Device Search (TODO)</div>);
 }
}

class OUISearch extends Component {

 render() {
  return (<div>OUI Search (TODO)</div>);
 }
}

class OUIList extends Component {

 render() {
  return (<div>OUI List (TODO)</div>);
 }
}

export class Info extends Component {

 render() {
  return (<div>Device Info (TODO)</div>);
 }
}
export class New extends Component {

 render() {
  return (<div>Device New (TODO)</div>);
 }
}
