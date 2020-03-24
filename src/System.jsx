import React, { Component, Fragment } from 'react'
import { rest_call} from './infra/Functions.js';
import { Spinner, TableRow, RimsContext, ContentReport, ContentList, ContentData } from './infra/Generic.js';
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
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {navinfo:[], navitems:[], logs:[], services:[] }
 }

 componentDidMount(){
  rest_call('api/system/service_list').then(result => {
   Object.assign(this.state,result)
   this.compileNavItems()
  })
  rest_call('api/master/inventory',{node:this.context.cookie.node, user_id:this.context.cookie.id}).then(result => {
   Object.assign(this.state,result)
   this.compileNavItems()
  })
 }

 compileNavItems = () => {
  let navitems = [];
  let reports = [];
   if (this.context.cookie.node === 'master') {
    navitems.push(
     {title:'Nodes',  onClick:() => this.changeContent(<NodeList key='node_list' />) },
     {title:'Servers', onClick:() => this.changeContent(<ServerList key='server_list' />) },
     {title:'ERD',    onClick:() => window.open('infra/erd.pdf','_blank') },
     {title:'Users',  onClick:() => this.changeContent(<UserList key='user_list' />) },
     {title:'Controls',  onClick:() => this.changeContent(<Controls  />) }
    )
    reports.push(
     {title:'Activities',  onClick:() => this.changeContent(<ActivityReport key='activity_report' />) },
     {title:'Reservations',  onClick:() => this.changeContent(<ReservationReport key='reservation_report' />) },
     {title:'Devices',  onClick:() => this.changeContent(<DeviceReport key='device_report' />) },
     {title:'Inventory',  onClick:() => this.changeContent(<InventoryReport key='inventory_report' />) }
    )
   }
   reports.push({title:'Tasks',   onClick:() => this.changeContent(<TaskReport key='task_report' />) },{title:'System',  onClick:() => this.changeContent(<Report key='system_report' />) })
   navitems.push(
    {title:'Logs',   type:'dropdown', items:this.state.logs.map(row => ({title:row, onClick:() => this.changeContent( <LogShow key={row.name} node={row} /> )})) },
    {title:'Report', type:'dropdown', items:reports},
    {title:'REST',  onClick:() => this.changeContent(<RestList key='rest_list' />) }
   )
   if (this.state.services.length > 0)
    navitems.push({title:'Services', type:'dropdown', items:this.state.services.map(row => ({title:row.name, onClick:() => this.changeContent( <ServiceInfo key={row.name} {...row} /> )})) })
   navitems.push({ onClick:() => this.setState({content:null}), className:'reload' })
   this.state.navinfo.forEach(row => navitems.push({title:row, className:'right navinfo'}))
   this.context.loadNavigation(navitems)
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <Fragment key='main_base'>{this.state.content}</Fragment>
 }
}
Main.contextType = RimsContext;

// ************** Report **************
//
export class Report extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('system/report').then(result => this.setState({data:Object.keys(result).sort((a,b) => a.localeCompare(b)).map(key => ({info:key,value:result[key]})) }))
 }

 listItem = (row) => [row.info,row.value]

 render(){
  return <ContentReport key='sys_cr' header='System Report' thead={['Key','Value']} trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** TaskReport **************
//
export class TaskReport extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/master/task_list',{node:this.context.cookie.node}).then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.frequency,row.module,row.function,row.args]

 render(){
  return <ContentReport key='task_cr' header='Tasks' thead={['Node','Frequency','Module','Function','Arguments']} trows={this.state.data} listItem={this.listItem} />
 }
}
TaskReport.contextType = RimsContext;

// ************** RestList **************
//
class RestList extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/system/rest_explore')
   .then((result) => {
    var apilist = [];
    result.data.forEach(item => item.functions.forEach(row => apilist.push({api:item.api, function:row})  ) );
    this.setState({data:apilist});
   })
 }

 listItem = (row) => [row.api,<TextButton key={'rest_' + row.api} text={row.function} onClick={() => { this.changeContent(<RestInfo key={`rest_info_${row.api}_${row.function}`} {...row} />)}} />]

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <Fragment key='rest_tp_fragment'>
   <ContentList key='rest_tp_cl' header='REST API' thead={['API','Function']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='rest_tp_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** RestInfo **************
//
class RestInfo extends Component {

 componentDidMount(){
  rest_call('api/system/rest_information',{api:this.props.api, function:this.props.function}).then(result => this.setState(result))
 }

 render() {
  if (this.state) {
   return(
    <article className='text'>
     <h1>API: {this.props.api}</h1>
     {this.state.module.map((row,index) => {return <p key={'ria_'+index}>{row}</p> })}
     <h1>Function: {this.props.function}</h1>
     {this.state.information.map((row,index) => {return <p key={'rif_'+index}>{row}</p> })}
    </article>
   )
  } else
   return <Spinner />
 }
}

// ************************ REST Execute ********************
//
class RestExecute extends Component {
 componentDidMount(){
  rest_call('api/' + this.props.api,this.props.args).then(result => this.setState(result))
 }

 render(){
  return (this.state) ? <article className='code'><h1>{this.props.text}</h1><pre>{JSON.stringify(this.state,null,2)}</pre></article> : <Spinner />
 }
}

// ************************ Controls ********************
//
// TODO: List should be dynamic from config and passed through REST engine
class Controls extends Component {
 constructor(props){
  super(props);
  this.state = {data:[
   {api:'monitor/ipam_init',text:'IPAM status check'},
   {api:'ipam/address_events',text:'IPAM clear status logs',args:{op:'clear'}},
   {api:'monitor/interface_init',text:'Interface status check'},
   {api:'device/network_info_discover',text:'Discover device system information (sysmac etc)'},
   {api:'device/model_sync',text:'Sync device model mapping'},
   {api:'device/vm_mapping',text:'VM UUID mapping'},
   {api:'master/oui_fetch',text:'Sync OUI database'},
   {api:'reservation/expiration_status',text:'Check reservation status'},
   {api:'system/sleep',text:'Sleep Test', args:{seconds:10}},
  ]}
 }

 changeContent = (elem) => this.setState({content:elem})

 listItem = (row) => [<TextButton key={'ctrl_' + row.api} text={row.text} onClick={() => { this.changeContent(<RestExecute key={'rest_' + row.api} {...row} />)}} />]

 render(){
  return <Fragment key='ctl_fragment'>
   <ContentList key='ctl_cl' header='' thead={['API']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='ctl_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
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
  rest_call('api/system/file_list',this.state.args).then(result => {
   if (result.status === 'OK')
    this.setState(result)
   else {
    window.alert("Error retrieving files:" + result.info);
    this.setState({files:[]})
   }
  })
 }

 listItem = (row) => {
  if (this.state.mode === 'images')
   return (row.substr(row.length - 4) === '.png') ? [row,<img src={this.state.path +'/'+row} alt={this.state.path +'/'+row} />] : []
  else
   return [<Fragment key={row}>{this.state.path + "/"}<a href={this.state.path + "/" + row} target="_blank" rel="noopener noreferrer">{row}</a></Fragment>]
 }

 render() {
  if (!this.state.files)
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

// ************** Service Info **************
//
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
  rest_call('api/system/service_info',args).then(result => {
   if (result.status === 'OK')
    this.setState(result)
   else
    window.alert("Error retrieving service state:" + result.info);
  })
 }

 render() {
   if (!this.state.state)
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
