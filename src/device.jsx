import React, { Component, Fragment } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, StateMap, SearchField, InfoColumns, RimsContext, Result, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { NavBar, NavButton, NavDropDown, NavReload } from './infra/Navigation.js'
import { TextInput, TextLine, StateLine, SelectInput, UrlInput } from './infra/Inputs.jsx';
import { AddButton, CheckButton, ConfigureButton, ConnectionButton, DeleteButton, DevicesButton, ItemsButton, LogButton, NetworkButton, ReloadButton, SaveButton, SearchButton, ShutdownButton, StartButton, SyncButton, HrefButton, TermButton, UiButton } from './infra/Buttons.jsx';

import { List as VisualizeList, Edit as VisualizeEdit } from './visualize.jsx';
import { List as RackList, Layout as RackLayout, Infra as RackInfra } from './rack.jsx';

// **************** Main ****************
//
// TODO - proper PDU and Console action for rack devices
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  if (this.props.rack_id)
   rest_call("api/rack/inventory",{id:this.props.rack_id}).then(result => this.compileNavItems({rack_id:this.props.rack_id, ...result}))
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
    <NavButton key='dev_nav_list' title='List' onClick={() => this.changeContent(<List key='dl' rack_id={state.rack_id} />)} />
    <NavButton key='dev_nav_srch' title='Search' onClick={() => this.changeContent(<Search key='ds' changeSelf={this.changeContent} />)} />
    <NavButton key='dev_nav_types' title='Types' onClick={() => this.changeContent(<TypeList key='dtl' changeSelf={this.changeContent} />)} />
    <NavButton key='dev_nav_model' title='Models' onClick={() => this.changeContent(<ModelList key='dml' />)} />
   </NavDropDown>
   <NavButton key='dev_nav_maps' title='Maps' onClick={() => this.changeContent(<VisualizeList key='visualize_list' />)} />
   {(state.pdu.length > 0) && <NavDropDown key='dev_nav_pdus' title='PDUs'>{state.pdu.map((row,idx) => <NavButton key={'dev_nav_pdu_' + idx} title={row.hostname} onClick={() =>alert('implement PDU')} />)}</NavDropDown>}
   {(state.console.length > 0) && <NavDropDown key='dev_nav_consoles' title='Consoles'>{state.console.map((row,idx) => <NavButton key={'dev_nav_console_' + idx} title={row.hostname} onClick={() =>alert('implement Console')} />)}</NavDropDown>}
   {(state.rack_id) && <NavButton key='dev_nav_rack' title={state.name} onClick={() => this.changeContent(<RackLayout key='rack_layout' id={state.rack_id} />)} />}
   <NavDropDown key='dev_nav_oui' title='OUI'>
    <NavButton key='dev_nav_ouis' title='Search' onClick={() => this.changeContent(<OUISearch key='oui_search' />)} />
    <NavButton key='dev_nav_ouil' title='List' onClick={() => this.changeContent(<OUIList key='oui_list' />)} />
   </NavDropDown>
   <NavButton key='dev_nav_resv' title='Reservations' onClick={() => this.changeImport('reservation','List',{})} style={{float:'right'}} />
   <NavButton key='dev_nav_loc' title='Locations' onClick={() => this.changeImport('location','List',{})} style={{float:'right'}} />
   <NavDropDown key='dev_nav_ipam' title='IPAM' style={{float:'right'}}>
    <NavButton key='dev_nav_isrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'DHCP'})} />
    <NavButton key='dev_nav_nets' title='Networks' onClick={() => this.changeImport('ipam','NetworkList',{})} />
   </NavDropDown>
   <NavDropDown key='dev_nav_dns' title='DNS' style={{float:'right'}}>
    <NavButton key='dev_nav_dsrv' title='Servers' onClick={() => this.changeImport('server','List',{type:'DNS'})} />
    <NavButton key='dev_nav_doms' title='Domains' onClick={() => this.changeImport('dns','DomainList',{})} />
   </NavDropDown>
   <NavDropDown key='dev_nav_racks' title='Rack' style={{float:'right'}}>
    <NavButton key='dev_nav_all_rack' title='Racks' onClick={() => this.changeContent(<RackList key='rack_list' />)} />
    <NavButton key='dev_nav_all_pdu' title='PDUs' onClick={() => this.changeContent(<RackInfra key='pdu_list' type='pdu' />)} />
    <NavButton key='dev_nav_all_con' title='Consoles' onClick={() => this.changeContent(<RackInfra key='console_list' type='console' />)} />
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
      <option value='hostname'>Hostname</option>
      <option value='type'>Type</option>
      <option value='id'>ID</option>
      <option value='ip'>IP</option>
      <option value='mac'>MAC</option>
      <option value='ipam_id'>IPAM ID</option>
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
    const num1 = Number(a.ip.split(".").map(num => (`000${num}`).slice(-3) ).join(""));
    const num2 = Number(b.ip.split(".").map(num => (`000${num}`).slice(-3) ).join(""));
    return num1-num2;
   });
  this.setState({sort:method})
 }

 listItem = (row) => [row.ip,<HrefButton key={'dl_btn_info_'+row.id} text={row.hostname} onClick={() => this.changeContent(<Info key={'di_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title={row.id} />,StateMap({state:row.state}),<DeleteButton key={'dl_btn_del_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete device' />]

 deleteList = (id) => (window.confirm("Really delete device "+id+"?") && rest_call('api/device/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  if (this.state.data){
   let device_list = this.state.data.filter(row => row.hostname.includes(this.state.searchfield));
   const thead = [<HrefButton key='dl_btn_ip' text='IP' style={(this.state.sort === 'ip') ? ({color:'var(--high-color)'}):({})} onClick={() => { this.sortList('ip') }} />,<HrefButton key='dl_btn_hostname' text='Hostname' style={(this.state.sort === 'hostname') ? ({color:'var(--high-color)'}):({})} onClick={() => { this.sortList('hostname') }} />,'',''];
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
  this.state = {data:undefined, found:true, content:null}
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 changeSelf = (elem) => this.props.changeSelf(elem);

 updateInfo = (api) => {
  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 componentDidMount(){
  rest_call("api/device/info",{id:this.props.id, extra:["types","classes"]}).then(result => this.setState(result))
 }

 lookupInfo = () => {
  this.setState({content:<Spinner />,result:''})
  rest_call("api/device/info",{id:this.props.id, op:'lookup'}).then(result => this.setState({...result,content:null}))
 }

 changeInterfaces(){
  import('./interface.jsx').then(lib => {
   var InterfaceList = lib.List;
   this.changeContent(<InterfaceList key='interface_list' device_id={this.props.id} changeSelf={this.changeContent} />);
  })
 }

 render() {
  if(this.state.data){
   const vm = (this.state.data.class === 'vm' && this.state.vm) ? this.state.vm : false;
   const rack = (this.state.rack && this.state.data.class !== 'vm') ? this.state.rack : false;
   const change_self = (this.props.changeSelf);
   const has_ip = (this.state.extra.interface_ip);

   // TODO: Function for 'manage' that takes base,type,id
   const functions = (this.state.extra.functions.length >0) ? this.state.extra.functions.split(',').map((row,idx) => (<NavButton key={'di_nav_'+idx} title={row} onClick={() => this.changeContent(<Function key={'dev_func'+row} id={this.props.id} op={row} type={this.state.extra.type_name} />)} />)) : null

   return (
    <Fragment key='di_fragment'>
     <article className='info'>
     <h1>Device</h1>
     <InfoColumns key='di_info' className='left'>
      <TextLine key='hostname' id='hostname' text={this.state.data.hostname} />
      <TextInput key='mac' id='mac' label='Sys Mac' value={this.state.data.mac} title='System MAC' onChange={this.onChange} />
      <TextLine key='if_mac' id='if_mac' label='Mgmt MAC' text={this.state.extra.interface_mac} title='Management Interface MAC' />
      <TextLine key='if_ip' id='if_ip' label='Mgmt IP' text={this.state.extra.interface_ip} />
      <TextLine key='snmp' id='snmp' label='SNMP' text={this.state.data.snmp} />
      <StateLine key='state' id='state' state={[this.state.extra.if_state,this.state.extra.ip_state]} />
     </InfoColumns>
     <InfoColumns key='di_extra' className='left'>
      <TextLine key='id' id='id' text={this.props.id} />
      <SelectInput key='class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={'di_class_'+row} value={row}>{row}</option>)}</SelectInput>
      <SelectInput key='type_id' id='type_id' label='Type' value={this.state.data.type_id} onChange={this.onChange}>{this.state.types.map((row,idx) => <option key={'di_type_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <TextInput key='model' id='model' value={this.state.data.model} onChange={this.onChange} extra={this.state.data.model} />
      <TextLine key='version' id='version' text={this.state.data.version} onChange={this.onChange} />
      <TextInput key='serial' id='serial' label='S/N' value={this.state.data.serial} onChange={this.onChange} />
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
      <TextInput key='comment' id='comment' value={this.state.data.comment} onChange={this.onChange} />
      <UrlInput key='url' id='url' label='URL' value={this.state.data.url} onChange={this.onChange} />
     </InfoColumns>
     <br />
     <SaveButton key='di_btn_save' onClick={() => this.updateInfo('api/device/info')} title='Save' />
     <ConnectionButton key='di_btn_conn' onClick={() => this.changeInterfaces()} title="Interfaces" />
     <StartButton key='di_btn_cont' onClick={() => this.changeContent(<Control key='device_control' id={this.props.id} />)} title="Device control" />
     <CheckButton key='di_btn_conf' onClick={() => this.changeContent(<Configuration key='device_configure' id={this.props.id} />)} title="Configuration template" />
     {change_self && <ConfigureButton key='di_btn_edit' onClick={() => this.changeSelf(<Extended key={'de_'+this.props.id} id={this.props.id} />)} title="Extended configuration" />}
     {change_self && <NetworkButton key='di_btn_netw' onClick={() => this.changeSelf(<VisualizeEdit key={'ve_'+this.props.id} type='device' id={this.props.id} changeSelf={this.props.changeSelf} />)} title="Connectivity map" />}
     {has_ip && <SearchButton key='di_btn_srch' onClick={() => this.lookupInfo()} title="Information lookup" />}
     {has_ip && <LogButton key='di_btn_logs' onClick={() => this.changeContent(<Logs key='device_logs' id={this.props.id} />)} title="Logs" />}
     {has_ip && <TermButton key='di_btn_ssh' onClick={() => { const sshWin = window.open(`ssh://${this.state.extra.username}@${this.state.extra.interface_ip}`,'_blank'); sshWin.close(); }} title='SSH connection' />}
     {rack && rack.console_ip && rack.console_port && <TermButton key='di_btn_console' onClick={() => { const termWin = window.open(`telnet://${rack.console_ip}:${6000 +rack.console_port}`,'_blank'); termWin.close();}} title="Serial Connection" /> }
     {this.state.data.url && <UiButton key='di_btn_ui' onClick={() => window.open(this.state.data.url,'_blank')} title="Web UI" />}
     <Result key='dev_result' result={JSON.stringify(this.state.update)} />
    </article>
    <NavBar key='di_navigation' id='di_navigation'>{functions}</NavBar>
    {this.state.content}
    </Fragment>
   )
  } else
   return <Spinner />
 }
}

// ************* Extended *************
//
// TODO: complete this one
class Extended extends Component {
 constructor(props){
  super(props)
  this.state = {data:undefined, found:true, content:null}
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target[(e.target.type !== "checkbox") ? "value" : "checked"]}})

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) => {
  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 componentDidMount(){
  rest_call("api/device/extended",{id:this.props.id}).then(result => this.setState(result))
  rest_call("api/dns/domain_list",{filter:'forward'}).then(result => this.setState({domains:result.data}))
 }

 render() {
  if (this.state.data && this.state.domains){
  const rack = (this.state.extra.class !== 'vm');
  return <article className='info'>
   <h1>Extended configuration</h1>
   <InfoColumns key='de_ic'>
    <TextInput key='hostnamee' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
    <TextLine key='oid' id='oid' label='Priv OID' text={this.state.extra.oid} />
    <TextLine key='oui' id='oui' label='Mgmt OUI' text={this.state.extra.oui} />
    <SelectInput key='management_id' id='management_id' label='Mgmt Interface' value={this.state.data.management_id} onChange={this.onChange}>{this.state.interfaces.map((row,idx) => <option key={'de_intf_'+idx} value={row.interface_id}>{`${row.name} (${row.ip} - ${row.fqdn})`}</option>)}</SelectInput>
    <SelectInput key='a_domain_id' id='a_domain_id' label='Mgmt Domain' value={this.state.extra.management_domain} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'de_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
    {rack && <SelectInput key='rack_id' id='rack_info_rack_id' label='Rack' value={(this.state.rack)?this.state.rack.rack_id:'NULL'} onChange={this.onChange}>{this.state.infra.racks.map((row,idx) => <option key={'de_rack_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>}
   </InfoColumns>
  </article>
  } else
   return <Spinner />
 }
}

// ************* Control **************
//
// TODO: complete this one
//
class Control extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }
 componentDidMount(){
  rest_call("api/device/control",{id:this.props.id}).then(result => this.setState(result));
 }

 operationDev = (op,msg) => {
  (window.confirm(msg) && rest_call("api/device/control",{id:this.props.id, dev_op:op}).then(result => this.setState(result)))
 }

 render() {
  return (
   <article className='info'>
    <h1>Device Control</h1>
    <InfoColumns key='dc_ic' columns={3}>
     <label htmlFor='reboot'>Reboot:</label><ReloadButton id='reboot' key='dev_ctr_reboot' onClick={() => this.operationDev('reboot','Really reboot?')} title='Restart device' /><div />
     <label htmlFor='shutdown'>Shutdown:</label><ShutdownButton id='shutdown' key='dev_ctr_shutdown' onClick={() => this.operationDev('shutdown','Really shutdown?')} title='Shutdown' /><div />
    </InfoColumns>
    <Result key='dc_result' result={JSON.stringify(this.state.result)} />
   </article>
  )
 }
}
 /*
 for pem in res.get('pems',[]):
  aWeb.wr("<!-- %(pdu_type)s@%(pdu_ip)s:%(pdu_slot)s/%(pdu_unit)s -->"%pem)
  aWeb.wr("<label for='pem_%(name)s'>PEM: %(name)s</label><span id='pem_%(name)s'>&nbsp;"%pem)
  if   pem['state'] == 'off':
   aWeb.wr(aWeb.button('start', DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&pem_id=%s&pem_op=on'%(res['id'],pem['id'])))
  elif pem['state'] == 'on':
   aWeb.wr(aWeb.button('stop',  DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&pem_id=%s&pem_op=off'%(res['id'],pem['id'])))
  else:
   aWeb.wr(aWeb.button('help', TITLE='Unknown state'))
  aWeb.wr("</span><DIV>%s</DIV>"%(pem.get('op',{'status':'&nbsp;'})['status']))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")
*/
// ************** Logs **************
//
export class Logs extends Component {
 componentDidMount(){
  rest_call("api/device/log_get",{id:this.props.id}).then(result => this.setState(result));
 }

 render() {
  return (!this.state) ? <Spinner /> : <ContentReport key='dev_log_cr' header='Devices' thead={['Time','Message']} trows={this.state.data} listItem={(row) => [row.time,row.message]} />
 }
}

// ******** Configuration *********
//
class Configuration extends Component {
 componentDidMount(){
  rest_call("api/device/configuration_template",{id:this.props.id}).then(result => this.setState(result));
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
   rest_call("api/device/new",this.state.data).then(result => this.setState({result:JSON.stringify(result)}))
 }

 searchIP = () => {
  if (this.state.data.ipam_network_id)
   rest_call("api/ipam/address_find",{network_id:this.state.data.ipam_network_id}).then(result => this.setState({data:{...this.state.data, ip:result.ip}}))
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
  rest_call("api/ipam/network_list").then(result => this.setState({networks:result.data}))
  rest_call("api/dns/domain_list",{filter:'forward'}).then(result => this.setState({domains:result.data}))
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 changeContent = (elem) => this.setState({content:elem})

 Result(props){
  return  <article className='code'><pre>{JSON.stringify(props.result,null,2)}</pre></article>
 }

 render() {
  if (this.state.networks && this.state.domains){
   return (
    <Fragment key='dd_fragment'>
     <article className="info">
      <h1>Device Discovery</h1>
      <InfoColumns key='dd_content'>
       <SelectInput key='ipam_network_id' id='ipam_network_id' label='Network' value={this.state.ipam_network_id} onChange={this.onChange}>{this.state.networks.map((row,idx) => <option key={'dd_net_'+idx} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
       <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'dd_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      </InfoColumns>
      <StartButton key='dd_btn_start' onClick={() => this.changeContent(<DiscoverRun key={'dd_run_' + this.state.ipam_network_id} ipam_network_id={this.state.ipam_network_id} a_domain_id={this.state.a_domain_id} />)} title='Start discovery' />
     </article>
     <NavBar key='dd_navigation' id='dd_navigation' />
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
 componentDidMount(){
  rest_call('api/device/type_list').then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem});

 changeSelf = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [row.base,<HrefButton text={row.name} onClick={() => this.changeSelf(<List key='device_list' field='type' search={row.name} />)} />,row.icon]

 render(){
  return (this.state) ? <Fragment key='dev_tp_fragment'>
   <ContentList key='dev_tp_cl' header='Device Types' thead={['Class','Name','Icon']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='dev_tp_cd'>{this.state.content}</ContentData>
  </Fragment> : <Spinner />
 }
}

// ************** Model List **************
//
class ModelList extends Component {

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
  return (this.state) ? <Fragment key='dev_ml_fragment'>
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

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

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
     <label htmlFor='parameters'>Parameters:</label>
     <textarea id='parameters' name='parameters' onChange={this.onChange} value={this.state.data.parameters} />
     <SaveButton key='dm_btn_save' onClick={() => this.updateInfo('api/device/model_info')} title='Save' />
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
  rest_call('api/master/oui_info',{oui:this.state.data.oui}).then(result => this.setState({content:<article><div className='info col2'><label htmlFor='oui'>OUI:</label><span id='oui'>{result.oui}</span><label htmlFor='company'>Company:</label><span id='company'>{result.company}</span></div></article>}))
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

// ************** Function **************
//
class Function extends Component {
 componentDidMount(){
  rest_call("api/device/function",{op:this.props.op, id:this.props.id, type:this.props.type}).then(result => this.setState(result))
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
