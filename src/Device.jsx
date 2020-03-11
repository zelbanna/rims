import React, { Component } from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner, StateMap, InfoCol2 } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';

import { List as ReservationList } from './Reservation.jsx';
import { List as LocationList } from './Location.jsx';
import { List as ServerList } from './Server.jsx';
import { NetworkList as IPAMNetworkList } from './IPAM.jsx';
import { DomainList as DNSDomainList } from './DNS.jsx';
import { List as VisualizeList } from './Visualize.jsx';
import { List as RackList, Inventory as RackInventory } from './Rack.jsx';

/*

def main(aWeb):
def logs(aWeb):
def list(aWeb):
def oui_search(aWeb):
def oui_list(aWeb):
def search(aWeb):
def info(aWeb):
def extended(aWeb):
def control(aWeb):
def delete(aWeb):
def type_list(aWeb):
def model_list(aWeb):
def model_info(aWeb):
def logs(aWeb):
def to_console(aWeb):
def conf_gen(aWeb):
def function(aWeb):
def new(aWeb):
def discover(aWeb):
def interface_list(aWeb):
def interface_lldp(aWeb):
def interface_info(aWeb):
def interface_ipam(aWeb):
def interface_connect(aWeb):
def connection_info(aWeb):

*/


export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state = {rack_name:null, rack_id:null,  pduinfo:[], coninfo:[]}
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
    {title:'List', onClick:() => this.changeMain(<List key='device_list' />)},
    {title:'Search', onClick:() => this.changeMain(<Search key='device_search' />)},
    {title:'Types', onClick:() => this.changeMain(<TypeList key='device_type_list' />)},
    {title:'Models', onClick:() => this.changeMain(<ModelList key='device_model_list' />)}
   ]},
   {title:'Reservations', className:'right', onClick:() => this.changeMain(<ReservationList key='reservation_list' />)},
   {title:'Locations', className:'right', onClick:() => this.changeMain(<LocationList key='location_list' />)},
   {title:'IPAM', type:'dropdown',  className:'right', items:[
    {title:'Servers', onClick:() => this.changeMain(<ServerList key='server_list' type='DHCP' />)},
    {title:'Networks', onClick:() => this.changeMain(<IPAMNetworkList key='ipam_network_list' />)}
   ]},
   {title:'DNS', type:'dropdown',  className:'right', items:[
    {title:'Servers', onClick:() => this.changeMain(<ServerList key='server_list' type='DNS' />)},
    {title:'Domains', onClick:() => this.changeMain(<DNSDomainList key='dns_domain_list' />)}
   ]},
   {title:'Racks', className:'right', onClick:() => this.changeMain(<RackList key='rack_list' />)},
   {title:'Maps',  onClick:() => this.changeMain(<VisualizeList key='visualize_list' />)},
   {title:'OUI', type:'dropdown', items:[
    {title:'Search',  onClick:() => this.changeMain(<OUISearch key='oui_search' />)},
    {title:'List',  onClick:() => this.changeMain(<OUIList key='oui_list' />)}
   ]},,
   { onClick:() => this.setState({content:null}), className:'reload' }
  ]
  if (this.state.pduinfo.length > 0)
   navitems.push({title:'PDUs', type:'dropdown', items:this.state.pduinfo})
  if (this.state.coninfo.length > 0)
   navitems.push({title:'Consoles', type:'dropdown', items:this.state.coninfo})
  if (this.state.rack_id)
   navitems.push({title:this.state.rack, onClick:() => this.changeMain(<RackInventory key='rack_inventory' id={this.state.rack_id} />)})
  this.props.loadNavigation(navitems)
 }

}

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

// ************** TODO**************
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

class TypeList extends ListBase {

 render() {
  return (<div>TypeList (TODO)</div>);
 }
}

class ModelList extends ListBase {

 render() {
  return (<div>ModelList (TODO)</div>);
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
