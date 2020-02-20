import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { NavBar }     from './infra/Navigation.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain, ContentTable } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

import { List as NodeList } from './Node.js';
import { List as ServerList } from './Server.js';
import { List as UserList } from './User.js';
import { Report as ActivityReport } from './Activity.js';
import { Report as ReservationReport } from './Reservation.js';
import { Report as DeviceReport } from './Device.js';
import { Report as InventoryReport } from './Inventory.js';

/*

def reload(aWeb):
def rest_information(aWeb):
def rest_execute(aWeb):
def logs_clear(aWeb):
def services_info(aWeb):
def file_list(aWeb):
def images(aWeb):
def controls(aWeb):

*/

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  const cookie = read_cookie('rims')
  this.state = {content:null, cookie:cookie, navinfo:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/service_list')
   .then((result) => {
    this.setState(result)
   })
  rest_call(rest_base + 'api/master/inventory',{node:this.state.cookie.node, user_id:this.state.cookie.id})
   .then((result) => {
   this.setState(result);
   })
 }
 content = (elem) => {
  this.setState({content:elem})
 }

 render() {
  if (this.state.navinfo === null)
   return <Spinner />;
  else {
   let navitems = [];
   let reports = []
   if (this.state.cookie.node === 'master') {
    navitems.push({title:'Nodes',  onClick:() => { this.content(<NodeList key='node_list' />) }})
    navitems.push({title:'Servers', onClick:() => { this.content(<ServerList key='server_list' />)}})
    navitems.push({title:'ERD',    onClick:() => { window.open('infra/erd.pdf','_blank'); }})
    navitems.push({title:'Users',  onClick:() => { this.content(<UserList key='user_list' />)}})
    reports.push({title:'Activities',  onClick:() => { this.content(<ActivityReport key='activity_report' />)}})
    reports.push({title:'Reservations',  onClick:() => { this.content(<ReservationReport key='reservation_report' />)}})
    reports.push({title:'Devices',  onClick:() => { this.content(<DeviceReport key='device_report' />)}})
    reports.push({title:'Inventory',  onClick:() => { this.content(<InventoryReport key='inventory_report' />)}})
   }
   navitems.push({title:'Logs',   type:'dropdown', items:this.state.logs.map( (row,index) => { return {title:row, onClick:() => { this.content( <LogShow node={row} /> )} } } )  })
   reports.push({title:'Tasks',   onClick:() => { this.content(<TaskReport key='task_report' />)}})
   reports.push({title:'System',  onClick:() => { this.content(<Report key='system_report' />)}})
   navitems.push({title:'Report', type:'dropdown', items:reports})
   navitems.push({title:'REST',  onClick:() => { this.content(<RestExplore key='rest_explore' />) }})

   return (
    <Fragment key='system_main'>
     <NavBar key='system_navbar' items={navitems} />
     <section className='content' id='div_content'>{this.state.content}</section>
    </Fragment>
   )
  }
 }
}

/*

def main(aWeb):
 if len(tools) > 0 or len(svcs) > 0:
  aWeb.wr("<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>")
  for tool in tools:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='%s'>%s</A>"%(tool['href'],tool['title']))
  for svc in svcs:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_services_info?service=%s'>%s</A>"%(svc['service'],svc['name']))
 aWeb.wr("</DIV></LI>")
 if aWeb.node() == 'master':
  aWeb.wr("<LI><A CLASS='z-op' DIV=div_content URL='system_controls'>Controls</A></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='system_main'></A></LI>")
 if data.get('navinfo'):
  for info in data['navinfo']:
   aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%info)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")


*/

class Report extends Component {
 render(){
  return (<div>System Report</div>)
 }
}

class LogShow extends Component {
 render(){
  return (<div>Log Show</div>)
 }
}

class TaskReport extends Component {
 render(){
  return (<div>Task Report</div>)
 }
}

class RestExplore extends Component {
 render() {
  return (<div>Rest Explore</div>)
 }
}
