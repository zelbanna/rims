import React, { Component, Fragment } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, StateMap, SearchField, InfoColumns, RimsContext, Result, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton, NavReload } from './infra/Navigation.jsx'
import { TextInput, TextLine, StateLine, SelectInput, UrlInput } from './infra/Inputs.jsx';
import { AddButton, CheckButton, ConfigureButton, ConnectionButton, DeleteButton, DevicesButton, GoButton, HeaderButton, HrefButton, InfoButton, ItemsButton, LogButton, NetworkButton, ReloadButton, SaveButton, SearchButton, ShutdownButton, StartButton, SyncButton, TermButton, UiButton } from './infra/Buttons.jsx';

import { List as VisualizeList, Edit as VisualizeEdit } from './visualize.jsx';

// **************** Main ****************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  if (this.props.rack_id)
   rest_call('api/rack/inventory',{id:this.props.rack_id}).then(result => this.compileNavItems({rack_id:this.props.rack_id, ...result}))
  else
   this.compileNavItems({pdu:[], console:[], name:'N/A', rack_id:undefined});
 }

 changeImport(module,func,args){
  import('./'+module+'.jsx').then(lib => {
   var Elem = lib[func];
   this.setState({content:<Elem key={module+'_'+func} {...args} />})
  })
 }

 compileNavItems = (state) => {
  this.context.loadNavigation(<NavBar key='device_navbar'>
   <NavDropDown key='dev_nav_devs' title='Devices'>
    <NavDropButton key='dev_nav_list' title='List' onClick={() => this.changeContent(<List key='dl' rack_id={state.rack_id} />)} />
    <NavDropButton key='dev_nav_srch' title='Search' onClick={() => this.changeContent(<Search key='ds' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_types' title='Types' onClick={() => this.changeContent(<TypeList key='dtl' changeSelf={this.changeContent} />)} />
    <NavDropButton key='dev_nav_model' title='Models' onClick={() => this.changeContent(<ModelList key='dml' />)} />
   </NavDropDown>
   <NavButton key='dev_nav_maps' title='Maps' onClick={() => this.changeContent(<VisualizeList key='visualize_list' />)} />
   {(state.pdu.length > 0) && <NavDropDown key='dev_nav_pdus' title='PDUs'>{state.pdu.map((row,idx) => <NavDropButton key={'dev_nav_pdu_' + idx} title={row.hostname} onClick={() => this.changeImport('pdu','Inventory',{device_id:row.id,type:row.type})} />)}</NavDropDown>}
   {(state.console.length > 0) && <NavDropDown key='dev_nav_consoles' title='Consoles'>{state.console.map((row,idx) => <NavDropButton key={'dev_nav_console_' + idx} title={row.hostname} onClick={() => this.changeImport('console','Inventory',{device_id:row.id,type:row.type})} />)}</NavDropDown>}
   {(state.rack_id) && <NavButton key='dev_nav_rack' title={state.name} onClick={() => this.changeImport('rack','Layout',{id:state.rack_id})} />}
   <NavDropDown key='dev_nav_oui' title='OUI'>
    <NavDropButton key='dev_nav_ouis' title='Search' onClick={() => this.changeContent(<OUISearch key='oui_search' />)} />
    <NavDropButton key='dev_nav_ouil' title='List' onClick={() => this.changeContent(<OUIList key='oui_list' />)} />
   </NavDropDown>
   <NavButton key='dev_nav_resv' title='Reservations' onClick={() => this.changeImport('reservation','List',{})} style={{float:'right'}} />
   <NavDropDown key='dev_nav_ipam' title='IPAM' style={{float:'right'}}>
    <NavDropButton key='dev_nav_isrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'DHCP'})} />
    <NavDropButton key='dev_nav_nets' title='Networks' onClick={() => this.changeImport('ipam','NetworkList',{})} />
   </NavDropDown>
   <NavDropDown key='dev_nav_dns' title='DNS' style={{float:'right'}}>
    <NavDropButton key='dev_nav_dsrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'DNS'})} />
    <NavDropButton key='dev_nav_doms' title='Domains' onClick={() => this.changeImport('dns','DomainList',{})} />
   </NavDropDown>
   <NavReload key='dev_nav_reload' onClick={() => this.changeContent(null)} />
  </NavBar>)
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return  <Fragment key='main_base'>{this.state.content}</Fragment>
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
  return (
   <article className='lineinput'>
    <h1>Device Search</h1>
    <div>
     <SelectInput key='field' id='field' onChange={this.onChange} value={this.state.field}>
      <optgroup label='Group'>
       <option value='hostname'>Hostname</option>
       <option value='type'>Type</option>
      </optgroup>
      <optgroup label='Unique'>
       <option value='id'>ID</option>
       <option value='ip'>IP</option>
       <option value='mac'>MAC</option>
       <option value='ipam_id'>IPAM ID</option>
      </optgroup>
     </SelectInput>
     <TextInput key='search' id='search' onChange={this.onChange} value={this.state.search} placeholder='search' />
    </div>
    <SearchButton key='ds_btn_search' onClick={() => this.changeContent(<List key='device_list' {...this.state} />)} title='Search devices' />
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
    if (a.ip && b.ip){
     const num1 = Number(a.ip.split('.').map(num => (`000${num}`).slice(-3) ).join(''));
     const num2 = Number(b.ip.split('.').map(num => (`000${num}`).slice(-3) ).join(''));
     return num1-num2;
   } else if (a.ip)
    return 1;
   else
    return a.hostname.localeCompare(b.hostname)
   });
  this.setState({sort:method})
 }

 listItem = (row) => [row.ip,<HrefButton key={'dl_btn_info_'+row.id} text={row.hostname} onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title={row.id} />,StateMap({state:row.state}),<Fragment key={'dl_buttons_'+row.id}>
  <InfoButton key={'dl_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title={row.id} />
  <DeleteButton key={'dl_btn_del_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete device' />
 </Fragment>]

 deleteList = (id) => (window.confirm('Really delete device '+id+'?') && rest_call('api/device/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  if (this.state.data){
   let device_list = this.state.data.filter(row => row.hostname.includes(this.state.searchfield));
   const thead = [<HeaderButton key='dl_btn_ip' text='IP' highlight={(this.state.sort === 'ip')} onClick={() => this.sortList('ip')} />,<HeaderButton key='dl_btn_hostname' text='Hostname' highlight={(this.state.sort === 'hostname')} onClick={() => this.sortList('hostname')} />,'',''];
   return <Fragment key={'dl_fragment'}>
    <ContentList key='dl_list' header='Device List' thead={thead} listItem={this.listItem} trows={device_list}>
     <ReloadButton key='dl_btn_reload' onClick={() => this.componentDidMount()} />
     <ItemsButton key='dl_btn_items' onClick={() => { Object.assign(this.state,{rack_id:undefined,field:undefined,search:undefined}); this.componentDidMount(); }} title='List all items' />
     <AddButton key='dl_btn_add' onClick={() => this.changeContent(<New key={'dn_new_' + rnd()} id='new' />)} title='Add device' />
     <DevicesButton key='dl_btn_devices' onClick={() => this.changeContent(<Discover key='dd' />) } title='Discover devices' />
     <SearchField key='dl_searchfield' searchHandler={this.searchHandler} value={this.state.searchfield} placeholder='Search devices' />
    </ContentList>
    <ContentData key='dl_content'>{this.state.content}</ContentData>
   </Fragment>
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
  rest_call('api/device/info',{id:this.props.id, extra:['types','classes']}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 changeSelf = (elem) => this.props.changeSelf(elem);

 updateInfo = () => rest_call('api/device/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 reload = () => {
  this.setState({rack:undefined,vm:undefined});
  rest_call('api/device/info',{id:this.props.id}).then(result => this.setState(result))
 }

 lookupInfo = () => {
  this.setState({content:<Spinner />,result:''})
  rest_call('api/device/info',{id:this.props.id, op:'lookup'}).then(result => this.setState({...result,content:null}))
 }

 changeInterfaces = () => import('./interface.jsx').then(lib => this.changeContent(<lib.List key='interface_list' device_id={this.props.id} changeSelf={this.changeContent} />))

 render() {
  if(this.state.data){
   const data = this.state.data;
   const extra = this.state.extra;
   const vm = (data.class === 'vm' && this.state.vm) ? this.state.vm : false;
   const rack = (this.state.rack && data.class !== 'vm') ? this.state.rack : false;
   const change_self = (this.props.changeSelf);
   const has_ip = (extra.interface_ip);
   const function_strings = (extra.functions.length >0) ? extra.functions.split(',') : [];
   return (
    <Fragment key='di_fragment'>
     <article className='info'>
     <h1>Device</h1>
     <InfoColumns key='di_info' className='left'>
      <TextLine key='hostname' id='hostname' text={data.hostname} />
      <TextInput key='mac' id='mac' label='Sys Mac' value={data.mac} title='System MAC' onChange={this.onChange} />
      <TextLine key='if_mac' id='if_mac' label='Mgmt MAC' text={extra.interface_mac} title='Management Interface MAC' />
      <TextLine key='if_ip' id='if_ip' label='Mgmt IP' text={extra.interface_ip} />
      <TextLine key='snmp' id='snmp' label='SNMP' text={data.snmp} />
      <StateLine key='state' id='state' state={[extra.if_state,extra.ip_state]} />
     </InfoColumns>
     <InfoColumns key='di_extra' className='left'>
      <TextLine key='id' id='id' text={this.props.id} />
      <SelectInput key='class' id='class' value={data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={'di_class_'+row} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='type_id' id='type_id' label='Type' value={data.type_id} onChange={this.onChange}>{this.state.types.map((row,idx) => <option key={'di_type_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <TextInput key='model' id='model' value={data.model} onChange={this.onChange} extra={data.model} />
      <TextLine key='version' id='version' text={data.version} onChange={this.onChange} />
      <TextInput key='serial' id='serial' label='S/N' value={data.serial} onChange={this.onChange} />
     </InfoColumns>
     <InfoColumns key='di_rack' className='left'>
      {rack && <TextLine key='rack_pos' id='rack_pos' label='Rack/Pos' text={`${rack.rack_name} (${rack.rack_unit})`} />}
      {rack && <TextLine key='rack_size' id='rack_size' label='Size (U)' text={rack.rack_size} />}
      {rack && <TextLine key='rack_con' id='rack_con' label='TS/Port' text={`${rack.console_name} (${rack.console_port})`} />}
      {rack && this.state.pems.map(pem => <TextLine key={'pem_'+pem.id} id={'pem_'+pem.id} label={pem.name+' PDU'} text={`${pem.pdu_name} (${pem.pdu_unit})`} />)}
     </InfoColumns>
     <InfoColumns key='di_vm' className='left'>
      {vm && <TextLine key='vm_name' id ='vm_name' label='VM Name' text={vm.name} />}
      {vm && <TextLine key='vm_host' id ='vm_host' label='VM Host' text={vm.host} />}
      {vm && <TextLine key='vm_uuid' id ='vm_uuid' label='VM UUID' text={vm.device_uuid} style={{maxWidth:170}} extra={vm.device_uuid} />}
      {vm && <TextLine key='vm_uuhost' id ='vm_uuhost' label='Host UUID' text={vm.server_uuid} style={{maxWidth:170}} extra={vm.server_uuid} />}
     </InfoColumns>
     <br />
     <InfoColumns key='di_text'>
      <TextInput key='comment' id='comment' value={data.comment} onChange={this.onChange} />
      <UrlInput key='url' id='url' label='URL' value={data.url} onChange={this.onChange} />
     </InfoColumns>
     <br />
     <ReloadButton key='di_btn_reload' onClick={() => this.reload()} />
     <SaveButton key='di_btn_save' onClick={() => this.updateInfo()} title='Save' />
     <ConnectionButton key='di_btn_conn' onClick={() => this.changeInterfaces()} title='Interfaces' />
     <StartButton key='di_btn_cont' onClick={() => this.changeContent(<Control key='device_control' id={this.props.id} />)} title='Device control' />
     <CheckButton key='di_btn_conf' onClick={() => this.changeContent(<Template key='device_configure' id={this.props.id} />)} title='Configuration template' />
     <ConfigureButton key='di_btn_edit' onClick={() => this.setState({navconf:!this.state.navconf})} title='Toggle config mode' />
     {change_self && <NetworkButton key='di_btn_netw' onClick={() => this.changeSelf(<VisualizeEdit key={'ve_'+this.props.id} type='device' id={this.props.id} changeSelf={this.props.changeSelf} />)} title='Connectivity map' />}
     {has_ip && <SearchButton key='di_btn_srch' onClick={() => this.lookupInfo()} title='Information lookup' />}
     {has_ip && <LogButton key='di_btn_logs' onClick={() => this.changeContent(<Logs key='device_logs' id={this.props.id} />)} title='Logs' />}
     {function_strings.includes('manage') && <GoButton key='d_btn_manage' onClick={() => this.context.changeMain({module:this.state.extra.type_base,function:'Manage',args:{device_id:this.props.id, type:this.state.extra.type_name}})} title={'Manage ' + data.hostname} />}
     {has_ip && <TermButton key='di_btn_ssh' onClick={() => { const sshWin = window.open(`ssh://${extra.username}@${extra.interface_ip}`,'_blank'); sshWin.close(); }} title='SSH connection' />}
     {rack && rack.console_url && <TermButton key='di_btn_console' onClick={() => { const termWin = window.open(rack.console_url,'_blank'); termWin.close(); }} title='Serial Connection' /> }
     {data.url && <UiButton key='di_btn_ui' onClick={() => window.open(data.url,'_blank')} title='Web UI' />}
     <Result key='dev_result' result={JSON.stringify(this.state.update)} />
    </article>
    <NavBar key='di_navigation' id='di_navigation'>
     {this.state.navconf && <NavButton key='di_nav_management' title='Management' onClick={() => this.changeContent(<ManagementInfo key='device_configure' id={this.props.id} />)} />}
     {this.state.navconf && ['infrastructure','out-of-band'].includes(data.class) && <NavButton key='di_nav_rack' title='Rack' onClick={() => this.changeContent(<RackInfo key='device_rack_info' device_id={this.props.id} />)} />}
     {this.state.navconf && ['device','infrastructure','out-of-band'].includes(data.class) && <NavButton key='di_nav_pems' title='PEMs' onClick={() => this.changeContent(<PemList key='device_pem_list' device_id={this.props.id} changeSelf={this.changeContent} />)} />}
     {this.state.navconf && <NavButton key='di_nav_stats' title='Statistics' onClick={() => this.changeContent(<StatisticsList key='device_statistics_list' device_id={this.props.id} changeSelf={this.changeContent} />)} />}
     {!this.state.navconf && function_strings.filter(fun => fun !== 'manage').map((op,idx) => <NavButton key={'di_nav_'+idx} title={op} onClick={() => this.changeContent(<Function key={'dev_func_'+op} id={this.props.id} op={op} type={this.state.extra.type_name} />)} />)}
    </NavBar>
    {this.state.content}
    </Fragment>
   )
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
  rest_call('api/device/extended',{id:this.props.id}).then(result => {
   result.data.a_domain_id = this.mapDomain(result.data.management_id, result.interfaces);
   this.setState(result)
  });
  rest_call('api/dns/domain_list',{filter:'forward'}).then(result => {
   const args = {data:this.state.data, domains:result.data}
   if (args.data)
    args.data.a_domain_id = this.mapDomain(this.state.data.management_id,this.state.interfaces);
   this.setState({domains:result.data})
  });
 }

 onChange = (e) => {
  const data = {...this.state.data, [e.target.name]:e.target.value}
  if(e.target.name === 'management_id')
   data.a_domain_id =  this.mapDomain(e.target.value,this.state.interfaces);
  this.setState({data:data})
 }

 mapDomain(id,interfaces){
  const if_obj = interfaces.find(intf => parseInt(intf.interface_id) === parseInt(id));
  return (if_obj) ? if_obj.a_domain_id : null;
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => rest_call('api/device/extended',{op:'update', ...this.state.data}).then(result => {
  result.data.a_domain_id = this.mapDomain(result.data.management_id,this.state.interfaces)
  this.setState(result)
 });

 render() {
  if (this.state.data && this.state.domains)
   return <article className='info'>
    <h1>Management Configuration</h1>
    <InfoColumns key='d_conf_ic'>
     <TextInput key='d_conf_hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
     <SelectInput key='d_conf_management_id' id='management_id' label='Mgmt Interface' value={this.state.data.management_id} onChange={this.onChange}>{this.state.interfaces.map((row,idx) => <option key={'de_intf_'+idx} value={row.interface_id}>{`${row.name} (${row.ip} - ${row.fqdn})`}</option>)}</SelectInput>
     <SelectInput key='d_conf_a_domain_id' id='a_domain_id' label='Mgmt Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'de_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
     <TextLine key='d_conf_oid' id='oid' label='Priv OID' text={this.state.extra.oid} />
     <TextLine key='d_conf_oui' id='oui' label='System OUI' text={this.state.extra.oui} />
    </InfoColumns>
    <SaveButton key='d_conf_btn_save' onClick={() => this.updateInfo()} title='Save' />
   </article>
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
  rest_call('api/device/rack',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => rest_call('api/device/rack',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data){
   const racked = (this.state.data.rack_id && this.state.data.rack_id !== 'NULL');
   return <article className='info'>
    <h1>Rack</h1>
    <InfoColumns key='d_rack_ic'>
     <SelectInput key='d_rack_id' id='rack_id' label='Rack ID' value={this.state.data.rack_id} onChange={this.onChange}>{this.state.racks.map((row,idx) => <option key={'d_rack_id_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
     {racked && <TextInput key='d_rack_size' id='rack_size' label='Size' value={this.state.data.rack_size} onChange={this.onChange} title='Size of device in U' />}
     {racked && <TextInput key='d_rack_unit' id='rack_unit' label='Unit' value={this.state.data.rack_unit} onChange={this.onChange} title='First unit of placement' />}
     {racked && <SelectInput key='d_rack_con_id' id='console_id' label='Console' value={this.state.data.console_id} onChange={this.onChange}>{this.state.consoles.map((row,idx) => <option key={'d_rack_con_id_'+idx} value={row.id}>{row.hostname}</option>)}</SelectInput>}
     {racked && <TextInput key='d_rack_con_port' id='console_port' label='Console Port' value={this.state.data.console_port} onChange={this.onChange} />}
    </InfoColumns>
    <SaveButton key='d_rack_btn_save' onClick={() => this.updateInfo()} title='Save' />
   </article>
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
  rest_call('api/pem/list',{device_id:this.props.device_id,lookup:true}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem)

 deleteList = (id) => (window.confirm('Really delete PEM?') && rest_call('api/pem/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 listItem = (row) => [row.id,row.name,row.pdu_id,row.pdu_name,row.pdu_slot,row.pdu_unit,<Fragment key={'dev_pems_frag_' + row.id}>
  <InfoButton key={'dev_pem_btn_info_' + row.id} onClick={() => this.changeContent(<PemInfo key={'pem_info_'+row.id} id={row.id} device_id={this.props.device_id} />)} title='Edit PEM information' />
  <DeleteButton key={'dev_pem_btn_delete_' + row.id}  onClick={() => this.deleteList(row.id) } title='Delete PEM' />
 </Fragment>]

 render(){
  return (this.state.data) ? <ContentReport key='dev_pems' header='PEMs' thead={['ID','Name','PDU ID','PDU Name','PDU Slot','PDU Unit','']} trows={this.state.data} listItem={this.listItem}>
   <ReloadButton key='dev_pems_btn_reload' onClick={() => this.componentDidMount()} />
   <AddButton key='dev_pems_btn_add' onClick={() => this.changeContent(<PemInfo key={'device_pem_info_new_' + rnd()} id='new' device_id={this.props.device_id} />)} title='Add PEM' />
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
  rest_call('api/pem/info',{id:this.props.id, device_id:this.props.device_id}).then(result => this.setState(result))
  rest_call('api/pdu/list',{device_id:this.props.device_id, empty:true}).then(result => this.setState({pdus:result.data}))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => rest_call('api/pem/info',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data && this.state.pdus){
   const pdu_info = this.state.pdus.find(pdu => parseInt(pdu.device_id) === parseInt(this.state.data.pdu_id));
   let slots = []
   if (pdu_info){
    for (let i = 0; i < pdu_info.slots; i++)
     slots.push({id:i,name:pdu_info[`${i}_slot_name`]});
   }
   return <article className='info'>
    <h1>PEM</h1>
    <InfoColumns key='d_pem_ic'>
     <TextInput key='d_pem_name' id='name' value={this.state.data.name} onChange={this.onChange} />
     <SelectInput key='d_pem_pdu_id' id='pdu_id' label='PDU' value={this.state.data.pdu_id} onChange={this.onChange}>{this.state.pdus.map((row,idx) => <option key={'d_pem_pdu_id_'+idx} value={row.device_id}>{row.name}</option>)}</SelectInput>
     <SelectInput key='d_pem_pdu_slot' id='pdu_slot' label='Slot' value={this.state.data.pdu_slot} onChange={this.onChange}>{slots.map((row,idx) => <option key={'d_pem_pdu_slot_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
     <TextInput key='d_pem_pdu_unit' id='pdu_unit' label='Unit' value={this.state.data.pdu_unit} onChange={this.onChange} />
    </InfoColumns>
    <SaveButton key='d_pem_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='d_pem_result' result={(this.state.update) ? (this.state.result) ? JSON.stringify(this.state.result) :JSON.stringify(this.state.update) : ''} />
   </article>
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

 loadList = (clear) => rest_call('api/statistics/list',{device_id:this.props.device_id}).then(result => this.setState((clear)? {...result,result:'',inserts:''} : result));

 changeContent = (elem) => this.props.changeSelf(elem)

 deleteList = (id) => (window.confirm('Really delete statistics point?') && rest_call('api/statistics/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 lookupStats = () => rest_call('api/statistics/lookup',{device_id:this.props.device_id}).then(result => { this.setState(result); this.loadList()} )

 listItem = (row) => [row.id,row.measurement,row.tags,row.name,row.oid,<Fragment key={'dev_stats_frag_' + row.id}>
  <InfoButton key={'dev_stats_btn_info_' + row.id} onClick={() => this.changeContent(<StatisticsInfo key={'statistics_info_'+row.id} id={row.id} device_id={this.props.device_id} />)} title='Edit data point' />
  <DeleteButton key={'dev_stats_btn_delete_' + row.id}  onClick={() => this.deleteList(row.id) } title='Delete data point' />
 </Fragment>]

 render(){
  return (this.state.data) ? <ContentReport key='dev_stats' header='Device statistics' thead={['ID','Measurement','Tags','Name','OID','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <ReloadButton key='dev_stats_btn_reload' onClick={() => this.loadList(true)} />
   <SearchButton key='dev_stats_btn_lookup' onClick={() => this.lookupStats()} title='Lookup device type stats' />
   <AddButton key='dev_stats_btn_add' onClick={() => this.changeContent(<StatisticsInfo key={'device_statistics_info_new_' + rnd()} id='new' device_id={this.props.device_id} />)} title='Add statistics' />
  </ContentReport>
  : <Spinner />
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
  rest_call('api/statistics/info',{id:this.props.id, device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}})

 updateInfo = () => rest_call('api/statistics/info',{op:'update', ...this.state.data}).then(result => this.setState(result));

 render() {
  if (this.state.data){
   return <article className='info'>
    <h1>Data point</h1>
    <InfoColumns key='dev_stat_ic'>
     <TextInput key='dev_stat_measurement' id='measurement' value={this.state.data.measurement} onChange={this.onChange} title='Group, or measurement, that the data point belongs to' />
     <TextInput key='dev_stat_tags' id='tags' value={this.state.data.tags} onChange={this.onChange} title='Tags are comma separated values that extend TSDB grouping' />
     <TextInput key='dev_stat_name' id='name' value={this.state.data.name} onChange={this.onChange} title='Data point name' />
     <TextInput key='dev_stat_oid' id='oid' value={this.state.data.oid} onChange={this.onChange} />
    </InfoColumns>
    <SaveButton key='dev_stat_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='dev_stat_result' result={(this.state.update) ? (this.state.result) ? JSON.stringify(this.state.result) :JSON.stringify(this.state.update) : JSON.stringify(this.state.update)} />
   </article>
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
  rest_call('api/device/control',{id:this.props.id}).then(result => this.setState(result));
 }

 operationDev = (op,msg) => {
  if (window.confirm(msg)){
   this.setState({wait:<Spinner />});
   rest_call('api/device/control',{id:this.props.id, device_op:op}).then(result => this.setState({...result,wait:null}))
  }
 }

 operationPem = (id,op,msg) => {
  if (window.confirm(msg)){
   this.setState({wait:<Spinner />});
   rest_call('api/device/control',{id:this.props.id, pem_op:op, pem_id:id}).then(result => this.setState({...result,wait:null}))
  }
 }

 lookupState = (id) => console.log('State lookup TODO');

 render() {
  return (
   <article className='info'>
    <h1>Device Control</h1>
    <InfoColumns key='dc_ic'>
     <label htmlFor='reboot'>Reboot:</label><ReloadButton id='reboot' key='dev_ctr_reboot' onClick={() => this.operationDev('reboot','Really reboot?')} title='Restart device' />
     <label htmlFor='shutdown'>Shutdown:</label><ShutdownButton id='shutdown' key='dev_ctr_shutdown' onClick={() => this.operationDev('shutdown','Really shutdown?')} title='Shutdown' />
     {this.state.pems.map(pem => {
      if(pem.state === 'off')
       return <Fragment key={'dc_pems_'+pem.id}><label htmlFor={pem.id}>{pem.name}</label><StartButton key={'dc_btn_start_'+pem.id} id={pem.id} onClick={() => this.operationPem(pem.id,'on','Power on PEM?')} title='Power ON' /></Fragment>
      else if (pem.state === 'on')
       return <Fragment key={'dc_pems_'+pem.id}><label htmlFor={pem.id}>{pem.name}</label><ShutdownButton key={'dc_btn_stop_'+pem.id} id={pem.id} onClick={() => this.operationPem(pem.id,'off','Power off PEM?')} title='Power OFF' /></Fragment>
      else
       return <Fragment key={'dc_pems_'+pem.id}><label htmlFor={pem.id}>{pem.name}</label><SearchButton key={'dc_btn_lookup_'+pem.id} id={pem.id} onClick={() => this.lookupState(pem.id)} title='Lookup State' /></Fragment>
     })}
    </InfoColumns>
    <Result key='dc_result' result={JSON.stringify(this.state.result)} />
    {this.state.wait}
   </article>)
 }
}

// ************** Logs **************
//
export class Logs extends Component {
 componentDidMount(){
  rest_call('api/device/log_get',{id:this.props.id}).then(result => this.setState(result));
 }

 clearLog = () => rest_call('api/device/log_clear',{id:this.props.id}).then(result => (result.deleted && this.setState({data:[]})));

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
  rest_call('api/device/configuration_template',{id:this.props.id}).then(result => this.setState(result));
 }

 render() {
  return (!this.state) ? <Spinner /> : <article>{(this.state.status === 'OK') ? this.state.data.map((row,idx) => <p key={'conf_'+idx}>{row}</p>) : <b>{this.state.info}</b>}</article>
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
  rest_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}))
  rest_call('api/ipam/network_list').then(result => this.setState({networks:result.data}))
  rest_call('api/device/class_list').then(result => this.setState({classes:result.data}))
 }

 addDevice = () => {
  if (this.state.data.hostname)
   rest_call('api/device/new',this.state.data).then(result => this.setState({result:JSON.stringify(result)}))
 }

 searchIP = () => {
  if (this.state.data.ipam_network_id)
   rest_call('api/ipam/address_find',{network_id:this.state.data.ipam_network_id}).then(result => this.setState({data:{...this.state.data, ip:result.ip}}))
 }

 render() {
  if (!this.state.domains || !this.state.classes || !this.state.networks)
   return <Spinner />
  else
   return (
    <article className='info'>
     <h1>Device Add</h1>
     <InfoColumns key='dn_content'>
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} placeholder='Device hostname' onChange={this.onChange} />
      <SelectInput key='class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={'dn_class_'+row} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='ipam_network_id' id='ipam_network_id' label='Network' value={this.state.data.ipam_network_id} onChange={this.onChange}>{this.state.networks.map((row,idx) => <option key={'dn_net_'+idx} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
      <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'dn_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <TextInput key='ip' id='ip' label='IP' value={this.state.data.ip} onChange={this.onChange} />
      <TextInput key='mac' id='mac' label='MAC' value={this.state.data.mac} onChange={this.onChange} />
     </InfoColumns>
     <StartButton key='dn_btn_start' onClick={() => this.addDevice()} title='Add device' />
     <SearchButton key='dn_btn_search' onClick={() => this.searchIP()} title='Find available IP' />
     <Result key='dn_result' result={this.state.result} />
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
  rest_call('api/ipam/network_list').then(result => this.setState({networks:result.data}))
  rest_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}))
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 changeContent = (elem) => this.setState({content:elem})

 Result(props){
  return  <article className='code'><pre>{JSON.stringify(props.result,null,2)}</pre></article>
 }

 runDiscovery(){
  this.setState({content:<Spinner />})
  rest_call('api/device/discover',{network_id:this.state.ipam_network_id, a_domain_id:this.state.a_domain_id}).then(result => this.setState({content:<article className='code'><pre>{JSON.stringify(result,null,2)}</pre></article>}))
 }

 render() {
  if (this.state.networks && this.state.domains){
   return (
    <Fragment key='dd_fragment'>
     <article className='info'>
      <h1>Device Discovery</h1>
      <InfoColumns key='dd_content'>
       <SelectInput key='ipam_network_id' id='ipam_network_id' label='Network' value={this.state.ipam_network_id} onChange={this.onChange}>{this.state.networks.map((row,idx) => <option key={'dd_net_'+idx} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
       <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'dd_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      </InfoColumns>
      <StartButton key='dd_btn_start' onClick={() => this.runDiscovery()} title='Start discovery' />
     </article>
     <NavBar key='dd_navigation' id='dd_navigation' />
     {this.state.content}
    </Fragment>
   )
  } else
   return <Spinner />
 }
}

// ************** Report **************
//
export class Report extends Component {
 componentDidMount(){
  rest_call('api/device/list', { extra:['system','type','mac','oui','class']}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.hostname,row.class,row.ip,row.mac,row.oui,row.model,row.oid,row.serial,StateMap({state:row.state})]

 render(){
  return (!this.state) ? <Spinner /> : <ContentReport key='dev_cr' header='Devices' thead={['ID','Hostname','Class','IP','MAC','OUI','Model','OID','Serial','State']} trows={this.state.data} listItem={this.listItem} />
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
  rest_call('api/device/type_list').then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem});

 changeSelf = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [row.base,<HrefButton text={row.name} onClick={() => this.changeSelf(<List key='device_list' field='type' search={row.name} />)} />,row.icon]

 render(){
  return (this.state.data) ? <Fragment key='dev_tp_fragment'>
   <ContentList key='dev_tp_cl' header='Device Types' thead={['Class','Name','Icon']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='dev_tp_cd'>{this.state.content}</ContentData>
  </Fragment> : <Spinner />
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
  rest_call('api/device/model_list').then(result => this.setState({...result,result:'OK'}))
 }

 syncModels = () => rest_call('api/device/model_list',{op:'sync'}).then(result => this.setState(result))

 listItem = (row) => [row.id,row.name,row.type,<Fragment key={'ml_' + row.id}>
  <ConfigureButton key={'ml_btn_info_' + row.id} onClick={() => this.changeContent(<ModelInfo key={'model_info_'+row.id} id={row.id} />)} title='Edit model information' />
  <DeleteButton key={'ml_btn_delete_' + row.id}  onClick={() => this.deleteList(row.id) } title='Delete model' />
 </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete model?') && rest_call('api/device/model_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return (this.state.data) ? <Fragment key='dev_ml_fragment'>
   <ContentList key='dev_ml_cl' header='Device Models' thead={['ID','Model','Type','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='ml_btn_reload' onClick={() => this.componentDidMount()} />
    <SyncButton key='_ml_btn_sync' onClick={() => this.syncModels() } title='Resync models' />
   </ContentList>
   <ContentData key='dev_ml_cd'>{this.state.content}</ContentData>
  </Fragment> : <Spinner />
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

 updateInfo = () =>  rest_call('api/device/model_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/device/model_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Device Model</h1>
     <InfoColumns key='dm_content'>
      <TextLine key='name' id='name' text={this.state.data.name} />
      <TextLine key='type' id='type' text={this.state.extra.type} />
      <TextInput key='defaults_file' id='defaults_file' label='Default File' value={this.state.data.defaults_file} onChange={this.onChange} />
      <TextInput key='image_file' id='image_file' label='Image  File' value={this.state.data.image_file} onChange={this.onChange} />
     </InfoColumns>
     <label className='info' htmlFor='parameters'>Parameters:</label>
     <textarea className='info' id='parameters' name='parameters' onChange={this.onChange} value={this.state.data.parameters} />
     <SaveButton key='dm_btn_save' onClick={() => this.updateInfo()} title='Save' />
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

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 ouiSearch = () => {
  rest_call('api/master/oui_info',{oui:this.state.data.oui}).then(result => this.setState({content:<article><div className='info col2'><label htmlFor='oui'>OUI:</label><span id='oui'>{result.data.oui}</span><label htmlFor='company'>Company:</label><span id='company'>{result.data.company}</span></div></article>}))
 }

 render() {
  return (<div className='flexdiv'>
   <article className='lineinput'>
    <h1>OUI Search</h1>
    <div>
     <span>Type OUI or MAC address to find OUI/company name:<input type='text' id='oui' name='oui' required='required' onChange={this.onChange} value={this.state.data.oui} placeholder='00:00:00' /></span>
     <SearchButton key='oui_btn_search' onClick={() => this.ouiSearch()} title='Search for OUI' />
    </div>
   </article>
   {this.state.content}
  </div>)
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
  rest_call('api/master/oui_list').then(result => this.setState(result))
 }

 render(){
  if (this.state.data)
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

// ************** Function **************
//
class Function extends Component {
 componentDidMount(){
  rest_call('api/device/function',{op:this.props.op, id:this.props.id, type:this.props.type}).then(result => this.setState(result))
 }
 render() {
  if (!this.state)
   return <Spinner />
  else if (this.state.status === 'OK'){
   if(this.state.data.length > 0){
    const head = Object.keys(this.state.data[0]);
    return <ContentReport key='df_cr' thead={head} trows={this.state.data} listItem={(row) => head.map(hd => row[hd])} />
   } else
    return <article>No Data</article>
  } else
   return <article><b>Error in devdata: {this.state.info}</b></article>
 }
}
