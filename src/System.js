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
  this.state = {data:null, contentright:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/rest_explore')
   .then((result) => {
    var apilist = [];
    result.data.forEach(item => item.functions.forEach(row => apilist.push({api:item.api, function:row})  ) );
    this.setState({data:apilist});
   })
 }

 contentRight = (elem) => { this.setState({contentright:elem}) }

 listItem = (row) => {
  return [row.api,<TextButton key={'rest_' + row.api} text={row.function} onClick={() => { this.contentRight(<RestInfo key={`rest_info_${row.api}_${row.function}`} {...row} />)}} />]
 }

 render() {
  return <ContentMain key='rest_content' base='rest' thead={['API','Function']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} />
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

// ************************ TODO ********************

class ServiceInfo extends Component {
 render() {
  return (<div>Service Info TODO</div>)
 }
}

class FileList extends Component {
 render() {
  return(<div>FileList</div>)
 }
}

class Images extends Component {
 render() {
  return(<div>Images</div>)
 }
}

/*
def controls(aWeb):
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/ipam_init'>IPAM status check</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/ipam_events&arguments={\"op\":\"clear\"}'>IPAM clear status logs</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/interface_init'>Interface status check</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/network_info_discover'>Discover system info</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/model_sync'>Sync models</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/vm_mapping'>VM UUID mapping</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=reservation/expiration_status'>Reservation checks</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=master/oui_fetch'>OUI Database sync</A></DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
*/

// Do when rest is done so no mapper is needed...
class Controls extends Component {
 render() {
  return (<div>System Controls TODO</div>)
 }
}
class RestExecute extends Component {
 render() {
  return(<div>RestExecute</div>)
 }
}


