import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner, TableRow } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase } from './infra/Base.jsx';
import { InfoButton, TextButton } from './infra/Buttons.jsx';

import { LogShow, List as NodeList } from './Node.jsx';
import { List as ServerList } from './Server.jsx';
import { List as UserList } from './User.jsx';
import { Report as ActivityReport } from './Activity.jsx';
import { Report as ReservationReport } from './Reservation.jsx';
import { Report as DeviceReport } from './Device.jsx';
import { Report as InventoryReport } from './Inventory.jsx';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state = {cookie:read_cookie('rims'), navinfo:[], navitems:[], logs:[], services:[] }
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/service_list')
   .then((result) => {
    Object.assign(this.state,result)
    this.compileNavItems()
   })
  rest_call(rest_base + 'api/master/inventory',{node:this.state.cookie.node, user_id:this.state.cookie.id})
   .then((result) => {
    Object.assign(this.state,result)
    this.compileNavItems()
   })
 }

 compileNavItems = () => {
  let navitems = [];
  let reports = [];
   if (this.state.cookie.node === 'master') {
    navitems.push({title:'Nodes',  onClick:() => this.changeMain(<NodeList key='node_list' />) })
    navitems.push({title:'Servers', onClick:() => this.changeMain(<ServerList key='server_list' />) })
    navitems.push({title:'ERD',    onClick:() => window.open('infra/erd.pdf','_blank') })
    navitems.push({title:'Users',  onClick:() => this.changeMain(<UserList key='user_list' />) })
    navitems.push({title:'Controls',  onClick:() => this.changeMain(<Controls  />) })
    reports.push({title:'Activities',  onClick:() => this.changeMain(<ActivityReport key='activity_report' />) })
    reports.push({title:'Reservations',  onClick:() => this.changeMain(<ReservationReport key='reservation_report' />) })
    reports.push({title:'Devices',  onClick:() => this.changeMain(<DeviceReport key='device_report' />) })
    reports.push({title:'Inventory',  onClick:() => this.changeMain(<InventoryReport key='inventory_report' />) })
   }
   reports.push({title:'Tasks',   onClick:() => this.changeMain(<TaskReport key='task_report' />) })
   reports.push({title:'System',  onClick:() => this.changeMain(<Report key='system_report' />) })
   navitems.push({title:'Logs',   type:'dropdown', items:this.state.logs.map(row => ({title:row, onClick:() => this.changeMain( <LogShow key={row.name} node={row} /> )})) })
   navitems.push({title:'Report', type:'dropdown', items:reports})
   navitems.push({title:'REST',  onClick:() => this.changeMain(<RestList key='rest_list' />) })
   if (this.state.services.length > 0)
    navitems.push({title:'Services', type:'dropdown', items:this.state.services.map(row => ({title:row.name, onClick:() => this.changeMain( <ServiceInfo key={row.name} {...row} /> )})) })
   navitems.push({ onClick:() => this.setState({content:null}), className:'reload' })
   this.state.navinfo.forEach(row => navitems.push({title:row, className:'right navinfo'}))
   this.props.loadNavigation(navitems)
 }

}

// ************** Report **************
//
export class Report extends ReportBase{
 constructor(props){
  super(props)
  this.header = 'System Report'
  this.thead = ['Key','Value']
 }

 componentDidMount(){
  rest_call(rest_base + 'system/report')
   .then(result => this.setState({data:Object.keys(result).sort((a,b) => a.localeCompare(b)).map(key => ({info:key,value:result[key]})) }))
 }

 listItem = (row) => [row.info,row.value]

}

// ************** TaskReport **************
//
export class TaskReport extends ReportBase {
 constructor(props){
  super(props);
  const cookie = read_cookie('rims')
  this.state.node = cookie.node
  this.header = 'Tasks'
  this.thead = ['Node','Frequency','Module','Function','Arguments']
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/task_list',{node:this.state.node})
   .then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.frequency,row.module,row.function,row.args]

}

// ************** RestList **************
//
class RestList extends ListBase {
 constructor(props){
  super(props);
  this.thead=['API','Function']
  this.header='REST API'
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/rest_explore')
   .then((result) => {
    var apilist = [];
    result.data.forEach(item => item.functions.forEach(row => apilist.push({api:item.api, function:row})  ) );
    this.setState({data:apilist});
   })
 }

 listItem = (row) => [row.api,<TextButton key={'rest_' + row.api} text={row.function} onClick={() => { this.changeList(<RestInfo key={`rest_info_${row.api}_${row.function}`} {...row} />)}} />]

}

// ************** RestInfo **************
//
class RestInfo extends Component {
 constructor(props){
  super(props)
  this.state = {module:null,information:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/rest_information',{api:this.props.api, function:this.props.function})
   .then((result) => { this.setState(result) })
 }

 render() {
  if ((this.state.module === null) || (this.state.information === null))
   return <Spinner />
  else {
   return(
    <article className='text'>
     <h1>API: {this.props.api}</h1>
     {this.state.module.map((row,index) => {return <p key={'ria_'+index}>{row}</p> })}
     <h1>Function: {this.props.function}</h1>
     {this.state.information.map((row,index) => {return <p key={'rif_'+index}>{row}</p> })}
    </article>
   )
  }
 }
}

// ************************ Controls ********************
//
class RestExecute extends Component {
 componentDidMount(){
  const args = ('args' in this.props) ? this.props.args : {}
  rest_call(rest_base + 'api/' + this.props.api,args)
  .then((result) => { this.setState(result) })
 }

 render(){
  if (this.state === null)
   return <Spinner />
  else
   return <article className='code'><h1>{this.props.text}</h1><pre>{JSON.stringify(this.state,null,2)}</pre></article>
 }
}

// ************************ Controls ********************
//
// TODO: List should be dynamic from config and passed through REST engine
class Controls extends ListBase {
 constructor(props){
  super(props);
  this.state.data = [
   {api:'monitor/ipam_init',text:'IPAM status check'},
   {api:'ipam/address_events',text:'IPAM clear status logs',args:{op:'clear'}},
   {api:'monitor/interface_init',text:'Interface status check'},
   {api:'device/network_info_discover',text:'Discover device system information (sysmac etc)'},
   {api:'device/model_sync',text:'Sync device model mapping'},
   {api:'device/vm_mapping',text:'VM UUID mapping'},
   {api:'master/oui_fetch',text:'Sync OUI database'},
   {api:'reservation/expiration_status',text:'Check reservation status'}
  ]
  this.header = undefined
  this.thead = ['Control Function']
 }

 listItem = (row) => [<TextButton key={'ctrl_' + row.api} text={row.text} onClick={() => { this.changeList(<RestExecute key={'rest_' + row.api} {...row} />)}} />]
}

// ************** File List **************
//
export class FileList extends Component {
 constructor(props){
  super(props)
  this.state = {files:null}
  if (this.props.hasOwnProperty('directory')){
   this.state.mode = 'directory'
   this.state.args = {directory:this.props.directory}
  } else if (this.props.hasOwnProperty('fullpath')){
   this.state.mode = 'fullpath'
   this.state.args = {fullpath:this.props.fullpath}
  } else {
   this.state.mode = 'images'
   this.state.args = {}
  }
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/file_list',this.state.args)
  .then((result) => {
   if (result.status === 'OK')
    this.setState(result)
   else {
    window.alert("Error retrieving files:" + result.info);
    this.setState({files:[]})
   }
  })
 }

 // TODO migrate rest_base to correct / when converted to single site
 listItem = (row) => {
  if (this.state.mode === 'images')
   return (row.substr(row.length - 4) === '.png') ? [row,<img src={this.state.path +'/'+row} alt={this.state.path +'/'+row} />] : []
  else
   return [<Fragment key={row}>{this.state.path + "/"}<a href={rest_base + this.state.path + "/" + row} target="_blank" rel="noopener noreferrer">{row}</a></Fragment>]
 }

 render() {
  if (this.state.files === null)
   return <Spinner />
  else
   return (
    <article className='files'>
     <h1>{this.state.mode}</h1>
     <div className='table'>
      <div className='tbody'>
      {this.state.files.map((row,index) => <TableRow key={'content_trow_files_'+index} cells={this.listItem(row)} /> )}
      </div>
     </div>
    </article>
   )
 }
}

// ************************ TODO ********************

class ServiceInfo extends Component {
 constructor(props){
  super(props)
  this.state = {state:null}
 }

 componentDidMount(){
  this.updateService({service:this.props.service})
 }

 updateService(args){
  // Always do a reset (so do a spinner)
  this.setState({state:null})
  rest_call(rest_base + 'api/system/service_info',args)
  .then((result) => {
   if (result.status === 'OK')
    this.setState(result)
   else {
    window.alert("Error retrieving service state:" + result.info);
   }
  })
 }

 render() {
   if (this.state.state === null)
    return <Spinner />
   else {
    const state = (this.state.state === 'inactive') ? 'start' : 'stop'
    return (
     <article className='lineinput'>
      <div>
       <b>{this.props.name}</b>: {this.state.state} ({this.state.extra}) <InfoButton key={'state_change'} type={state} onClick={() => this.updateService({service:this.props.service,op:state})} />
      </div>
     </article>
    )
   }
 }
}
