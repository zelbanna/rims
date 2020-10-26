import React, { Component, Fragment } from 'react'
import { post_call } from './infra/Functions.js';
import { RimsContext, Result, Spinner, StateLeds, InfoArticle, InfoColumns, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { AddButton, DeleteButton, GoButton, HeaderButton, InfoButton, ItemsButton, LogButton, PauseButton, RevertButton, ReloadButton, SaveButton, ShutdownButton, SnapshotButton, StartButton, StopButton, SyncButton, UiButton } from './infra/Buttons.jsx';
import { SearchField, StateLine, TextInput, TextLine } from './infra/Inputs.jsx';
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
  return [row.hostname,row.type_name,<>
   <StateLeds key='state' state={row.ip_state} />
   {up && row.type_functions === 'manage' && <InfoButton key='info' onClick={() => this.context.changeMain(<Manage key={'hypervisor_manage_'+row.id} device_id={row.id} type={row.type_name} />)} />}
   {up && row.url && row.url.length > 0 && <UiButton key='ui' onClick={() => window.open(row.url,'_blank') } />}
   </>]
 }

 render(){
  return <>
   <ContentList key='cl' header='Hypervisor' thead={['Hostname','Type','']} trows={this.state.data} listItem={this.listItem}>
    <SyncButton key='sync' onClick={() => this.changeContent(<Sync key='vm_sync' />) } />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </>
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
  post_call('api/device/vm_mapping',{device_id:this.props.device_id}).then(result => {
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
  return <>{this.state.content}</>
 }
}
Manage.contextType = RimsContext;

// ************** Inventory **************
//
export class Inventory extends Component{
 constructor(props){
  super(props)
  this.state = {sort:'name', searchfield:''}
 }

 componentDidMount(){
  post_call('api/devices/' + this.props.type + '/inventory',{device_id:this.props.device_id, sort: this.state.sort}).then(result => this.setState(result))
 }

 sortList = (method) => {
  const data = this.state.data;
  if (method === 'name')
   data.sort((a,b) => a.name.localeCompare(b.name));
  else
   data.sort((a,b) => (a.id - b.id))
  this.setState({sort:method})
 }

 listItem = (row) => [row.id,row.name,<Operation key={'hl_op_'+row.id} vm_id={row.id} device_id={this.props.device_id} type={this.props.type} changeContent={(e) => this.changeContent(e)} state={row.state} />]

 render(){
  if (this.state.data){
   const searchfield = this.state.searchfield;
   const data = (searchfield.length === 0) ? this.state.data : this.state.data.filter(row => (row.name.toLowerCase().includes(searchfield)));
   const thead = [<HeaderButton key='id' text='ID' highlight={(this.state.sort === 'id')} onClick={() => this.sortList('id')} />,<HeaderButton key='vm' text='VM' highlight={(this.state.sort === 'name')} onClick={() => this.sortList('name')} />,'Operations'];
   return <>
    <ContentList key='cl' header='Inventory' thead={thead} trows={data} listItem={this.listItem}>
     <ReloadButton key='reload' onClick={() => {this.setState({data:undefined}); this.componentDidMount()} } />
     <LogButton key='logs' onClick={() => this.changeContent(<DeviceLogs key='device_logs' id={this.props.device_id} />)} title='Device logs' />
     <SyncButton key='sync' onClick={() => this.changeContent(<Sync key='vm_sync' device_id={this.props.device_id}/>)} title='Map VMs' />
     <SearchField key='search' searchFire={(s) => this.setState({searchfield:s})} placeholder='Search inventory' />
    </ContentList>
    <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
   </>
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
   return <>
    <InfoButton key='info' onClick={() => this.props.changeContent(<Info key='hypervisor_info' device_id={this.props.device_id} vm_id={this.props.vm_id} type={this.props.type} changeSelf={this.props.changeContent} />)} title='VM info' />
    {(off || this.state.state === 'suspended')  && <StartButton key='start' onClick={() => this.operation('on')} title={this.state.status} />}
    {on && <StopButton key='stop' onClick={() => this.operation('shutdown')} title={this.state.status} />}
    {on && <ReloadButton key='reload' onClick={() => this.operation('reboot')} title={this.state.status} />}
    {on && <PauseButton key='suspend' onClick={() => this.operation('suspend')} title={this.state.status} />}
    {(on || this.state.state === 'suspended') && <ShutdownButton key='shutdown' onClick={() => this.operation('off')} title={this.state.status} />}
    {off && <SnapshotButton key='snapshot' onClick={() => this.snapshot('create')} title='Take snapshot' />}
    {off && <ItemsButton key='snapshots' onClick={() => this.props.changeContent(<Snapshots key={'hypervisor_snapshots_'+this.props.vm_id} device_id={this.props.device_id} vm_id={this.props.vm_id} type={this.props.type} />)} title='Snapshot info' />}
    {this.state.wait}
   </>
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

 componentDidUpdate(prevProps){
  if (prevProps !== this.props){
   this.componentDidMount()
  }
 }

 componentDidMount(){
  post_call('api/devices/'+this.props.type+'/vm_info',{device_id:this.props.device_id, vm_id:this.props.vm_id}).then(result => {
   if (result.data.device_id === null)
    result.data.device_id = '';
   this.setState(result);
  })
 }

 syncDatabase(){
  post_call('api/devices/'+this.props.type+'/vm_info',{device_id:this.props.device_id, vm_id:this.props.vm_id, op:'update'}).then(result => this.setState(result))
 }

 updateInfo(){
  post_call('api/devices/'+this.props.type+'/vm_map',{device_uuid:this.state.data.device_uuid, device_id:this.state.data.device_id, host_id:this.props.device_id, op:'update'}).then(result => this.setState({update:result.update}))
 }

 changeImport = (iif) => import('./interface.jsx').then(lib => this.setState({content:<lib.Info key='interface_info' device_id={this.state.data.device_id} class='virtual' mac={iif.mac} name={iif.name} interface_id={iif.interface_id} description={iif.port} changeSelf={this.changeContent} />}))

 interfaceButton(vm_if,iif){
  if(this.state.data.device_id){
   if (iif.interface_id)
    return <InfoButton key='info' onClick={() => this.changeImport({interface_id:iif.interface_id})} />
   else
    return <AddButton key='add' onClick={() => this.changeImport({...iif, interface_id:'new'})} />
  } else
   return <div />
 }

 render(){
  if (this.state.data) {
   const data = this.state.data;
   return <>
    <InfoArticle key='hyp_article' header='VM info'>
     <InfoColumns key='hyp_ic' columns={3}>
      <TextLine key='name' id='name' text={data.name} /><div />
      <TextInput key='device_id' id='device_id' label='Device ID' value={data.device_id} onChange={this.onChange} /><div />
      <TextLine key='device_name' id='device' label='Device Name' text={data.device_name} /><div />
      <TextLine key='snmp' id='snmp_id' label='SNMP id' text={data.snmp_id} /><div />
      <TextLine key='uuid' id='uuid' label='UUID' text={data.device_uuid} /><div />
      <StateLine key='state' id='state' state={data.state} /><div />
      <TextLine key='config' id='config' text={data.config} /><div />
      {Object.entries(this.state.interfaces).map(row => <Fragment key={row[0]}><TextLine key='interface' id={'interface_'+row[0]} label='Interface' text={`${row[1].name} - ${row[1].mac} - ${row[1].port}`} />{this.interfaceButton(row[0],row[1])}</Fragment>)}
     </InfoColumns>
     <ReloadButton key='reload' onClick={() => this.componentDidMount()} title='Reload' />
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save mapping' />
     <SyncButton key='sync' onClick={() => this.syncDatabase()} title='Resync database with VM info' />
     {data.device_id && <GoButton key='go' onClick={() => this.changeSelf(<DeviceInfo key='device_info' id={data.device_id} changeSelf={this.props.changeSelf} />)} title='VM device info' />}
     <Result key='result' result={JSON.stringify(this.state.update)} />
    </InfoArticle>
    <NavBar />
    {this.state.content}
   </>
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

 listItem = (row) => [row.name,row.id,row.desc,row.created,row.state,<>
  <RevertButton key='revert' onClick={() => this.snapshot('revert',row.id)} title='Revert to snapshot' />
  <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete snapshot' />
 </>]

 render(){
  return <ContentReport key='hyp_snapshot_cr' header={`Snapshot (${this.props.vm_id}) Highest ID:${this.state.highest}`} thead={['Name','ID','Description','Created','State','']} trows={this.state.data} listItem={this.listItem}>
   <ReloadButton key='reload' onClick={() => this.snapshot('list',undefined)} title='Reload list' />
   {this.state.wait}
  </ContentReport>
 }
}
