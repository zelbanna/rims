import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { TextButton } from './infra/Buttons.js';
import { ContentMain, ContentList } from './infra/Content.js';

import { LogShow, List as NodeList } from './Node.js';
import { List as ServerList } from './Server.js';
import { List as UserList } from './User.js';
import { Report as ActivityReport } from './Activity.js';
import { Report as ReservationReport } from './Reservation.js';
import { Report as DeviceReport } from './Device.js';
import { Report as InventoryReport } from './Inventory.js';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  const cookie = read_cookie('rims')
  this.state = {content:null, cookie:cookie, navinfo:[], navitems:[],logs:[],services:[]}
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
  let reports = []
   if (this.state.cookie.node === 'master') {
    navitems.push({title:'Nodes',  onClick:() => { this.content(<NodeList key='node_list' />) }})
    navitems.push({title:'Servers', onClick:() => { this.content(<ServerList key='server_list' />)}})
    navitems.push({title:'ERD',    onClick:() => { window.open('infra/erd.pdf','_blank'); }})
    navitems.push({title:'Users',  onClick:() => { this.content(<UserList key='user_list' />)}})
    navitems.push({title:'Controls',  onClick:() => { this.content(<Controls  />)}})
    reports.push({title:'Activities',  onClick:() => { this.content(<ActivityReport key='activity_report' />)}})
    reports.push({title:'Reservations',  onClick:() => { this.content(<ReservationReport key='reservation_report' />)}})
    reports.push({title:'Devices',  onClick:() => { this.content(<DeviceReport key='device_report' />)}})
    reports.push({title:'Inventory',  onClick:() => { this.content(<InventoryReport key='inventory_report' />)}})
   }
   reports.push({title:'Tasks',   onClick:() => { this.content(<TaskReport key='task_report' />)}})
   reports.push({title:'System',  onClick:() => { this.content(<Report key='system_report' />)}})
   navitems.push({title:'Logs',   type:'dropdown', items:this.state.logs.map( (row,index) => { return {title:row, onClick:() => { this.content( <LogShow node={row} /> )} } } )  })
   navitems.push({title:'Report', type:'dropdown', items:reports})
   navitems.push({title:'REST',  onClick:() => { this.content(<RestList key='rest_list' />) }})
   if (this.state.services.length > 0)
    navitems.push({title:'Services',   type:'dropdown', items:this.state.services.map( (row,index) => { return {title:row, onClick:() => { this.content( <ServiceInfo {... row} /> )} } } )  })
   navitems.push({ onClick:() => { this.setState({content:null}) }, className:'reload'} )
   this.state.navinfo.forEach(row => navitems.push({title:row, className:'right navinfo'}))
   this.props.loadNavigation(navitems)
 }

 content = (elem) => {
  this.setState({content:elem})
 }

 render() {
  if (this.state.navinfo === null)
   return <Spinner />;
  else {
   return (
    <Fragment key='system_main'>
     {this.state.content}
    </Fragment>
   )
  }
 }
}

// ************** Report **************
//
export class Report extends Component{
 constructor(props){
  super(props);
  this.state = {data:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'system/report')
   .then((result) => {
   this.setState({data:Object.keys(result).sort(function(a,b){ return a-b}).map(key => { return {info:key,value:result[key]}})});
  })
 }

 listItem = (row) => {
 return [row.info,row.value];
 }

 render(){
  return <ContentList key='system_content' base='system' header='System' thead={['Information','Value']}
    trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** TaskReport **************
//
export class TaskReport extends Component{
 constructor(props){
  super(props);
  const cookie = read_cookie('rims')
  this.state = {data:null,node:cookie.node}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/task_list',{node:this.state.node})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => {
 return [row.node,row.frequency,row.module,row.function,row.args];
 }

 render(){
  return <ContentList key='system_content' base='system' header='System' thead={['Node','Frequency','Module','Function','Args']}
    trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** RestList **************
//
class RestList extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, content:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/rest_explore')
   .then((result) => {
    var apilist = [];
    result.data.forEach(item => item.functions.forEach(row => apilist.push({api:item.api, function:row})  ) );
    this.setState({data:apilist});
   })
 }

 changeContent = (elem) => { this.setState({content:elem}) }

 listItem = (row) => {
  return [row.api,<TextButton key={'rest_' + row.api} text={row.function} onClick={() => { this.changeContent(<RestInfo key={`rest_info_${row.api}_${row.function}`} {...row} />)}} />]
 }

 render() {
  return <ContentMain key='rest_content' base='rest' thead={['API','Function']}
    trows={this.state.data} content={this.state.content} listItem={this.listItem} />
 }
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
     {this.state.module.map(row => {return <p>{row}</p> })}
     <h1>Function: {this.props.function}</h1>
     {this.state.information.map(row => {return <p>{row}</p> })}
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
class Controls extends Component {
 constructor(props){
  super(props);
  const items = [
   {api:'monitor/ipam_init',text:'IPAM status check'},
   {api:'ipam/address_events',text:'IPAM clear status logs',args:{op:'clear'}},
   {api:'monitor/interface_init',text:'Interface status check'},
   {api:'device/network_info_discover',text:'Discover device system information (sysmac etc)'},
   {api:'device/model_sync',text:'Sync device model mapping'},
   {api:'device/vm_mapping',text:'VM UUID mapping'},
   {api:'master/oui_fetch',text:'Sync OUI database'},
   {api:'reservation/expiration_status',text:'Check reservation status'}
  ]
  this.state = {content:null,items:items}
 }

 changeContent = (elem) => { this.setState({content:elem}) }

 listItem = (row) => {
  return [<TextButton key={'ctrl_' + row.api} text={row.text} onClick={() => { this.changeContent(<RestExecute key={'rest_' + row.api} {...row} />)}} />]
 }

 render() {
  if (this.state.items === null)
   return <Spinner />
  else
   return <ContentMain key='ctrl_content' base='ctrl' thead={['Control Function']}
    trows={this.state.items} content={this.state.content} listItem={this.listItem} />
 }
}

// ************************ TODO ********************

class ServiceInfo extends Component {
 render() {
  return (<div>Service Info TODO</div>)
 }
}

export class FileList extends Component {
 render() {
  return(<div>FileList</div>)
 }
}

export class Images extends Component {
 render() {
  return(<div>Images</div>)
 }
}
