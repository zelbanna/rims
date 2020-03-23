import React, { Component, Fragment } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, StateMap, SearchField, InfoCol2, RimsContext, ContentList, ContentData } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { NavBar } from './infra/Navigation.js'

import { List as ReservationList } from './Reservation.jsx';
import { List as LocationList } from './Location.jsx';
import { List as ServerList } from './Server.jsx';
import { NetworkList as IPAMNetworkList } from './IPAM.jsx';
import { DomainList as DNSDomainList } from './DNS.jsx';
import { List as VisualizeList, Edit as VisualizeEdit } from './Visualize.jsx';
import { List as RackList, Inventory as RackInventory, Infra as RackInfra } from './Rack.jsx';
import { List as InterfaceList } from './Interface.jsx';

// **************** Main ****************
//
// TODO - proper PDU and Console action for rack devices
//
export class Main extends MainBase {

 componentDidMount(){
  if (this.props.rack_id)
   rest_call("api/rack/inventory",{id:this.props.rack_id}).then(result => this.compileNavItems({rack_id:this.props.rack_id, ...result}))
  else
   this.compileNavItems({pdu:[], console:[], name:'N/A', rack_id:undefined});
 }

 compileNavItems = (state) => {
  const navitems = [
   {title:'Devices', type:'dropdown', items:[
    {title:'List', onClick:() => this.changeContent(<List key='dl' changeSelf={this.changeContent} rack_id={state.rack_id} />)},
    {title:'Search', onClick:() => this.changeContent(<Search key='ds' changeSelf={this.changeContent} />)},
    {title:'Types', onClick:() => this.changeContent(<TypeList key='dtl' changeSelf={this.changeContent} />)},
    {title:'Models', onClick:() => this.changeContent(<ModelList key='dml' />)}
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
  if (state.pdu.length > 0)
   navitems.push({title:'PDUs', type:'dropdown', items:state.pdu.map(row => ({title:row.hostname, onClick:() =>alert('implement PDU')}))})
  if (state.console.length > 0)
   navitems.push({title:'Consoles', type:'dropdown', items:state.console.map(row => ({title:row.hostname, onClick:() => alert('implement Console')}))})
  if (state.rack_id)
   navitems.push({title:state.name, onClick:() => this.changeContent(<RackInventory key='rack_inventory' id={state.rack_id} />)})
  navitems.push({ onClick:() => this.setState({content:null}), className:'reload' })
  this.context.loadNavigation(navitems)
 }

}
Main.contextType = RimsContext;


// ************** Search **************
//
class Search extends Component {
  constructor(props){
  super(props)
  this.state = {field:'ip',search:''}
 }

 changeHandler = (e) => {
  this.setState({[e.target.name]:e.target.value})
 }

 render() {
  return (
   <article className='lineinput'>
    <h1>Device Search</h1>
    <div>
     <span>Field:
      <select id='field' name='field' onChange={this.changeHandler} value={this.state.field}>
       <option value='hostname'>Hostname</option>
       <option value='type'>Type</option>
       <option value='id'>ID</option>
       <option value='ip'>IP</option>
       <option value='mac'>MAC</option>
       <option value='type'>Type</option>
       <option value='ipam_id'>IPAM ID</option>
      </select>:
      <input type='text' id='search' name='search' required='required' onChange={this.changeHandler} value={this.state.search} placeholder='search' />
     </span>
     <InfoButton key='ds_btn_search' type='search' title='Search' onClick={() => this.props.changeSelf(<List key='dl' {...this.state} changeSelf={this.props.changeSelf} />)} />
    </div>
   </article>
  )
 }
}
// ************** List **************
//
class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, content:null, sort:(props.hasOwnProperty('sort')) ? props.sort : 'hostname', rack_id:this.props.rack_id, searchfield:'', field:this.props.field, search:this.props.search}
 }

 componentDidMount(){
  rest_call('api/device/list', {sort:this.state.sort, rack_id:this.state.rack_id, field:this.state.field, search:this.state.search}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})

 searchHandler = (e) => { this.setState({searchfield:e.target.value}) }

 sortList = (method) => {
  if (method === 'hostname')
   this.state.data.sort((a,b) => a.hostname.localeCompare(b.hostname));
  else
   this.state.data.sort((a,b) => {
    const num1 = Number(a.ip.split(".").map(num => (`000${num}`).slice(-3) ).join(""));
    const num2 = Number(b.ip.split(".").map(num => (`000${num}`).slice(-3) ).join(""));
    return num1-num2;
   });
  this.setState({sort:method})
 }

 listItem = (row) => [
  row.ip,
  <TextButton key={'dl_btn_info_'+row.id} text={row.hostname} onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} />,
  StateMap({state:row.state}),
  <InfoButton key={'dl_btn_del_'+row.id} type='delete' onClick={() => { this.deleteList('api/device/delete',row.id,'Really delete device?'); }} />
 ]

 deleteList = (api,id,msg) => {
  if (window.confirm(msg))
   rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null}))
 }

 render(){
  if (!this.state.data)
   return <Spinner />
  else {
   let device_list = this.state.data.filter(row => row.hostname.includes(this.state.searchfield));
   const thead = [<TextButton key='dl_btn_ip' text='IP' className={(this.state.sort === 'ip') ? 'highlight':''} onClick={() => { this.sortList('ip') }} />,<TextButton key='dl_btn_hostname' text='Hostname' className={(this.state.sort === 'hostname') ? 'highlight':''} onClick={() => { this.sortList('hostname') }} />,'',''];
   return <Fragment key={'dl_fragment'}>
    <ContentList key='dl_list' header='Device List' thead={thead}listItem={this.listItem} trows={device_list}>
     <InfoButton key='dl_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
     <InfoButton key='dl_btn_items' type='items'   onClick={() => { Object.assign(this.state,{rack_id:undefined,field:undefined,search:undefined}); this.componentDidMount(); }} title='All items' />
     <InfoButton key='dl_btn_add' type='add'       onClick={() => this.changeContent(<New key={'dn_' + rnd()} id='new' />) } />
     <InfoButton key='dl_btn_devices' type='devices' onClick={() => this.changeContent(<Discover key='dd' />) } title='Discovery' />
     <SearchField key='dl_searchfield' searchHandler={this.searchHandler} value={this.state.searchfield} placeholder='Search devices' />
    </ContentList>
    <ContentData key='dl_content'>{this.state.content}</ContentData>
   </Fragment>
  }
 }
}

// ************** Info **************
//
export class Info extends Component {
 constructor(props){
  super(props)
  this.state = {data:undefined, found:true, content:null}
 }

 changeHandler = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data})
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) => {
  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 componentDidMount(){
  rest_call("api/device/info",{id:this.props.id, extra:["types","classes"]}).then(result => this.setState(result))
 }

 lookupInfo = () => {
  setTimeout(() => window.alert('lookup'),3000)
 }

 render() {
  if(this.state.data){
   const info =  [
    {tag:'span', id:'name', text:'Name', value:this.state.data.hostname},
    {tag:'input', type:'text', id:'mac', text:'Sys MAC', value:this.state.data.mac, title:'System MAC'},
    {tag:'span', id:'if_mac', text:'Mgmt MAC', value:this.state.extra.interface_mac, title:'Management Interface MAC'},
    {tag:'span', id:'if_ip', text:'Mgmt IP', value:this.state.extra.interface_ip},
    {tag:'span', id:'snmp', text:'SNMP', value:this.state.data.snmp},
    {tag:'state', id:'state', text:'State', value:[this.state.extra.if_state,this.state.extra.ip_state]}
   ];
   const extra = [
    {tag:'span', id:'id', text:'ID', value:this.props.id},
    {tag:'select', id:'class', text:'Class', value:this.state.data.class, options:this.state.classes.map(row => ({value:row, text:row}))},
    {tag:'select', id:'type_id', text:'Type', value:this.state.data.type_id, options:this.state.types.map(row => ({value:row.id, text:row.name}))},
    {tag:'input', type:'text', id:'model', text:'Model', value:this.state.data.model, extra:this.state.data.model},
    {tag:'span', id:'version', text:'Version', value:this.state.data.version},
    {tag:'input', type:'text', id:'serial', text:'S/N', value:this.state.data.serial}
   ];
   let vm = [];
   if (this.state.vm)
    vm = [
    {tag:'span', id:'vm_name', text:'VM Name', value:this.state.vm.name},
    {tag:'span', id:'vm_host', text:'VM Host', value:this.state.vm.host},
    {tag:'span', id:'vm_uuid', text:'VM UUID', value:this.state.vm.device_uuid, style:{maxWidth:170}, extra:this.state.vm.device_uuid},
    {tag:'span', id:'vm_uhost', text:'Host UUID', value:this.state.vm.server_uuid, style:{maxWidth:170}, extra:this.state.vm.server_uuid}
    ]
   let rack = [];
   if (this.state.rack){
    rack = [
     {tag:'span', id:'rack_pos', text:'Rack/Pos', value:`${this.state.rack.rack_name} (${this.state.rack.rack_unit})`},
     {tag:'span', id:'rack_size', text:'Size (U)', value:this.state.rack.rack_name},
     {tag:'span', id:'rack_con', text:'TS/Port', value:`${this.state.rack.console_name} (${this.state.rack.console_port})`}
    ];
    this.state.pems.map(pem => rack.push({tag:'span', id:'pem_'+pem.id, text:pem.name+' PDU', value:`${pem.pdu_name} (${pem.pdu_unit})`}));
   }
   const text = [
    {tag:'input', type:'text', id:'comment', text:'Comments', value:this.state.data.comment},
    {tag:'input', type:'url', id:'url', text:'URL', value:this.state.data.url}
   ];
   const buttons = [
    <InfoButton key='di_btn_save' type='save' onClick={() => this.updateInfo('api/device/info')} />,
    <InfoButton key='di_btn_conn' type='connections' onClick={() => this.changeContent(<InterfaceList key='interface_list' device_id={this.props.id} />)} />,
    <InfoButton key='di_btn_cont' type='start' onClick={() => this.changeContent(<Control key='device_control' id={this.props.id} />)} />,
    <InfoButton key='di_btn_conf' type='document' onClick={() => this.changeContent(<Configuration key='device_configure' device_id={this.props.id} />)} />
   ]
   if(this.props.changeSelf)
    buttons.push(
     <InfoButton key='di_btn_edit' type='edit' onClick={() => this.props.changeSelf(<Extended key={'de_'+this.props.id} id={this.props.id} />)} />,
     <InfoButton key='di_btn_netw' type='network' onClick={() => this.props.changeSelf(<VisualizeEdit key={'ve_'+this.props.id} type='device' id={this.props.id} changeSelf={this.props.changeSelf} />)} />
    )
   if(this.state.extra.interface_ip)
    buttons.push(
     <InfoButton key='di_btn_srch' type='search' onClick={() => this.lookupInfo()} />,
     <InfoButton key='di_btn_logs' type='logs' onClick={() => this.changeContent(<Logs key='device_logs' id={this.props.id} />)} />,
     <InfoButton key='di_btn_ssh'  type='term' onClick={() => { const sshWin = window.open(`ssh://${this.state.extra.username}@${this.state.extra.interface_ip}`,'_blank'); sshWin.close(); }} />
    )
   return (
    <Fragment key='di_fragment'>
     <article className='info'>
     <h1>Device Info</h1>
     <InfoCol2 key='di_info'  griditems={info} changeHandler={this.changeHandler} className='left' />
     <InfoCol2 key='di_extra' griditems={extra} changeHandler={this.changeHandler} className='left' />
     <InfoCol2 key='di_rack'  griditems={rack} changeHandler={this.changeHandler} className='left' />
     <InfoCol2 key='di_vm'    griditems={vm}   changeHandler={this.changeHandler} className='left' />
     <br />
     <InfoCol2 key='di_text'  griditems={text} changeHandler={this.changeHandler} />
     <br />
     {buttons}
     <span className='results'>{JSON.stringify(this.state.update)}</span>
    </article>
    <NavBar key='di_navbar' items='' />
    {this.state.content}
    </Fragment>
   )
  } else
   return <Spinner />
 }
}

/*
 if dev.get('rack') and dev['rack'].get('console_ip') and dev['rack'].get('console_port'):
  # Hardcoded port to 60xx
  aWeb.wr(aWeb.button('term',TITLE='Console', HREF='telnet://%s:%i'%(dev['rack']['console_ip'],6000+dev['rack']['console_port'])))
 if dev_info.get('url'):
  aWeb.wr(aWeb.button('ui',TITLE='WWW', TARGET='_blank', HREF=dev_info['url']))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('update','')))
*/

// ************** New **************
//
export class New extends InfoBase {
 constructor(props){
  super(props)
  this.state.data = {ip:this.props.ip,mac:'00:00:00:00:00:00',class:'device',ipam_network_id:this.props.ipam_network_id,hostname:''}
 }

 componentDidMount(){
  rest_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}))
  rest_call('api/ipam/network_list').then(result => this.setState({networks:result.data}))
  rest_call('api/device/class_list').then(result => this.setState({classes:result.data}))
 }

 addDevice = () => {
  if (this.state.data.hostname)
   rest_call("api/device/new",this.state.data).then(result => this.setState({result:JSON.stringify(result)}))
 }

 searchIP = () => {
  if (this.state.data.ipam_network_id)
   rest_call("api/ipam/address_find",{network_id:this.state.data.ipam_network_id}).then(result => this.setState({data:{...this.state.data, ip:result.ip}}))
 }

 infoItems = () => [
    {tag:'input', type:'text', id:'hostname', text:'Hostname', value:this.state.data.hostname, placeholder:'Device hostname'},
    {tag:'select', id:'class', text:'Class', value:this.state.data.class, options:this.state.classes.map(row => ({value:row, text:row}))},
    {tag:'select', id:'ipam_network_id', text:'Network', value:this.state.data.ipam_network_id, options:this.state.networks.map(row => ({value:row.id, text:`${row.netasc} (${row.description})`}))},
    {tag:'select', id:'a_domain_id', text:'Domain', value:this.state.data.a_domain_id, options:this.state.domains.map(row => ({value:row.id, text:row.name}))},
    {tag:'input', type:'text', id:'ip', text:'IP', value:this.state.data.ip},
    {tag:'input', type:'text', id:'mac', text:'MAC', value:this.state.data.mac}
   ]

 render() {
   if (!this.state.domains || !this.state.classes || !this.state.networks)
    return <Spinner />
   else
    return (
     <article className='info'>
      <h1>Device Add</h1>
      <InfoCol2 key='da_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
      <InfoButton key='da_start' type='start' onClick={() => this.addDevice()} />
      <InfoButton key='da_search' type='search' onClick={() => this.searchIP()} />
      <span className='results'>{this.state.result}</span>
     </article>
    )
 }
}

// ************** Discover **************
//
class Discover extends Component {
 constructor(props){
  super(props)
  this.state = {ipam_network_id:undefined,a_domain_id:undefined,content:null}
 }

 componentDidMount(){
  rest_call("api/ipam/network_list").then(result => this.setState({networks:result.data}))
  rest_call("api/dns/domain_list",{filter:'forward'}).then(result => this.setState({domains:result.data}))
 }

 changeHandler = (e) => this.setState({[e.target.name]:e.target.value});

 changeContent = (elem) => this.setState({content:elem})

 infoItems = () => [
  {tag:'select', id:'ipam_network_id', text:'Network', value:this.state.ipam_network_id, options:this.state.networks.map(row => ({value:row.id, text:`${row.netasc} (${row.description})`}))},
  {tag:'select', id:'a_domain_id', text:'Domain', value:this.state.a_domain_id, options:this.state.domains.map(row => ({value:row.id, text:row.name}))}
 ]

 Result(props){
  return  <article className='code'><pre>{JSON.stringify(props.result,null,2)}</pre></article>
 }

 render() {
  if (!this.state.discover && this.state.networks && this.state.domains){
   return (
    <Fragment key='dd_fragment'>
     <article className="info">
      <h1>Device Discovery</h1>
      <InfoCol2 key='dd_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
      <InfoButton key='dd_save' type='start' onClick={() => this.changeContent(<DiscoverRun key={'dd_run_' + this.state.ipam_network_id} ipam_network_id={this.state.ipam_network_id} a_domain_id={this.state.a_domain_id} />)} />
     </article>
     <NavBar key='dd_nav' />
     {this.state.content}
    </Fragment>
   )
  } else
   return <Spinner />
 }
}

class DiscoverRun extends Component {
 componentDidMount(){
  rest_call("api/device/discover",{network_id:this.props.ipam_network_id, a_domain_id:this.props.a_domain_id}).then(result => this.setState(result))
 }

 render(){
  return (this.state) ? <article className='code'><pre>{JSON.stringify(this.state,null,2)}</pre></article> : <Spinner />
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
  rest_call('api/device/list', { extra:['system','type','mac','oui','class']}).then(result => this.setState(result))
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
  rest_call('api/device/type_list').then(result => this.setState(result))
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
  rest_call('api/device/model_list').then(result => this.setState({...result,result:'OK'}))
 }

 syncModels(){
  rest_call('api/device/model_list',{op:'sync'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.name,row.type,<Fragment key={'ml_' + row.id}>
  <InfoButton type='info' onClick={() => this.changeContent(<ModelInfo key={'model_info_'+row.id} id={row.id} />)} />
  <InfoButton type='delete' onClick={() => this.deleteList('api/device/model_delete',row.id,'Really delete model?') } />
 </Fragment>]
}

// ************** Model Info **************
//
export class ModelInfo extends InfoBase {

 componentDidMount(){
  rest_call('api/device/model_info',{id:this.props.id}).then(result => this.setState(result))
 }

 infoItems = () => [
    {tag:'span', id:'name', text:'Name', value:this.state.data.name},
    {tag:'span', id:'type', text:'Type', value:this.state.extra.type},
    {tag:'input', type:'text', id:'defaults_file', text:'Defaults File', value:this.state.data.defaults_file},
    {tag:'input', type:'text', id:'image_file', text:'Image File', value:this.state.data.image_file}
   ]

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Device Model</h1>
     <InfoCol2 key='device_model_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <label htmlFor='parameters'>Parameters:</label>
     <textarea id='parameters' name='parameters' className='info' onChange={this.changeHandler} value={this.state.data.parameters} />
     <InfoButton key='device_model_save' type='save' onClick={() => this.updateInfo('api/device/model_info')} />
    </article>
   );
  else
   return <Spinner />
 }
}

// ************** OUI Search **************
//
class OUISearch extends Component {
 constructor(props){
  super(props)
  this.state = {data:{oui:''},content:null}
 }

 changeHandler = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 ouiSearch = () => {
  rest_call('api/master/oui_info',{oui:this.state.data.oui}).then(result => this.setState({content:<article><div className='info col2'><label htmlFor='oui'>OUI:</label><span id='oui'>{result.oui}</span><label htmlFor='company'>Company:</label><span id='company'>{result.company}</span></div></article>}))
 }

 render() {
  return (<div className='flexdiv'>
   <article className='lineinput'>
    <h1>OUI Search</h1>
    <div>
     <span>Type OUI or MAC address to find OUI/company name:<input type='text' id='oui' name='oui' required='required' onChange={this.changeHandler} value={this.state.data.oui} placeholder='00:00:00' /></span>
     <InfoButton type='search' title='Search' onClick={() => this.ouiSearch()} />
    </div>
   </article>
   {this.state.content}
  </div>)
 }
}

// ************** OUI LIST **************
//
class OUIList extends Component {

 componentDidMount(){
  rest_call('api/master/oui_list').then(result => this.setState(result))
 }

 render(){
  if (this.state)
   return <article className='table'>
    <h1>OUI</h1>
    <div className='table'>
     <div className='thead'>
      <div>oui</div><div>company</div>
     </div>
     <div className='tbody'>
      {this.state.data.map((row,index) => <div key={'tr_'+index}><div>{`${row.oui.substring(0,2)}:${row.oui.substring(2,4)}:${row.oui.substring(4,6)}`}</div><div>{row.company}</div></div>)}
     </div>
    </div>
   </article>
  else
   return <Spinner />
 }
}

// ************** TODO **************
//
export class Logs extends Component {
 render() {
  return (<div>Device Logs (TODO)</div>);
 }
}

class Extended extends Component {
 render() {
  return (<div>Device Extended (TODO)</div>);
 }
}

class Control extends Component {
 render() {
  return (<div>Device Control (TODO)</div>);
 }
}

class Function extends Component {
 render() {
  return (<div>Device Function (TODO)</div>);
 }
}

class Configuration extends Component {
 render() {
  return (<div>Device Configuration (TODO)</div>);
 }
}

class ToConsole extends Component {
 render() {
  return (<div>Device To Console (TODO)</div>);
 }
}



