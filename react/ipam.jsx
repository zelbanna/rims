import React, { Component } from 'react'
import { post_call, rnd, int2ip, ip2int } from './infra/Functions.js';
import { Spinner, Article, InfoArticle, InfoColumns, StateLeds, Result, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { CheckboxInput, TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { AddButton, BackButton, DeleteButton, ViewButton, LogButton, ConfigureButton, ItemsButton, ReloadButton, CheckButton, SaveButton, IpamGreenButton, IpamRedButton, IpamGreyButton } from './infra/Buttons.jsx';
// import styles from './infra/ui.module.css';

// *************** Main ***************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <NetworkList key='network_list' />
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <>{this.state}</>
 }
}

// *************** NetworkList ***************
//
export class NetworkList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/ipam/network_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,
   row.netasc,
   row.description,
   row.service,
   <>
    <ConfigureButton key='conf' onClick={() => this.changeContent(<NetworkInfo key={'network_'+row.id} id={row.id} />)} title='Edit network properties' />
    <ItemsButton key='items' onClick={() => this.changeContent(<AddressList key={'address_list_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='View addresses' />
    {row.class === 'v4' && <ViewButton key='layout' onClick={() => this.changeContent(<Layout key={'address_layout_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='View usage map' />}
    {row.class === 'v4' && <CheckButton key='resv' onClick={() => this.changeContent(<ReservationList key={'resv_list_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='Reserved addresses for network' />}
    <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete network' />
    <ReloadButton key='reset' onClick={() => this.resetStatus(row.id)} title='Reset state for network addresses' />
  </>]

 deleteList = (id) => (window.confirm('Really delete network') && post_call('api/ipam/network_delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 resetStatus = (id) => post_call('api/ipam/clear',{network_id:id}).then(result => this.setState({result:result.count}))

 render(){
  return <>
   <ContentList key='cl' header='Networks' thead={['ID','Network','Description','DHCP','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='reload'  onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<NetworkInfo key={'network_new_'+rnd()} id='new' />)} title='Add network' />
    <LogButton key='leases' onClick={() => this.changeContent(<Leases key='network_leases' />)} title='View IPAM/DHCP leases' />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </>
 }
}

// *************** NetworkInfo ***************
//
class NetworkInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true };
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => post_call('api/ipam/network_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  post_call('api/ipam/network_info',{id:this.props.id, extra:['servers','domains']}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return <InfoArticle key='net_article' header='Network'>
     <InfoColumns key='network_content'>
      <TextLine key='id' id='id' label='ID' text={this.state.data.id} />
      <TextInput key='description' id='description'  value={this.state.data.description} onChange={this.onChange} />
      <TextInput key='network' id='network' value={this.state.data.network} onChange={this.onChange} />
      <TextInput key='mask' id='mask' value={this.state.data.mask} onChange={this.onChange} />
      <TextInput key='gateway' id='gateway' value={this.state.data.gateway} onChange={this.onChange} />
      <SelectInput key='server_id' id='server_id' label='Server' value={this.state.data.server_id} onChange={this.onChange}>
       {this.state.servers.map((row,idx) => <option key={idx} value={row.id}>{`${row.service}@${row.node}`}</option>)}
      </SelectInput>
      <SelectInput key='reverse_zone_id' id='reverse_zone_id' label='Reverse Zone' value={this.state.data.reverse_zone_id} onChange={this.onChange}>
       {this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{`${row.server} (${row.name})`}</option>)}
      </SelectInput>
     </InfoColumns>
     <SaveButton key='network_btn_save' onClick={() => this.updateInfo()} title='Save' />
    </InfoArticle>
  else
   return <Spinner />
 }
}

// *************** Network Layout ***************
//
class Layout extends Component {

 componentDidMount(){
  post_call('api/ipam/address_list',{network_id:this.props.network_id,dict:'ip_integer',extra:['device_id','reservation','ip_integer']}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem)

 changeDevice = (id) => import('./device.jsx').then(lib => this.changeContent(<lib.Info key={'di_'+id} id={id} />))

 createDevice = (network,ip) => import('./device.jsx').then(lib =>  this.changeContent(<lib.New key={'dn_new'} ipam_network_id={network} ip={ip} />))

 render(){
  if (!this.state)
   return <Spinner />
  else {
   const data = this.state.data;
   const start = ip2int(this.state.network);
   const layout = [];
   for (let cnt = 0; cnt < this.state.size; cnt++){
    const pos = start + cnt;
    if (!(pos in data))
     layout.push(<IpamGreenButton key={'btn_' + pos} onClick={() => this.createDevice(this.props.network_id,int2ip(pos))} text={cnt%256} />)
    else if (data[pos].device_id)
     layout.push(<IpamRedButton key={'btn_' + pos} onClick={() => this.changeDevice(data[pos].device_id)} text={cnt%256} />)
    else
     layout.push(<IpamGreyButton key={'btn_' + pos} text={cnt%256} />)
   }
   return <Article key='il_art' header={this.state.network + '/' + this.state.mask}>
    {layout}
   </Article>
  }
 }
}

// *************** Leases ***************
//
class Leases extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/ipam/server_leases',{type:'active'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.ip,row.mac,row.hostname,row.oui,row.starts,row.ends]

 render(){
  return <ContentReport key='lease_cr' header='Leases' thead={['IP','Mac','Hostname','OUI','Starts','End']} trows={this.state.data} listItem={this.listItem} />
 }
}

// *************** Address List ***************
//
class AddressList extends Component{
 constructor(props){
  super(props)
  this.state = {data:null,result:null}
 }

 componentDidMount(){
  post_call('api/ipam/address_list',{network_id:this.props.network_id,extra:['hostname','a_domain_id','device_id']}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem)

 listItem = (row) => [row.id,row.ip,row.hostname,row.domain,<>
   { (row.monitor === 'true') ? <StateLeds key='state' state={row.state} /> : '' }
   <ConfigureButton key='info' onClick={() => this.changeContent(<AddressInfo key={'address_info_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title='Edit address entry' />
   <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete address entry' />
  </>]

 deleteList = (id) => (window.confirm('Delete address?') && post_call('api/ipam/address_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 render(){
  return <ContentReport key='al_cr' header='Allocated IP Addresses' thead={['ID','IP','Hostname','Domain','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <ReloadButton key='al_btn_reload' onClick={() => this.componentDidMount() } />
   <AddButton key='al_btn_add' onClick={() => this.changeContent(<AddressInfo key={'address_new_' + rnd()} network_id={this.props.network_id} id='new' />)} title='Add address entry' />
  </ContentReport>
 }
}

// *************** Address Info ***************
//
export class AddressInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})

 updateInfo = () => {
  this.setState({status:undefined});
  post_call('api/ipam/address_info',{op:'update', ...this.state.data}).then(result => this.setState(result))
 }

 componentDidMount(){
  post_call('api/ipam/address_info',{id:this.props.id,network_id:this.props.network_id}).then(result => this.setState(result))
  post_call('api/dns/domain_list',{'filter':'forward'}).then(result => this.setState({domains:result.data}))
 }

 render() {
  if (this.state && this.state.data && this.state.domains){
   let result = '';
   if (this.state.status) {
    if (this.state.status === 'OK')
     result = 'OK';
    else
     result = this.state.info
   }
   return <InfoArticle key='ip_article' header='IP Address'>
     <InfoColumns key='ip_content'>
      <TextLine key='id' id='id' label='ID' text={this.state.data.id} />
      <TextLine key='network' id='network' text={this.state.extra.network} />
      <TextInput key='ip' id='ip' label='IP'  value={this.state.data.ip} onChange={this.onChange} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} title='Hostname when creating FQDN for DNS entry' />
      <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <CheckboxInput key='monitor' id='monitor' value={this.state.data.monitor} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='ip_btn_save' onClick={() => this.updateInfo()} title='Save' />
     <Result key='ip_operation' result={result} />
    </InfoArticle>
  } else
   return <Spinner />
 }
}

// *************** Reservation List ***************
//
class ReservationList extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  post_call('api/ipam/reservation_list',{network_id:this.props.network_id}).then(result => this.setState(result))
 }

 deleteList = (id) => post_call('api/ipam/reservation_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))}))

 listItem = (row,idx) => [row.ip,row.type,<DeleteButton key={'resv_list_delete_'+row.id} onClick={() => this.deleteList(row.id)} />]

 addEntry = () => this.props.changeSelf(<ReservationNew key={'resv_new_'+this.props.network_id} network_id={this.props.network_id} changeSelf={this.props.changeSelf} />);

 render() {
  if(this.state.data){
   return <ContentReport key={'resv_list_'+this.props.server_id} header='Reservations' thead={['IP','Type','']} trows={this.state.data} listItem={this.listItem}>
    <AddButton key='resv_list_add_btn' onClick={() => this.addEntry()} />
   </ContentReport>
  } else
   return <Spinner />
 }
}

// *************** Reservation New ****************
//
class ReservationNew extends Component {
  constructor(props){
  super(props);
  this.state = {ip:'',start:'',end:'', result:undefined,type:'dhcp'}
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 componentDidMount(){
  post_call('api/ipam/network_info',{'id':this.props.network_id}).then(result => this.setState({...result.data}))
  post_call('api/dns/domain_list',{'filter':'forward'}).then(result => this.setState({domains:result.data}))
 }

 updateInfo = () => post_call('api/ipam/reservation_new',{network_id:this.props.network_id, ip:this.state.ip, type:this.state.type, a_domain_id:this.state.a_domain_id, start:this.state.start, end:this.state.end}).then(result => this.setState({result:result}))

 render() {
  if (this.state.domains){
   const network_id = this.props.network_id;
   const result = (this.state.result) ? JSON.stringify(this.state.result.resv) : '';
   return <InfoArticle key='dn_article' header='Reservation Address/Scope'>
    <span>Allocate address with either 'ip' or 'start' to 'end' (e.g. a scope)</span>
    <InfoColumns key='dn_content'>
     <TextLine key='id' id='network_id' label='Network ID' text={network_id} />
     <TextLine key='network' id='network' text={this.state.network + '/' + this.state.mask} />
     <TextInput key='ip' id='ip' label='IP' value={this.state.ip} onChange={this.onChange} />
     <TextInput key='start' id='start' label='Start IP' value={this.state.start} onChange={this.onChange} />
     <TextInput key='end' id='end' label='End IP' value={this.state.end} onChange={this.onChange} />
     <SelectInput key='type' id='type' label='Type' value={this.state.type} onChange={this.onChange}>
      <option key='dhcp' value='dhcp'>dhcp</option>
      <option key='reservation' value='reservation'>reservation</option>
     </SelectInput>
     <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={idx} value={row.id}>{row.name}</option>)}</SelectInput>
    </InfoColumns>
    {this.props.changeSelf && <BackButton key='dn_btn_back' onClick={() => this.props.changeSelf(<ReservationList key={'resv_list_' + network_id} network_id={network_id} changeSelf={this.props.changeSelf} />)} />}
    <SaveButton key='dn_btn_save' onClick={() => this.updateInfo()} title='Save' />
    <Result key='dn_operation' result={result} />
   </InfoArticle>
  } else
   return <Spinner />
 }
}
