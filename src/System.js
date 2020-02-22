import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { NavBar }     from './infra/Navigation.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain, ContentTable } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

import { LogShow, List as NodeList } from './Node.js';
import { List as ServerList } from './Server.js';
import { List as UserList } from './User.js';
import { Report as ActivityReport } from './Activity.js';
import { Report as ReservationReport } from './Reservation.js';
import { Report as DeviceReport } from './Device.js';
import { Report as InventoryReport } from './Inventory.js';

/*

def rest_information(aWeb):
def rest_execute(aWeb):
def file_list(aWeb):
def images(aWeb):

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
    navitems.push({title:'Controls',  onClick:() => { this.content(<Controls  />)}})
    reports.push({title:'Activities',  onClick:() => { this.content(<ActivityReport key='activity_report' />)}})
    reports.push({title:'Reservations',  onClick:() => { this.content(<ReservationReport key='reservation_report' />)}})
    reports.push({title:'Devices',  onClick:() => { this.content(<DeviceReport key='device_report' />)}})
    reports.push({title:'Inventory',  onClick:() => { this.content(<InventoryReport key='inventory_report' />)}})
   }
   navitems.push({title:'Logs',   type:'dropdown', items:this.state.logs.map( (row,index) => { return {title:row, onClick:() => { this.content( <LogShow node={row} /> )} } } )  })
   navitems.push({title:'Report', type:'dropdown', items:reports})
   navitems.push({title:'REST',  onClick:() => { this.content(<RestExplore key='rest_explore' />) }})
   if (this.state.services.length > 0)
    navitems.push({title:'Services',   type:'dropdown', items:this.state.services.map( (row,index) => { return {title:row, onClick:() => { this.content( <ServiceInfo {... row} /> )} } } )  })

   navitems.push({ onClick:() => { this.setState({content:null}) }, className:'reload'} )
   this.state.navinfo.map(row => { navitems.push({title:row, className:'right navinfo'}) })
   reports.push({title:'Tasks',   onClick:() => { this.content(<TaskReport key='task_report' />)}})
   reports.push({title:'System',  onClick:() => { this.content(<Report key='system_report' />)}})

   return (
    <Fragment key='system_main'>
     <NavBar key='system_navbar' items={navitems} />
     <section className='content' id='div_content'>{this.state.content}</section>
    </Fragment>
   )
  }
 }
}


class Report extends Component {
 render(){
  return (<div>System Report TODO</div>)
 }
}

class TaskReport extends Component {
 render(){
  return (<div>Task Report TODO</div>)
 }
}

class RestExplore extends Component {
 render() {
  return (<div>Rest Explore TODO</div>)
 }
}

class ServiceInfo extends Component {
 render() {
  return (<div>Service Info TODO</div>)
 }
}

class Controls extends Component {
 render() {
  return (<div>System Controls TODO</div>)
 }
}
