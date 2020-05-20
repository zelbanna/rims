import React, { Fragment, Component } from 'react'
import { post_call } from './infra/Functions.js';
import { RimsContext, Result, Spinner, StateLeds, InfoArticle, InfoColumns, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { AddButton, DeleteButton, GoButton, HeaderButton, InfoButton, ItemsButton, LogButton, PauseButton, RevertButton, ReloadButton, SaveButton, ShutdownButton, SnapshotButton, StartButton, StopButton, SyncButton, UiButton } from './infra/Buttons.jsx';
import { StateLine, TextInput, TextLine } from './infra/Inputs.jsx';
import { NavBar, NavInfo, NavButton } from './infra/Navigation.jsx';

import { Info as DeviceInfo, Logs as DeviceLogs } from './device.jsx';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/list',{field:'base',search:'hypervisor',extra:['type','functions','url'],sort:'hostname'}).then(result => this.setState(result))
 }

 listItem = (row) => {
  const up =  (row.ip_state === 'up');
  return [row.hostname,row.type_name,<Fragment key={'hyp_buttons_'+row.id}>
   <StateLeds state={row.ip_state} />
   {up && row.type_functions === 'manage' && <InfoButton key={'hyp_btn_info_'+row.id} onClick={() => this.context.changeMain(<Manage key={'hypervisor_manage_'+row.id} device_id={row.id} type={row.type_name} />)} />}
   {up && row.url && row.url.length > 0 && <UiButton key={'hyp_ btn_ui_'+row.id} onClick={() => window.open(row.url,'_blank') } />}
   </Fragment>]
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <Fragment key='hyp_fragment'>
   <ContentList key='hyp_cl' header='Hypervisor' thead={['Hostname','Type','']} trows={this.state.data} listItem={this.listItem}>
    <SyncButton key='hyp_btn_sync' onClick={() => this.changeContent(<Sync />) } />
   </ContentList>
   <ContentData key='hyp_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}
Main.contextType = RimsContext;

// ************** Sync **************
//
class Sync extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/vm_mapping').then(result => {
    let entries = [];
    ['existing','inventory','discovered','database'].forEach(type => {
     if (result.hasOwnProperty(type))
      result[type].forEach(entry => { entry.type = type; entries.push(entry); })
    })
    this.setState({data:entries})
   })
 }

 listItem = (row) => [row.type,row.host_id,row.device_id,row.vm,row.device_uuid,row.config]

 render(){
  return <ContentReport key='hyp_cr' header='VM Mapping' thead={['Status','Host','Device','VM Name','Device UUID','Config']} trows={this.state.data} listItem={this.listItem} />
 }
}

// ************** Manage **************
//
export class Manage extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/management',{id:this.props.device_id}).then(result => {
   this.context.loadNavigation(<NavBar key='hypervisor_navbar'>
    <NavButton key='hyp_nav_inv' title='Inventory' onClick={() => this.changeContent(<Inventory key='hypervisor_inventory' device_id={this.props.device_id} type={this.props.type} />)} />
    <NavButton key='hyp_nav_logs' title='Logs' onClick={() => this.changeContent(<DeviceLogs key='device_logs' id={this.props.device_id} />)} />
    {result.data.url && (result.data.url.length > 0) && <NavButton key='hyp_nav_ui' title='UI' onClick={() => window.open(result.data.url,'_blank')} />}
    <NavInfo key='hyp_nav_name' title={result.data.hostname} />
   </NavBar>);
   this.setState({...result,content:<Inventory key='hypervisor_inventory' device_id={this.props.device_id} type={this.props.type} />});
  })
 }

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return  <Fragment key='manage_base'>{this.state.content}</Fragment>
 }
}
Manage.contextType = RimsContext;

// ************** Inventory **************
//
export class Inventory extends Component{
 constructor(props){
  super(props)
  this.state = {sort:'name'}
 }

 componentDidMount(){
  post_call('api/devices/' + this.props.type + '/inventory',{device_id:this.props.device_id, sort: this.state.sort}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})

 sortList = (method) => {
  if (method === 'name')
   this.state.data.sort((a,b) => a.name.localeCompare(b.name));
  else
   this.state.data.sort((a,b) => (a.id - b.id))
  this.setState({sort:method})
 }

 listItem = (row) => [row.id,row.name,<Operation key={'hl_op_'+row.id} vm_id={row.id} device_id={this.props.device_id} type={this.props.type} changeContent={this.changeContent} state={row.state} />]

 render(){
  if (this.state.data){
   const thead = [<HeaderButton key='hl_btn_id' text='ID' highlight={(this.state.sort === 'id')} onClick={() => this.sortList('id')} />,<HeaderButton key='hl_btn_vm' text='VM' highlight={(this.state.sort === 'name')} onClick={() => this.sortList('name')} />,'Operations'];
   return <Fragment key='hl_fragment'>
    <ContentList key='hl_cl' header='Inventory' thead={thead} trows={this.state.data} listItem={this.listItem}>
     <ReloadButton key='hl_btn_reload' onClick={() => {this.setState({data:undefined}); this.componentDidMount()} } />
     <LogButton key='hl_btn_logs' onClick={() => this.changeContent(<DeviceLogs key='device_logs' id={this.props.device_id} />)} title='Device logs' />
    </ContentList>
    <ContentData key='hl_cd'>{this.state.content}</ContentData>
   </Fragment>
  } else
   return <Spinner />
 }
}

// *************** Operation ***************
//
class Operation extends Component{
 constructor(props){
  super(props)
  this.state = {state:this.props.state, status:'',wait:null};
 }

 operation = (op) => {
  this.setState({wait:<Spinner />})
  post_call('api/devices/'+this.props.type+'/vm_op',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:op}).then(result => this.setState({...result, wait:null}));
 }

 snapshot = (op) => {
  this.setState({wait:<Spinner />})
  post_call('api/devices/'+this.props.type+'/vm_snapshot',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:op}).then(result => this.setState({...result, wait:null}));
 }

 render(){
   const on = (this.state.state === 'on');
   const off = (this.state.state === 'off');
   return <Fragment key={'hyp_frag_'+this.props.vm_id}>
    <InfoButton key={'hyp_btn_info_'+this.props.vm_id} onClick={() => this.props.changeContent(<Info key={'hypervisor_info_'+this.props.vm_id} device_id={this.props.device_id} vm_id={this.props.vm_id} type={this.props.type} changeSelf={this.props.changeContent} />)} title='VM info' />
    {(off || this.state.state === 'suspended')  && <StartButton key={'hyp_btn_start_'+this.props.vm_id} onClick={() => this.operation('on')} title={this.state.status} />}
    {on && <StopButton key={'hyp_btn_stop_'+this.props.vm_id} onClick={() => this.operation('shutdown')} title={this.state.status} />}
    {on && <ReloadButton key={'hyp_btn_reload_'+this.props.vm_id} onClick={() => this.operation('reboot')} title={this.state.status} />}
    {on && <PauseButton key={'hyp_btn_suspend_'+this.props.vm_id} onClick={() => this.operation('suspend')} title={this.state.status} />}
    {(on || this.state.state === 'suspended') && <ShutdownButton key={'hyp_btn_shutdown_'+this.props.vm_id} onClick={() => this.operation('off')} title={this.state.status} />}
    {off && <SnapshotButton key={'hyp_btn_snapshot_'+this.props.vm_id} onClick={() => this.snapshot('create')} title='Take snapshot' />}
    {off && <ItemsButton key={'hyp_btn_snapshots_'+this.props.vm_id} onClick={() => this.props.changeContent(<Snapshots key={'hypervisor_snapshots_'+this.props.vm_id} device_id={this.props.device_id} vm_id={this.props.vm_id} type={this.props.type} />)} title='Snapshot info' />}
    {this.state.wait}
   </Fragment>
 }
}

// ************ Info *************
//
class Info extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeSelf = (elem) => this.props.changeSelf(elem);

 changeContent = (elem) => this.setState({content:elem});

 changeImport = (intf) => import('./interface.jsx').then(lib => this.setState({content:<lib.Info key={'interface_info_'+intf[0]} device_id={this.state.data.device_id} class='virtual' mac={intf[1].mac} name={intf[1].name} interface_id={intf[1].interface_id} changeSelf={this.changeContent} />}))

 componentDidMount(){
  post_call('api/devices/'+this.props.type+'/vm_info',{device_id:this.props.device_id, vm_id:this.props.vm_id}).then(result => this.setState(result))
 }

 syncDatabase(){
  post_call('api/devices/'+this.props.type+'/vm_info',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:'update'}).then(result => this.setState(result))
 }

 updateInfo(){
  post_call('api/devices/'+this.props.type+'/vm_map',{device_uuid:this.state.data.device_uuid, device_id:this.state.data.device_id, host_id:this.props.device_id, op:'update'}).then(result => this.setState({update:result.update}))
 }

 interfaceButton(intf){
  if(this.state.data.device_id){
   if (intf[1].interface_id)
    return <InfoButton key={'hyp_if_btn_'+intf[0]} onClick={() => this.changeImport([intf[0],{interface_id:intf[1].interface_id}])} />
   else
    return <AddButton key={'hyp_if_btn_'+intf[0]} onClick={() => this.changeImport({...intf,interface_id:'new'})} />
  } else
   return <div />
 }

 render(){
  if (this.state.data) {
   const data = this.state.data;
   return <Fragment key='hyp_frag'>
    <InfoArticle key='hyp_article' header='VM info'>
     <InfoColumns key='hyp_ic' columns={3}>
      <TextLine key='hyp_name' id='name' text={data.name} /><div />
      <TextInput key='hyp_device_id' id='device_id' label='Device ID' value={data.device_id} onChange={this.onChange} /><div />
      <TextLine key='hyp_device_name' id='device' label='Device Name' text={data.device_name} /><div />
      <TextLine key='hyp_snmp' id='snmp_id' label='SNMP id' text={data.snmp_id} /><div />
      <TextLine key='hyp_uuid' id='uuid' label='UUID' text={data.device_uuid} /><div />
      <StateLine key='hyp_state' id='state' state={data.state} /><div />
      <TextLine key='hyp_config' id='config' text={data.config} /><div />
      {Object.entries(this.state.interfaces).map(row => <Fragment key={'hyp_intf_frag_'+row[0]}><TextLine key={'hyp_intf_'+row[0]} id={'interface_'+row[0]} label='Interface' text={`${row[1].name} - ${row[1].mac} - ${row[1].port}`} />{this.interfaceButton(row)}</Fragment>)}
     </InfoColumns>
     <SaveButton key='hyp_btn_save' onClick={() => this.updateInfo()} title='Save mapping' />
     <SyncButton key='hyp_btn_sync' onClick={() => this.syncDatabase()} title='Resync database with VM info' />
     {data.device_id && <GoButton key='hyp_btn_device_vm_info' onClick={() => this.changeSelf(<DeviceInfo key='device_info' id={data.device_id} changeSelf={this.props.changeSelf} />)} title='VM device info' />}
     <Result key='hyp_res' result={JSON.stringify(this.state.update)} />
    </InfoArticle>
    <NavBar />
    {this.state.content}
   </Fragment>
  } else
   return <Spinner />
 }
}

// ************ Snapshots *************
//
class Snapshots extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  this.snapshot('list',undefined);
 }

 snapshot = (op,id) => {
  this.setState({wait:<Spinner />});
  post_call('api/devices/'+this.props.type+'/vm_snapshot',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:op, snapshot:id}).then(result => this.setState({...result, wait:null}));
 }

 deleteList = (id) => {
  if (window.confirm('Really delete snapshot?')){
   this.setState({wait:<Spinner />})
   post_call('api/devices/'+this.props.type+'/vm_snapshot',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:'remove', snapshot:id}).then(result => {
    if(result.deleted){
     let highest = 0;
     const data = this.state.data.filter(row => (row.id !== id));
     data.forEach(row => { highest = (highest < parseInt(row.id)) ? parseInt(row.id) : highest });
     this.setState({data:data,highest:highest,wait:null});
    }
   })
  }
 }

 listItem = (row) => [row.name,row.id,row.desc,row.created,row.state,<Fragment key={'hyp_snap_buttons_'+row.id}>
  <RevertButton key={'hs_revert_'+row.id} onClick={() => this.snapshot('revert',row.id)} title='Revert to snapshot' />
  <DeleteButton key={'hs_delete_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete snapshot' />
 </Fragment>]

 render(){
  return <ContentReport key='hyp_snapshot_cr' header={`Snapshot (${this.props.vm_id}) Highest ID:${this.state.highest}`} thead={['Name','ID','Description','Created','State','']} trows={this.state.data} listItem={this.listItem}>
   <ReloadButton key='hs_reload' onClick={() => this.snapshot('list',undefined)} title='Reload list' />
   {this.state.wait}
  </ContentReport>
 }
}
