import React, { Component, Fragment } from 'react';
import { post_call } from './infra/Functions.js';
import { RimsContext, Flex, Spinner, StateLeds, Article, CodeArticle, InfoArticle, InfoColumns, LineArticle, Result, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton } from './infra/Navigation.jsx'
import { TextAreaInput, TextInput, TextLine, StateLine, SelectInput, UrlInput, SearchInput } from './infra/Inputs.jsx';
import { AddButton, BackButton, CheckButton, ConfigureButton, DeleteButton, GoButton, HeaderButton, HealthButton, HrefButton, InfoButton, ItemsButton, LogButton, NetworkButton, ReloadButton, RevertButton, SaveButton, SearchButton, ShutdownButton, StartButton, SyncButton, TermButton, UiButton } from './infra/Buttons.jsx';

import { List as FdbList, Device as FdbDevice, Search as FdbSearch } from './fdb.jsx';
import styles from './infra/ui.module.css';


// **************** Main ****************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {pdu:[], console:[], name:'N/A', rack_id:undefined}
 }

 componentDidMount(){
  if (this.props.rack_id)
   post_call('api/rack/inventory',{id:this.props.rack_id}).then(result => {
    Object.assign(this.state,{rack_id:this.props.rack_id, ...result})
    this.compileNavItems();
   })
  else
   this.compileNavItems();
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.compileNavItems();
 }

 compileNavItems = () => {
  this.context.loadNavigation(<NavBar key='device_navbar'>
   <NavDropDown key='dev_nav_devs' title='Devices'>
    <NavDropButton key='dev_nav_list' title='List' onClick={() => this.changeContent(<List key='dl' rack_id={this.state.rack_id} />)} />
    <NavDropButton key='dev_nav_new' title='New' onClick={() => this.changeContent(<New key='device_new' ip='0.0.0.0' />)} />
    <NavDropButton key='dev_nav_srch' title='Search' onClick={() => this.changeContent(<Search key='ds' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_types' title='Types' onClick={() => this.changeContent(<TypeList key='dtl' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_model' title='Models' onClick={() => this.changeContent(<ModelList key='dml' />)} />
   </NavDropDown>
   <NavDropDown key='dev_nav_tools' title='Tools'>
    <NavDropButton key='dev_nav_fdbx' title='FDB Search' onClick={() => this.changeContent(<FdbSearch key='fdb_search' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_fdbs' title='FDB List' onClick={() => this.changeContent(<FdbList key='fdb_list' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_ouis' title='OUI Search' onClick={() => this.changeContent(<OUISearch key='oui_search' />)} />
    <NavDropButton key='dev_nav_ouil' title='OUI List' onClick={() => this.changeContent(<OUIList key='oui_list' />)} />
    <NavDropButton key='dev_nav_resv' title='Reservations' onClick={() => this.changeImport('reservation','List',{})} />
   </NavDropDown>
   {(this.state.pdu.length > 0) && <NavDropDown key='dev_nav_pdus' title='PDUs'>{this.state.pdu.map((row,idx) => <NavDropButton key={'dev_nav_pdu_' + idx} title={row.hostname} onClick={() => this.changeImport('pdu','Inventory',{device_id:row.id,type:row.type})} />)}</NavDropDown>}
   {(this.state.console.length > 0) && <NavDropDown key='dev_nav_consoles' title='Consoles'>{this.state.console.map((row,idx) => <NavDropButton key={'dev_nav_console_' + idx} title={row.hostname} onClick={() => this.changeImport('console','Inventory',{device_id:row.id,type:row.type})} />)}</NavDropDown>}
   {(this.state.rack_id) && <NavButton key='dev_nav_rack' title={this.state.name} onClick={() => this.changeImport('rack','Layout',{id:this.state.rack_id})} />}
   <NavButton key='dev_nav_maps' title='Maps' onClick={() => this.changeImport('visualize','List',{})} style={{float:'right'}}/>
   <NavDropDown key='dev_nav_ipam' title='IPAM' style={{float:'right'}}>
    <NavDropButton key='dev_nav_nets' title='Networks' onClick={() => this.changeImport('ipam','NetworkList',{})} />
    <NavDropButton key='dev_nav_isrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'DHCP'})} />
   </NavDropDown>
   <NavDropDown key='dev_nav_dns' title='DNS' style={{float:'right'}}>
    <NavDropButton key='dev_nav_doms' title='Domains' onClick={() => this.changeImport('dns','DomainList',{})} />
    <NavDropButton key='dev_nav_dsrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'NAMESERVER'})} />
    <NavDropButton key='dev_nav_recs' title='Recursors' onClick={() => this.changeImport('server','List',{type:'RECURSOR'})} />
   </NavDropDown>
  </NavBar>)
 }

 changeImport(module,func,args){
  import('./'+module+'.jsx').then(lib => {
   var Elem = lib[func];
   this.setState({content:<Elem key={module+'_'+func} {...args} />})
  })
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <>{this.state.content}</>
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

 changeContent = (elem) => this.props.changeSelf(elem);

 onChange = (e) => this.setState({[e.target.name]:e.target.value})

 render() {
  return <LineArticle key='ds_art' header='Device Search'>
   <SelectInput key='field' id='field' onChange={this.onChange} value={this.state.field}>
    <optgroup label='Group'>
     <option value='hostname'>Hostname</option>
     <option value='type'>Type</option>
    </optgroup>
    <optgroup label='Unique'>
     <option value='id'>ID</option>
     <option value='ip'>IP</option>
     <option value='mac'>MAC</option>
     <option value='interface_id'>Interface ID</option>
    </optgroup>
    </SelectInput>
    <TextInput key='search' id='search' onChange={this.onChange} value={this.state.search} placeholder='search' />
    <SearchButton key='ds_btn_search' onClick={() => this.changeContent(<List key='device_list' {...this.state} />)} title='Search devices' />
   </LineArticle>
 }
}
// ************** List **************
//
class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, sort:(props.hasOwnProperty('sort')) ? props.sort : 'hostname', rack_id:this.props.rack_id, searchfield:'', field:this.props.field, search:this.props.search}
 }

 componentDidMount(){
  post_call('api/device/list', {sort:this.state.sort, rack_id:this.state.rack_id, field:this.state.field, search:this.state.search}).then(result => this.setState(result));
 }

 sortList = (method) => {
  if (method === 'hostname')
   this.state.data.sort((a,b) => a.hostname.localeCompare(b.hostname));
  else
   this.state.data.sort((a,b) => {
    if (a.ip && b.ip){
     const num1 = Number(a.ip.split('.').map(num => (`000${num}`).slice(-3) ).join(''));
     const num2 = Number(b.ip.split('.').map(num => (`000${num}`).slice(-3) ).join(''));
     return num1-num2;
   } else if (a.ip)
    return 1;
   else
    return a.hostname.localeCompare(b.hostname)
   });
  this.setState({sort:method});
 }

 listItem = (row) => [row.ip,<HrefButton key={'info_'+row.id} text={row.hostname} onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title={row.id} />,<>
  <StateLeds key='state' state={(row.ip_state) ? row.ip_state : row.if_state} />
  <InfoButton key='info' onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title={row.id} />
  <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete device' />
 </>]

 deleteList = (id) => (window.confirm('Really delete device '+id+'?') && post_call('api/device/delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 render(){
  if (this.state.data){
   const data = this.state.data
   const searchfield = this.state.searchfield.toLowerCase();
   const dev_list = (searchfield.length === 0) ? data : data.filter(row => (row.hostname.toLowerCase().includes(searchfield) || (row.ip && row.ip.includes(searchfield))));
   const thead = [<HeaderButton key='sort_ip' text='IP' highlight={(this.state.sort === 'ip')} onClick={() => this.sortList('ip')} />,<HeaderButton key='sort_hostname' text='Hostname' highlight={(this.state.sort === 'hostname')} onClick={() => this.sortList('hostname')} />,''];
   return <>
    <ContentList key='mcl' header='Device List' thead={thead} listItem={this.listItem} trows={dev_list}>
     <ReloadButton key='reload' onClick={() => this.componentDidMount()} />
     <ItemsButton key='items' onClick={() => { Object.assign(this.state,{rack_id:undefined,field:undefined,search:undefined}); this.componentDidMount(); }} title='List all items' />
     <AddButton key='add' onClick={() => this.changeContent(<New key='dn_new' ip='0.0.0.0' />)} title='Add device' />
     <SearchButton key='devices' onClick={() => this.changeContent(<Discover key='device_discover' />) } title='Discover new devices' />
     <SearchInput key='search' searchFire={(s) => this.setState({searchfield:s})} placeholder='Search devices' />
    </ContentList>
    <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
   </>
  } else
   return <Spinner />
 }
}

// ************** Info **************
//
export class Info extends Component {
 constructor(props){
  super(props)
  this.state = {data:undefined, found:true, content:null, navconf:false}
 }

 componentDidMount(){
  post_call('api/device/info',{id:this.props.id, extra:['types','classes']}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 changeSelf = (elem) => this.props.changeSelf(elem);

 updateInfo = () => post_call('api/device/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 reload = () => {
  this.setState({rack:undefined,vm:undefined});
  post_call('api/device/info',{id:this.props.id}).then(result => this.setState(result))
 }

 lookupInfo = () => {
  this.setState({content:<Spinner />,result:''})
  post_call('api/device/info',{id:this.props.id, op:'lookup'}).then(result => this.setState({...result,content:null}))
 }

 changeIpam = (id) => import('./ipam.jsx').then(lib => this.changeContent(<lib.AddressEvents key='address_events' id={id} changeSelf={this.changeContent} />))
 changeInterfaces = () => import('./interface.jsx').then(lib => this.changeContent(<lib.List key='interface_list' device_id={this.props.id} changeSelf={this.changeContent} />))
 changeVisualize = () => import('./visualize.jsx').then(lib => this.changeSelf(<lib.Edit key={'viz_id_' + this.props.id} type='device' changeSelf={this.changeSelf} id={this.props.id} />))

 render() {
  if(this.state.data){
   const data = this.state.data;
   const extra = this.state.extra;
   const vm = (data.class === 'vm' && this.state.vm) ? this.state.vm : false;
   const rack = (this.state.rack && data.class !== 'vm') ? this.state.rack : false;
   const change_self = (this.props.changeSelf);
   const has_ip = (extra.ip);
   const function_strings = (extra.functions.length >0) ? extra.functions.split(',') : [];
   const type = this.state.types.find(tp => tp.id === parseInt(data.type_id));
   return <>
    <InfoArticle key='di_ia' header='Device'>
     <InfoColumns key='ic_info' style={{float:'left'}}>
      <TextLine key='hostname' id='hostname' text={data.hostname} />
      <TextInput key='mac' id='mac' label='MAC' value={data.mac} title='System MAC' onChange={this.onChange} />
      {has_ip && <TextLine key='ip' id='ip' label='Mgmt IP' text={extra.ip} />}
      {has_ip && <StateLine key='state' id='state' state={extra.state} />}
     </InfoColumns>
     <InfoColumns key='ic_extra' style={{float:'left'}}>
      <SelectInput key='class' id='class' value={data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='type_id' id='type_id' label='Type' value={data.type_id} onChange={this.onChange}>{this.state.types.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <TextInput key='model' id='model' value={data.model} onChange={this.onChange} extra={data.model} />
      <TextLine key='version' id='version' text={data.version} />
      <TextInput key='serial' id='serial' label='S/N' value={data.serial} onChange={this.onChange} />
     </InfoColumns>
     <InfoColumns key='ic_rack' style={{float:'left'}}>
      {rack && <TextLine key='pos' id='rack_pos' label='Rack/Pos' text={`${rack.rack_name} (${rack.rack_unit})`} />}
      {rack && <TextLine key='size' id='rack_size' label='Size (U)' text={rack.rack_size} />}
      {rack && <TextLine key='con' id='rack_con' label='TS/Port' text={`${rack.console_name} (${rack.console_port})`} />}
      {rack && this.state.pems.map(pem => <TextLine key={pem.id} id={'pem_'+pem.id} label={pem.name+' PDU'} text={`${pem.pdu_name} (${pem.pdu_unit})`} />)}
     </InfoColumns>
     <InfoColumns key='ic_vm' style={{float:'left'}}>
      {vm && <TextLine key='name' id ='vm_name' label='VM Name' text={vm.name} />}
      {vm && <TextLine key='host' id ='vm_host' label='VM Host' text={vm.host} />}
      {vm && <TextLine key='uuid' id ='vm_uuid' label='VM UUID' text={vm.device_uuid} style={{maxWidth:170}} extra={vm.device_uuid} />}
      {vm && <TextLine key='uuhost' id ='vm_uuhost' label='Host UUID' text={vm.server_uuid} style={{maxWidth:170}} extra={vm.server_uuid} />}
     </InfoColumns>
     <InfoColumns key='ic_text' style={{clear:'both'}}>
      <TextInput key='comment' id='comment' value={data.comment} onChange={this.onChange} />
      <UrlInput key='url' id='url' label='URL' value={data.url} onChange={this.onChange} />
     </InfoColumns>
     <ReloadButton key='reload' onClick={() => this.reload()} />
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save' />
     <ConfigureButton key='edit' onClick={() => this.setState({navconf:!this.state.navconf})} title='Toggle config mode' />
     <StartButton key='cont' onClick={() => this.changeContent(<Control key='device_control' id={this.props.id} />)} title='Device control' />
     <CheckButton key='conf' onClick={() => this.changeContent(<Template key='device_configure' id={this.props.id} />)} title='Configuration template' />
     {change_self && <NetworkButton key='netw' onClick={() => this.changeVisualize()} title='Connectivity map' />}
     {has_ip && <SearchButton key='search' onClick={() => this.lookupInfo()} title='Information lookup' />}
     {has_ip && <LogButton key='logs' onClick={() => this.changeContent(<Logs key='device_logs' id={this.props.id} />)} title='Logs' />}
     {function_strings.includes('manage') && <GoButton key='manage' onClick={() => this.context.changeMain({module:this.state.extra.type_base,function:'Manage',args:{device_id:this.props.id, type:this.state.extra.type_name}})} title={'Manage ' + data.hostname} />}
     {has_ip && <TermButton key='ssh' onClick={() => window.open(`ssh://${extra.username}@${extra.ip}`,'_self')} title='SSH connection' />}
     {has_ip && <HealthButton key='health' onClick={() => this.changeIpam(this.state.extra.ipam_id)} title='IP health report' />}
     {rack && rack.console_url && <TermButton key='console' onClick={() => window.open(rack.console_url,'_self')} title='Serial Connection' /> }
     {data.url && <UiButton key='ui' onClick={() => window.open(data.url,'_blank')} title='Web UI' />}
     <Result key='result' result={JSON.stringify(this.state.update)} />
    </InfoArticle>
    <NavBar key='device_navigation' id='di_navigation'>
     {this.state.navconf && <NavButton key='management' title='Management' onClick={() => this.changeContent(<ManagementInfo key='device_configure' id={this.props.id} />)} />}
     {!this.state.navconf && <NavButton key='interfaces' title='Interfaces' onClick={() => this.changeInterfaces()} />}
     {!this.state.navconf && <NavButton key='stats' title='Statistics' onClick={() => this.changeContent(<StatisticsList key='statistics_list' device_id={this.props.id} changeSelf={this.changeContent} />)} />}
     {!this.state.navconf && type.base === 'network' && has_ip && <NavButton key='fdb' title='FDB' onClick={() => this.changeContent(<FdbDevice key='fdb_device' id={this.props.id} ip={extra.ip} type={type.name} changeSelf={this.changeContent} />)} />}
     {this.state.navconf && ['infrastructure','out-of-band'].includes(data.class) && <NavButton key='rack' title='Rack' onClick={() => this.changeContent(<RackInfo key='device_rack_info' device_id={this.props.id} />)} />}
     {this.state.navconf && ['device','infrastructure','out-of-band'].includes(data.class) && <NavButton key='pems' title='PEMs' onClick={() => this.changeContent(<PemList key='device_pem_list' device_id={this.props.id} changeSelf={this.changeContent} />)} />}
     {!this.state.navconf && function_strings.filter(fun => fun !== 'manage').map((op,idx) => <NavButton key={'nav_'+idx} title={op.replace('_',' ')} onClick={() => this.changeContent(<Function key={'dev_func_'+op} id={this.props.id} op={op} type={this.state.extra.type_name} />)} />)}
    </NavBar>
    {this.state.content}
   </>
  } else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// ************* Configure *************
//
class ManagementInfo extends Component {
 constructor(props){
  super(props)
  this.state = {data:undefined, found:true, content:null}
 }

 componentDidMount(){
  post_call('api/device/extended',{id:this.props.id, extra:['domains']}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => post_call('api/device/extended',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (this.state.data && this.state.domains)
   return <InfoArticle key='d_conf_art' header='Management Configuration'>
    <InfoColumns key='d_conf_ic'>
     <TextInput key='d_conf_hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
     <SelectInput key='d_conf_a_domain_id' id='a_domain_id' label='Host Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
     <SelectInput key='d_conf_ipam_id' id='ipam_id' label='Mgmt IP' value={this.state.data.ipam_id} onChange={this.onChange}>{this.state.interfaces.map((row,idx) => <option key={idx} value={row.ipam_id}>{`${row.ip} (${row.name})`}</option>)}</SelectInput>
     <TextLine key='id' id='id' label='Local ID'  text={this.props.id} title='Database ID' />
     <TextLine key='snmp' id='snmp' label='SNMP' text={this.state.data.snmp} />
     <TextLine key='d_conf_oid' id='oid' label='Priv OID' text={this.state.extra.oid} />
     <TextLine key='d_conf_oui' id='oui' label='System OUI' text={this.state.extra.oui} />
    </InfoColumns>
    <SaveButton key='d_conf_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='d_conf_result' result={this.state.status} />
   </InfoArticle>
  else
   return <Spinner />
 }
}

// ************* RackInfo **************
//
class RackInfo extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/rack',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => post_call('api/device/rack',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data){
   const racked = (this.state.data.rack_id && this.state.data.rack_id !== 'NULL');
   return <InfoArticle key='d_rack_art' header='Rack'>
    <InfoColumns key='d_rack_ic'>
     <SelectInput key='d_rack_id' id='rack_id' label='Rack ID' value={this.state.data.rack_id} onChange={this.onChange}>{this.state.racks.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
     {racked && <TextInput key='d_rack_size' id='rack_size' label='Size' value={this.state.data.rack_size} onChange={this.onChange} title='Size of device in U' />}
     {racked && <TextInput key='d_rack_unit' id='rack_unit' label='Unit' value={this.state.data.rack_unit} onChange={this.onChange} title='First unit of placement' />}
     {racked && <SelectInput key='d_rack_con_id' id='console_id' label='Console' value={this.state.data.console_id} onChange={this.onChange}>{this.state.consoles.map((row,idx) => <option key={idx} value={row.id}>{row.hostname}</option>)}</SelectInput>}
     {racked && <TextInput key='d_rack_con_port' id='console_port' label='Console Port' value={this.state.data.console_port} onChange={this.onChange} />}
    </InfoColumns>
    <SaveButton key='d_rack_btn_save' onClick={() => this.updateInfo()} title='Save' />
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* PEMs **************
//
class PemList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/pem/list',{device_id:this.props.device_id,lookup:true}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem)

 deleteList = (id) => (window.confirm('Really delete PEM?') && post_call('api/pem/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 listItem = (row) => [row.id,row.name,row.pdu_id,row.pdu_name,row.pdu_slot,row.pdu_unit,<>
  <InfoButton key='info' onClick={() => this.changeContent(<PemInfo key={'pem_info_'+row.id} id={row.id} device_id={this.props.device_id} changeSelf={this.changeContent} />)} title='Edit PEM information' />
  <DeleteButton key='del' onClick={() => this.deleteList(row.id) } title='Delete PEM' />
 </>]

 render(){
  return (this.state.data) ? <ContentReport key='pems' header='PEMs' thead={['ID','Name','PDU ID','PDU Name','PDU Slot','PDU Unit','']} trows={this.state.data} listItem={this.listItem}>
   <ReloadButton key='pems_btn_reload' onClick={() => this.componentDidMount()} />
   <AddButton key='pems_btn_add' onClick={() => this.changeContent(<PemInfo key='pem_new' id='new' device_id={this.props.device_id} changeSelf={this.changeContent} />)} title='Add PEM' />
  </ContentReport>
  : <Spinner />
 }
}

// ************* PemInfo **************
//
class PemInfo extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/pem/info',{id:this.props.id, device_id:this.props.device_id}).then(result => this.setState(result))
  post_call('api/pdu/list',{device_id:this.props.device_id, empty:true}).then(result => this.setState({pdus:result.data}))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => post_call('api/pem/info',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data && this.state.pdus){
   const pdu_info = this.state.pdus.find(pdu => parseInt(pdu.device_id) === parseInt(this.state.data.pdu_id));
   let slots = []
   if (pdu_info){
    for (let i = 0; i < pdu_info.slots; i++)
     slots.push({id:i,name:pdu_info[`${i}_slot_name`]});
   }
   return <InfoArticle key='d_pem_art' header='PEM'>
    <InfoColumns key='d_pem_ic'>
     <TextInput key='d_pem_name' id='name' value={this.state.data.name} onChange={this.onChange} />
     <SelectInput key='d_pem_pdu_id' id='pdu_id' label='PDU' value={this.state.data.pdu_id} onChange={this.onChange}>{this.state.pdus.map((row,idx) => <option key={idx} value={row.device_id}>{row.name}</option>)}</SelectInput>
     <SelectInput key='d_pem_pdu_slot' id='pdu_slot' label='Slot' value={this.state.data.pdu_slot} onChange={this.onChange}>{slots.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
     <TextInput key='d_pem_pdu_unit' id='pdu_unit' label='Unit' value={this.state.data.pdu_unit} onChange={this.onChange} />
    </InfoColumns>
    <BackButton key='d_pem_btn_back' onClick={() => this.props.changeSelf(<PemList key='device_pem_list' device_id={this.props.device_id} changeSelf={this.props.changeSelf} />)} />
    <SaveButton key='d_pem_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='d_pem_result' result={(this.state.update) ? (this.state.result) ? JSON.stringify(this.state.result) :JSON.stringify(this.state.update) : ''} />
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* StatisticsList **************
//
class StatisticsList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  this.loadList()
 }

 loadList = (clear) => post_call('api/statistics/list',{device_id:this.props.device_id}).then(result => this.setState((clear)? {...result,result:'',inserts:''} : result));

 changeContent = (elem) => this.props.changeSelf(elem)

 deleteList = (id) => (window.confirm('Really delete statistics point?') && post_call('api/statistics/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 lookupStats = () => post_call('api/statistics/lookup',{device_id:this.props.device_id}).then(result => { this.setState(result); this.loadList()} )

 listItem = (row) => [row.id,row.measurement,row.tags,row.name,row.oid,<>
  <InfoButton key='info' onClick={() => this.changeContent(<StatisticsInfo key={'statistics_info_'+row.id} id={row.id} device_id={this.props.device_id} />)} title='Edit data point' />
  {row.measurement && row.name && <HealthButton key='stats' onClick={() => this.changeContent(<Statistics key={row.id} device_id={this.props.device_id} measurement={row.measurement} name={row.name} />)} title='Stats for data point' />}
  <DeleteButton key='del' onClick={() => this.deleteList(row.id) } title='Delete data point' />
 </>]

 render(){
  return (this.state.data) ? <ContentReport key='cr_stats' header='Device statistics' thead={['ID','Measurement','Tags','Name','OID','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <ReloadButton key='reload' onClick={() => this.loadList(true)} />
   <SearchButton key='lookup' onClick={() => this.lookupStats()} title='Lookup device type stats' />
   <AddButton key='add' onClick={() => this.changeContent(<StatisticsInfo key={'stats_new_'} id='new' device_id={this.props.device_id} />)} title='Add statistics' />
  </ContentReport>
  : <Spinner />
 }
}


// *************** Statistics ****************
//
class Statistics extends Component {
 constructor(props){
  super(props)
  this.state = {range:1}
  this.canvas = React.createRef()
  this.graph = null;
  this.vis = null;
 }

 componentDidMount(){
  import('vis-timeline/standalone/esm/vis-timeline-graph2d').then(vis => {
   this.vis = vis;
   const options = { locale:'en', width:'100%', height:'100%', zoomMin:60000, zoomMax:1209600000, clickToUse:true, drawPoints: false, interpolation:false, legend:true, dataAxis:{ alignZeros:false , icons: true, left:{ title:{ text:'value' } } } };
   const groups = new this.vis.DataSet([{id:'data', content:this.props.name}]);
   this.graph = new this.vis.Graph2d(this.canvas.current, [], groups, options);
   this.updateItems(this.state.range);
  })
 }

 updateItems = (range) => post_call('api/statistics/query_device',{device_id:this.props.device_id, measurement:this.props.measurement, name:this.props.name, range:range}).then(result => {
  const dataset = new this.vis.DataSet(result.data.flatMap(({time, value}) => [{x:new Date(time*1000), y:value, group:'data'}]));
  this.graph.setItems(dataset);
  this.graph.fit();
 });

 rangeChange = (e) => {
  this.setState({[e.target.name]:e.target.value})
  this.updateItems(e.target.value);
 }

 gotoNow = () => {
  const today = new Date()
  this.graph.moveTo(today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate()+' '+today.getHours()+':'+today.getMinutes());
 }

 render(){
  return <Article key='ds_art' header='Statistics'>
   <ReloadButton key='reload' onClick={() => this.updateItems(this.state.range)} title='Reload' />
   <RevertButton key='reset' onClick={() => this.gotoNow()} title='Go to now' />
   <br />
   <TextLine key='name' id='name' label='Device Data Point' text={this.props.name} />
   <br />
   <SelectInput key='range' id='range' label='Time range' value={this.state.range} onChange={this.rangeChange}>
    <option value='1'>1h</option>
    <option value='4'>4h</option>
    <option value='8'>8h</option>
    <option value='24'>24h</option>
   </SelectInput>
   <div className={styles.graphs} ref={this.canvas} />
  </Article>
 }
}

// ************* PemInfo **************
//
class StatisticsInfo extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/statistics/info',{id:this.props.id, device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => post_call('api/statistics/info',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data){
   return <InfoArticle key='d_stat_art' header='Data point'>
    <InfoColumns key='d_stat_ic'>
     <TextInput key='d_stat_measurement' id='measurement' value={this.state.data.measurement} onChange={this.onChange} title='Group, or measurement, that the data point belongs to' />
     <TextInput key='d_stat_tags' id='tags' value={this.state.data.tags} onChange={this.onChange} title='Tags are comma separated values that extend TSDB grouping' />
     <TextInput key='d_stat_name' id='name' value={this.state.data.name} onChange={this.onChange} title='Data point name' />
     <TextInput key='d_stat_oid' id='oid' value={this.state.data.oid} onChange={this.onChange} />
    </InfoColumns>
    <SaveButton key='d_stat_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='d_stat_result' result={(this.state.update) ? (this.state.result) ? JSON.stringify(this.state.result) :JSON.stringify(this.state.update) : JSON.stringify(this.state.update)} />
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* Control **************
//
class Control extends Component {
 constructor(props){
  super(props)
  this.state = {pems:[]}
 }

 componentDidMount(){
  post_call('api/device/control',{id:this.props.id}).then(result => this.setState(result));
 }

 operationDev = (op,msg) => {
  if (window.confirm(msg)){
   this.setState({wait:<Spinner />});
   post_call('api/device/control',{id:this.props.id, device_op:op}).then(result => this.setState({...result,wait:null}))
  }
 }

 operationPem = (id,op,msg) => {
  if (window.confirm(msg)){
   this.setState({wait:<Spinner />});
   post_call('api/device/control',{id:this.props.id, pem_op:op, pem_id:id}).then(result => this.setState({...result,wait:null}))
  }
 }

 lookupState = (id) => console.log('State lookup TODO');

 render() {
  return (
   <InfoArticle key='ia_dc' header='Device Control'>
    <InfoColumns key='ic'>
     <label htmlFor='reboot'>Reboot:</label><ReloadButton id='reboot' key='reboot' onClick={() => this.operationDev('reboot','Really reboot?')} title='Restart device' />
     <label htmlFor='shutdown'>Shutdown:</label><ShutdownButton id='shutdown' key='shutdown' onClick={() => this.operationDev('shutdown','Really shutdown?')} title='Shutdown' />
     {this.state.pems.map(pem => {
      if(pem.state === 'off')
       return <Fragment key={pem.id}><label htmlFor={pem.id}>{pem.name}:</label><StartButton key={'dc_btn_start_'+pem.id} id={pem.id} onClick={() => this.operationPem(pem.id,'on','Power on PEM?')} title='Power ON' /></Fragment>
      else if (pem.state === 'on')
       return <Fragment key={pem.id}><label htmlFor={pem.id}>{pem.name}:</label><ShutdownButton key={'dc_btn_stop_'+pem.id} id={pem.id} onClick={() => this.operationPem(pem.id,'off','Power off PEM?')} title='Power OFF' /></Fragment>
      else
       return <Fragment key={pem.id}><label htmlFor={pem.id}>{pem.name}:</label><SearchButton key={'dc_btn_lookup_'+pem.id} id={pem.id} onClick={() => this.lookupState(pem.id)} title='Lookup State' /></Fragment>
     })}
    </InfoColumns>
    <Result key='result' result={JSON.stringify(this.state.result)} />
    {this.state.wait}
   </InfoArticle>)
 }
}

// ************** Logs **************
//
export class Logs extends Component {
 componentDidMount(){
  post_call('api/device/log_get',{id:this.props.id}).then(result => this.setState(result));
 }

 clearLog = () => post_call('api/device/log_clear',{id:this.props.id}).then(result => (result.deleted && this.setState({data:[]})));

 render() {
  return (!this.state) ? <Spinner /> : <ContentReport key='dev_log_cr' header='Devices' thead={['Time','Message']} trows={this.state.data} listItem={(row) => [row.time,row.message]}>
   <DeleteButton key='devlog_btn_delete' onClick={() => this.clearLog()} title='Clear device logs' />
  </ContentReport>
 }
}

// ******** Template *********
//
class Template extends Component {
 componentDidMount(){
  post_call('api/device/configuration_template',{id:this.props.id}).then(result => this.setState(result));
 }

 render() {
  return (!this.state) ? <Spinner /> : <CodeArticle key='dtemp_art'>{(this.state.status === 'OK') ? this.state.data.join('\n') : this.state.info}</CodeArticle>
 }
}

// ************** New **************
//
export class New extends Component {
 constructor(props){
  super(props)
  this.state = {data:{ip:this.props.ip,mac:'00:00:00:00:00:00',class:'device',ipam_network_id:this.props.ipam_network_id,hostname:''}, found:true}
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 componentDidMount(){
  post_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}))
  post_call('api/ipam/network_list').then(result => this.setState({networks:result.data}))
  post_call('api/device/class_list').then(result => this.setState({classes:result.data}))
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.setState({data:{ip:this.props.ip,mac:'00:00:00:00:00:00',class:'device',ipam_network_id:this.props.ipam_network_id,hostname:''}})
 }

 addDevice = () => {
  if (this.state.data.hostname)
   post_call('api/device/new',this.state.data).then(result => this.setState({result:JSON.stringify(result)}))
 }

 searchIP = () => {
  if (this.state.data.ipam_network_id)
   post_call('api/ipam/address_find',{network_id:this.state.data.ipam_network_id}).then(result => this.setState({data:{...this.state.data, ip:result.ip}}))
 }

 render() {
  if (!this.state.domains || !this.state.classes || !this.state.networks)
   return <Spinner />
  else
   return (
    <InfoArticle key='dn_art' header='Device Add'>
     <InfoColumns key='dn_content'>
      <TextInput key='dn_hostname' id='hostname' value={this.state.data.hostname} placeholder='Device hostname' onChange={this.onChange} />
      <SelectInput key='dn_class' id='class' label='Device Class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='dn_a_domain_id' id='a_domain_id' label='Host Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <SelectInput key='dn_if_domain_id' id='if_domain_id' label='Interface Domain' value={this.state.data.if_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <SelectInput key='dn_ipam_network_id' id='ipam_network_id' label='Interface Network' value={this.state.data.ipam_network_id} onChange={this.onChange}>{this.state.networks.map((row,idx) => <option key={idx} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
      <TextInput key='dn_ip' id='ip' label='IP' value={this.state.data.ip} onChange={this.onChange} />
      <TextInput key='dn_mac' id='mac' label='MAC' value={this.state.data.mac} onChange={this.onChange} />
     </InfoColumns>
     <StartButton key='dn_btn_start' onClick={() => this.addDevice()} title='Add device' />
     <SearchButton key='dn_btn_search' onClick={() => this.searchIP()} title='Find available IP' />
     <Result key='dn_result' result={this.state.result} />
    </InfoArticle>
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
  post_call('api/ipam/network_list').then(result => this.setState({networks:result.data}))
  post_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}))
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 changeContent = (elem) => this.setState({content:elem})

 runDiscovery(){
  this.setState({content:<Spinner />})
  post_call('api/device/discover',{network_id:this.state.ipam_network_id, a_domain_id:this.state.a_domain_id,if_domain_id:this.state.if_domain_id}).then(result => this.setState({content:<CodeArticle key='dd_result'>{JSON.stringify(result,null,2)}</CodeArticle>}))
 }

 render() {
  if (this.state.networks && this.state.domains){
   return <>
     <InfoArticle key='ia_dd' header='Device Discovery'>
      <InfoColumns key='ic'>
       <SelectInput key='ipam_network_id' id='ipam_network_id' label='Network' value={this.state.ipam_network_id} onChange={this.onChange}>{this.state.networks.map((row,idx) => <option key={idx} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
       <SelectInput key='a_domain_id' id='a_domain_id' label='Host Domain' value={this.state.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
       <SelectInput key='if_domain_id' id='if_domain_id' label='Interface Domain' value={this.state.if_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
      </InfoColumns>
      <StartButton key='start' onClick={() => this.runDiscovery()} title='Start discovery' />
     </InfoArticle>
     <NavBar key='dd_navigation' id='dd_navigation' />
     {this.state.content}
    </>
  } else
   return <Spinner />
 }
}

// ************** Report **************
//
export class Report extends Component {
 componentDidMount(){
  post_call('api/device/list', { extra:['system','mac','type','oui','class']}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.hostname,row.class,row.ip,row.mac,row.oui,row.type_name,row.oid,row.serial,<StateLeds key={'dr_'+row.id} state={row.state} />]

 render(){
  return (!this.state) ? <Spinner /> : <ContentReport key='dev_cr' header='Devices' thead={['ID','Hostname','Class','IP','MAC','OUI','Type','OID','Serial','State']} trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** Type List **************
//
class TypeList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/type_list').then(result => this.setState(result))
 }

 changeSelf = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [row.base,<HrefButton key={'tl_btn_' + row.name} text={row.name} onClick={() => this.changeSelf(<List key='device_list' field='type' search={row.name} />)} />,row.icon]

 render(){
  return (this.state.data) ? <>
   <ContentList key='cl' header='Device Types' thead={['Class','Name','Icon']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </> : <Spinner />
 }
}

// ************** Model List **************
//
class ModelList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/model_list').then(result => this.setState({...result,result:'OK'}))
 }

 syncModels = () => post_call('api/device/model_list',{op:'sync'}).then(result => this.setState(result))

 listItem = (row) => [row.id,row.name,row.type,<>
  <ConfigureButton key='info' onClick={() => this.changeContent(<ModelInfo key={'model_info_'+row.id} id={row.id} />)} title='Edit model information' />
  <DeleteButton key='del' onClick={() => this.deleteList(row.id) } title='Delete model' />
 </>]

 deleteList = (id) => (window.confirm('Really delete model?') && post_call('api/device/model_delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 render(){
  return (this.state.data) ? <>
   <ContentList key='cl' header='Device Models' thead={['ID','Model','Type','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount()} />
    <SyncButton key='sync' onClick={() => this.syncModels() } title='Resync models' />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </> : <Spinner />
 }
}

// ************** Model Info **************
//
export class ModelInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = () =>  post_call('api/device/model_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  post_call('api/device/model_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return <InfoArticle key='dm_art' header='Device Model'>
    <InfoColumns key='dm_content'>
     <TextLine key='dm_name' id='name' text={this.state.data.name} />
     <TextLine key='dm_type' id='type' text={this.state.extra.type} />
     <TextInput key='dm_defaults_file' id='defaults_file' label='Default File' value={this.state.data.defaults_file} onChange={this.onChange} />
     <TextInput key='dm_image_file' id='image_file' label='Image  File' value={this.state.data.image_file} onChange={this.onChange} />
    </InfoColumns>
    <TextAreaInput key='dm_parameters'  id='parameters' onChange={this.onChange} value={this.state.data.parameters} />
    <SaveButton key='dm_btn_save' onClick={() => this.updateInfo()} title='Save' />
   </InfoArticle>
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

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 ouiSearch = () => {
  post_call('api/master/oui_info',{oui:this.state.data.oui}).then(result => this.setState({content:<InfoArticle key='os_art'><InfoColumns key='os_cont'><label htmlFor='oui'>OUI:</label><span id='oui'>{result.data.oui}</span><label htmlFor='company'>Company:</label><span id='company'>{result.data.company}</span></InfoColumns></InfoArticle>}))
 }

 render() {
  return <Flex key='flex'>
   <LineArticle key='os_art'>
    Type MAC address to find <TextInput key='oui' id='oui' onChange={this.onChange} value={this.state.data.oui} placeholder='00:00:00' />
    <SearchButton key='os_btn_search' onClick={() => this.ouiSearch()} title='Search for OUI' />
   </LineArticle>
   {this.state.content}
  </Flex>
 }
}

// ************** OUI List **************
//
class OUIList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/master/oui_list').then(result => this.setState(result))
 }

 render(){
   return (this.state.data) ? <ContentReport key='oui_list_cr' header='OUI' thead={['oui','company']} trows={this.state.data} listItem={(row)=> [`${row.oui.substring(0,2)}:${row.oui.substring(2,4)}:${row.oui.substring(4,6)}`,row.company]} /> : <Spinner />
 }
}

// ************** Function **************
//
class Function extends Component {
 componentDidMount(){
  post_call('api/device/function',{op:this.props.op, id:this.props.id, type:this.props.type}).then(result => this.setState(result))
 }

 render() {
  if (!this.state)
   return <Spinner />
  else if (this.state.status === 'OK'){
   if(this.state.data.length > 0){
    const head = Object.keys(this.state.data[0]);
    return <ContentReport key='df_cr' thead={head} trows={this.state.data} listItem={(row) => head.map(hd => row[hd])} />
   } else
    return <InfoArticle key='df_art'>No Data</InfoArticle>
  } else
   return <CodeArticle key='df_art'>Error in devdata: {this.state.info}</CodeArticle>
 }
}
