import React, { Component, Fragment } from 'react'
import { post_call } from './infra/Functions.js';
import { RimsContext, Title, Spinner, Article, CodeArticle, LineArticle, ContentReport, ContentList, ContentData } from './infra/UI.jsx';
import { StartButton, StopButton, HrefButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton, NavInfo, NavReload } from './infra/Navigation.jsx';
import { TextLine } from './infra/Inputs.jsx'

import styles from './infra/ui.module.css';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {navinfo:[], navitems:[], logs:[], services:[] }
 }

 componentDidMount(){
  post_call('api/system/inventory',{user_id:this.context.settings.id}).then(result => {
   Object.assign(this.state,result)
   this.compileNavItems()
  })
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.compileNavItems();
 }

 compileNavItems = () => {
  const master = (this.context.settings.node === 'master');
  const admin = (this.context.settings.class === 'admin');
  const master_admin = (master && admin);
  this.context.loadNavigation(<NavBar key='system_navbar'>
   {master_admin && <NavButton key='sys_nav_node' title='Nodes' onClick={() => this.changeImport('node','List')} />}
   {master_admin && <NavButton key='sys_nav_srv' title='Servers' onClick={() => this.changeImport('server','List')} />}
   {master && <NavButton key='sys_nav_erd' title='ERD'     onClick={() => window.open('erd.pdf','_blank')} />}
   {master_admin && <NavButton key='sys_nav_user' title='Users'  onClick={() => this.changeImport('user','List')} />}
   {master && <NavButton key='sys_nav_ctrl' title='Controls' onClick={() => this.changeContent(<Controls key='system_controls' />)} />}
   <NavDropDown key='sys_nav_reports' title='Reports'>
    <NavDropButton key='sys_nav_sys' title='System' onClick={() => this.changeContent(<Report key='system_report' />)} />
    <NavDropButton key='sys_nav_task' title='Tasks' onClick={() => this.changeContent(<TaskReport key='task_report' />)} />
    {admin && <NavDropButton key='sys_nav_act' title='Activities' onClick={() => this.changeImport('activity','Report')} />}
    {master && <NavDropButton key='sys_nav_resv' title='Reservations' onClick={() => this.changeImport('reservation','Report')} />}
    {master && <NavDropButton key='sys_nav_dev' title='Devices' onClick={() => this.changeImport('device','Report')} />}
    {master && <NavDropButton key='sys_nav_inv' title='Inventory' onClick={() => this.changeImport('inventory','Report')} />}
   </NavDropDown>
   <NavButton key='sys_nav_logs' title='Logs' onClick={() => this.changeImport('node','LogShow',{node:this.context.settings.node})} />
   {admin && <NavButton key='sys_nav_rest' title='REST' onClick={() => this.changeContent(<RestList key='rest_list' />)} />}
   {admin && this.state.services.length > 0 && <NavDropDown key='sys_nav_svcs' title='Services'>{this.state.services.map((row,idx) => <NavDropButton key={'sys_nav_svcs_'+idx} title={row.name} onClick={() => this.changeContent(<ServiceInfo key={row.name} {...row} /> )} />)}</NavDropDown>}
   <NavReload key='sys_nav_reload' onClick={() => this.setState({content:null})} />
   {this.state.navinfo.map((row,idx) => <NavInfo key={'sys_nav_ni_'+idx} title={row} />)}
  </NavBar>)
 }

 changeContent = (elem) => this.setState({content:elem})

 changeImport(module,func,args){
  import('./'+module+'.jsx').then(lib => {
   var Elem = lib[func];
   this.setState({content:<Elem key={module+'_'+func} {...args} />})
  })
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
  post_call('api/system/report').then(result => this.setState({data:Object.keys(result).sort((a,b) => a.localeCompare(b)).map(key => ({info:key,value:result[key]})) }))
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
  post_call('api/master/task_list',{node:this.context.settings.node}).then(result => this.setState(result))
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
  post_call('api/system/rest_explore')
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
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/system/rest_information',{api:this.props.api, function:this.props.function}).then(result => this.setState(result))
 }

 render() {
  if (this.state.module && this.state.information) {
   return(
    <Article key='ri_art' header={this.props.api}>
     {this.state.module.join('\n')}
     <Title text={this.props.function} />
     {this.state.information.join('\n')}
    </Article>
   )
  } else
   return <Spinner />
 }
}

// ************************ REST Execute ********************
//
class RestExecute extends Component {
 componentDidMount(){
  post_call('api/' + this.props.api,this.props.args).then(result => this.setState(result))
 }

 render(){
  return (this.state) ? <CodeArticle key='re_code' header={this.props.text}>{JSON.stringify(this.state,null,2)}</CodeArticle> : <Spinner />
 }
}

// ************************ Controls ********************
//
// TODO: List should be dynamic from config and passed through REST engine
class Controls extends Component {
 constructor(props){
  super(props);
  this.state = {data:[
   {api:'ipam/address_events',text:'IPAM clear all status logs',args:{op:'clear'}},
   {api:'device/log_clear',text:'Device clear all status logs'},
   {api:'ipam/check',text:'IPAM status check'},
   {api:'interface/check',text:'Interface status check'},
   {api:'device/system_info_discover',text:'Discover device system information (sysmac etc)'},
   {api:'device/model_sync',text:'Sync device model mapping'},
   {api:'device/vm_mapping',text:'VM UUID mapping'},
   {api:'master/oui_fetch',text:'Sync OUI database'},
   {api:'reservation/expiration_status',text:'Check reservation status'},
   {api:'fdb/check',text:'Update FDB'}
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
  this.state = {}
 }

 componentDidUpdate(prevProps){
  if (prevProps !== this.props)
   this.loadFiles();
 }

 componentDidMount(){
  this.loadFiles()
 }

 loadFiles = () => {
  let state = {};
  if (this.props.hasOwnProperty('directory'))
   state = {mode:'directory',args:{directory:this.props.directory},files:undefined}
  else if (this.props.hasOwnProperty('fullpath'))
   state = {mode:'fullpath',args:{fullpath:this.props.fullpath},files:undefined}
  else
   state = {mode:'images',args:{},files:undefined}
  post_call('api/system/file_list',state.args).then(result => {
   if (result.status === 'OK')
    this.setState({mode:state.mode,...result})
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
   return [<Fragment key={row}>{this.state.path + '/'}<a className={styles.href} href={this.state.path + '/' + row} target='_blank' rel='noopener noreferrer'>{row}</a></Fragment>]
 }

 render() {
  return (!this.state.files) ? <Spinner /> : <ContentReport header={this.state.mode} thead={[]} trows={this.state.files} listItem={this.listItem} />
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
  post_call('api/system/service_info',{service:this.props.service,...args}).then(result => {
   if (result.status === 'OK')
    this.setState({...result,spinner:null})
   else
    window.alert('Error retrieving service state:' + result.info);
  })
 }

 render() {
  const inactive = (this.state.state === 'inactive');
  const Elem = (inactive) ? StartButton : StopButton;
  return <LineArticle key='svc_art'>
    <TextLine key='service_line' id='service' label={this.props.name} text={this.state.state + ' (' +this.state.extra +')'} /><Elem key={'state_change'} onClick={() => this.updateService({op:(inactive) ? 'start' : 'stop'})} title='Operate service' />
    {this.state.spinner}
   </LineArticle>
 }
}
