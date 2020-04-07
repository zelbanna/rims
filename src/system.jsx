import React, { Component, Fragment } from 'react'
import { rest_call} from './infra/Functions.js';
import { Spinner, TableRow, RimsContext, ContentReport, ContentList, ContentData } from './infra/UI.jsx';
import { StartButton, StopButton, HrefButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavDropDown, NavInfo, NavReload } from './infra/Navigation.js';

import { LogShow } from './node.jsx';

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

 changeContent = (elem) => this.setState({content:elem})

 changeImport(module,func){
  import('./'+module+'.jsx').then(lib => {
   var Elem = lib[func];
   this.setState({content:<Elem key={module+'_'+func} />})
  })
 }

 compileNavItems = () => {
  const master = (this.context.cookie.node === 'master')
  this.context.loadNavigation(<NavBar key='system_navbar'>
   {master && <NavButton key='sys_nav_node' title='Nodes' onClick={() => this.changeImport('node','List')} />}
   {master && <NavButton key='sys_nav_srv' title='Servers' onClick={() => this.changeImport('server','List')} />}
   {master && <NavButton key='sys_nav_erd' title='ERD'     onClick={() => window.open('infra/erd.pdf','_blank')} />}
   {master && <NavButton key='sys_nav_user' title='Users'  onClick={() => this.changeImport('user','List')} />}
   {master && <NavButton key='sys_nav_ctrl' title='Controls' onClick={() => this.changeContent(<Controls key='system_controls' />)} />}
   <NavDropDown key='sys_nav_logs' title='Logs'>
    {this.state.logs.map((row,idx) => <NavButton key={'sys_nav_logs_'+idx} title={row} onClick={() => this.changeContent( <LogShow key={row.name} node={row} /> )} />)}
   </NavDropDown>
   <NavDropDown key='sys_nav_reports' title='Reports'>
    <NavButton key='sys_nav_sys' title='System' onClick={() => this.changeContent(<Report key='system_report' />)} />
    <NavButton key='sys_nav_task' title='Tasks' onClick={() => this.changeContent(<TaskReport key='task_report' />)} />
    {master && <NavButton key='sys_nav_act' title='Activities' onClick={() => this.changeImport('activity','Report')} />}
    {master && <NavButton key='sys_nav_resv' title='Reservations' onClick={() => this.changeImport('reservation','Report')} />}
    {master && <NavButton key='sys_nav_dev' title='Devices' onClick={() => this.changeImport('device','Report')} />}
    {master && <NavButton key='sys_nav_inv' title='Inventory' onClick={() => this.changeImport('inventory','Report')} />}
   </NavDropDown>
   <NavButton key='sys_nav_rest' title='REST' onClick={() => this.changeContent(<RestList key='rest_list' />)} />
   {this.state.services.length > 0 &&  <NavDropDown key='sys_nav_svcs' title='Services'>{this.state.services.map((row,idx) => <NavButton key={'sys_nav_svcs_'+idx} title={row.name} onClick={() => this.changeContent(<ServiceInfo key={row.name} {...row} /> )} />)}</NavDropDown>}
   <NavReload key='sys_nav_reload' onClick={() => this.setState({content:null})} />
   {this.state.navinfo.map((row,idx) => <NavInfo key={'sys_nav_ni_'+idx} title={row} />)}
  </NavBar>)
 }

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

 listItem = (row) => [row.api,<HrefButton key={'rest_' + row.api} text={row.function} onClick={() => { this.changeContent(<RestInfo key={`rest_info_${row.api}_${row.function}`} {...row} />)}} />]

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

 listItem = (row) => [<HrefButton key={'ctrl_' + row.api} text={row.text} onClick={() => { this.changeContent(<RestExecute key={'rest_' + row.api} {...row} />)}} />]

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
    window.alert('Error retrieving files:' + result.info);
    this.setState({files:[]})
   }
  })
 }

 listItem = (row) => {
  if (this.state.mode === 'images')
   return (row.substr(row.length - 4) === '.png') ? [row,<img src={this.state.path +'/'+row} alt={this.state.path +'/'+row} />] : []
  else
   return [<Fragment key={row}>{this.state.path + '/'}<a href={this.state.path + '/' + row} target='_blank' rel='noopener noreferrer'>{row}</a></Fragment>]
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
  this.state = {state:'inactive'}
 }

 componentDidMount(){
  this.updateService({})
 }

 updateService(args){
  // Always do a reset (so do a spinner)
  this.setState({spinner:<Spinner />})
  rest_call('api/system/service_info',{service:this.props.service,...args}).then(result => {
   if (result.status === 'OK')
    this.setState({...result,spinner:null})
   else
    window.alert('Error retrieving service state:' + result.info);
  })
 }

 render() {
  const inactive = (this.state.state === 'inactive');
  const Elem = (inactive) ? StartButton : StopButton;
  return (
   <article className='lineinput'>
    <div>
     <b>{this.props.name}</b>: {this.state.state} ({this.state.extra}) <Elem key={'state_change'} onClick={() => this.updateService({op:(inactive) ? 'start' : 'stop'})} title='Operate service' />
    </div>
    {this.state.spinner}
   </article>
   );
 }
}
