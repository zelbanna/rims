import React, { Component, Fragment } from 'react';
import { post_call } from './infra/Functions.js';
import { Spinner, LineArticle, ContentReport, ContentList, ContentData } from './infra/UI.jsx';
import { TextInput, SearchInput, SelectInput } from './infra/Inputs.jsx';
import { HrefButton, NetworkButton, ReloadButton, SearchButton, SyncButton } from './infra/Buttons.jsx';

import { Edit as VisualizeEdit } from './visualize.jsx';

// ************** Search **************
//
export class Search extends Component {
  constructor(props){
  super(props)
  this.state = {field:'mac',search:''}
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 onChange = (e) => this.setState({[e.target.name]:e.target.value})

 render() {
  return <LineArticle key='fs_art' header='FDB Search'>
   <SelectInput key='field' id='field' onChange={this.onChange} value={this.state.field}>
    <option value='mac'>MAC</option>
    <option value='device_id'>Device ID</option>
   </SelectInput>
   <TextInput key='search' id='search' onChange={this.onChange} value={this.state.search} placeholder='search' />
   <SearchButton key='fs_btn_search' onClick={() => this.changeContent(<List key='fdb_list' {...this.state} changeSelf={this.props.changeSelf} />)} title='Search FDB' />
  </LineArticle>
 }
}

// *************** Device *****************
//
export class Device extends Component {
 constructor(props){
  super(props)
  this.state = {wait:null}
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 componentDidMount(){
  post_call('api/fdb/list',{field:"device_id",search:this.props.id}).then(result => this.setState(result))
 }

 syncFDB(){
  this.setState({wait:<Spinner />})
  post_call('api/fdb/sync',{id:this.props.id, ip:this.props.ip, type:this.props.type}).then(result => this.setState({wait:null}));
 }

 changeInterface = (interface_id) => import('./interface.jsx').then(lib => this.changeContent(<lib.Info key='interface_info' device_id={this.props.id} interface_id={interface_id} changeSelf={this.changeContent} />))

 listItem = (row,idx) => [row.vlan,row.snmp_index,<HrefButton key={'fd_intf_'+row.interface_id} text={row.name} onClick={() => this.changeInterface(row.interface_id)} />,row.mac]

 render(){
  if (this.state.data)
   return <ContentReport key='fd_cr' header='FDB' thead={['VLAN','SNMP','Interface','MAC']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='fd_btn_reload' onClick={() => this.componentDidMount()} />
    <SyncButton key='fd_btn_sync' onClick={() => this.syncFDB() } title='Resync FDB' />
    {this.state.wait}
   </ContentReport>
  else
   return <Spinner />
 }
}

// *************** List *****************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {searchfield:'', content:null}
 }

 componentDidMount(){
  post_call('api/fdb/list',{search:this.props.search, field:this.props.field, extra:['device_id','hostname']}).then(result => this.setState(result))
 }

 changeSearch = (mac,idx) => this.setState({content:<Info key={'fi_'+idx} mac={mac} />});

 changeVisualize = (device_id) => ('changeSelf' in this.props && this.setState({content:<VisualizeEdit key={'viz_id_' + device_id} type='device' id={device_id} />}));

 searchHandler = (e) => this.setState({searchfield:e.target.value})

 listItem = (row,idx) => [row.device_id,row.hostname,row.vlan,row.snmp_index,row.name,<HrefButton key={'fd_intf_'+idx} text={row.mac} onClick={() => this.changeSearch(row.mac,idx)} />,<NetworkButton key={'fd_map_'+idx} onClick={() => this.changeVisualize(row.device_id)} />]

 render(){
  if (this.state.data){
   const search = this.state.searchfield.toUpperCase();
   const data = (search.length === 0) ? this.state.data : this.state.data.filter(row => row.mac.includes(search))
   return <Fragment key='fl_frag'>
    <ContentList key='fl_cr' header='FDB' thead={['ID','Hostname','VLAN','SNMP','Interface','MAC','']} trows={data} listItem={this.listItem}>
     <ReloadButton key='fl_btn_reload' onClick={() => this.componentDidMount()} />
     <SearchInput key='fl_search' searchHandler={this.searchHandler} value={this.state.searchfield} placeholder='Search MAC' />
    </ContentList>
    <ContentData key='fl_content'>{this.state.content}</ContentData>
   </Fragment>
  } else
   return <Spinner />
 }
}

// *************** Info *****************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  post_call('api/fdb/search',{mac:this.props.mac}).then(result => this.setState(result))
 }

 render(){
  if (this.state.device)
   return <ContentReport key='fd_cr' header={`${this.state.device.hostname} (${this.state.device.id})`} thead={['ID','Name','Description']} trows={this.state.interfaces} listItem={(row) => [row.interface_id,row.name,row.description]} />
  else if (this.state.status)
   return <LineArticle key='fd_la' header='Search error'>Search result: {this.state.info}</LineArticle>
  else
   return <Spinner />
 }
}
