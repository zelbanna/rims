
import React, { Fragment, Component } from 'react'
import { post_call, rnd, int2ip } from './infra/Functions.js';
import { Spinner, Article, InfoArticle, InfoColumns, StateLeds, Result, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, ViewButton, LogButton, ConfigureButton, HrefButton, ItemsButton, ReloadButton, SaveButton, IpamGreenButton, IpamRedButton, IpamGreyButton } from './infra/Buttons.jsx';

// *************** Main ***************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <NetworkList key='network_list' />
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
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

 listItem = (row) => [row.id,row.netasc,row.description,<HrefButton key={'net_btn_dhcp_'+row.id} text={row.service} onClick={() => this.changeContent(<DhcpList key={'dhcp_list_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='DHCP allocation for network' />,<Fragment key={'network_buttons_'+row.id}>
   <ConfigureButton key={'net_btn_info_'+row.id} onClick={() => this.changeContent(<NetworkInfo key={'network_'+row.id} id={row.id} />)} title='Edit network properties' />
   <ItemsButton key={'net_btn_items2_'+row.id} onClick={() => this.changeContent(<AddressList key={'address_list_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='View addresses' />
   <ViewButton key={'net_btn_layout_'+row.id} onClick={() => this.changeContent(<Layout key={'address_layout_'+row.id} network_id={row.id} changeSelf={this.changeContent} />)} title='View usage map' />
   <DeleteButton key={'net_btn_delete_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete network' />
   <ReloadButton key={'net_btn_rset_'+row.id} onClick={() => this.resetStatus(row.id)} title='Reset state for network addresses' />
  </Fragment>
 ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete network') && post_call('api/ipam/network_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 resetStatus = (id) => post_call('api/ipam/clear',{network_id:id}).then(result => this.setState({result:result.count}))

 render(){
  return <Fragment key='nl_fragment'>
   <ContentList key='nl_cl' header='Networks' thead={['ID','Network','Description','DHCP','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='nl_btn_reload'  onClick={() => this.componentDidMount() } />
    <AddButton key='nl_btn_add' onClick={() => this.changeContent(<NetworkInfo key={'network_new_'+rnd()} id='new' />)} title='Add network' />
    <LogButton key='nl_btn_doc' onClick={() => this.changeContent(<Leases key='network_leases' />)} title='View IPAM/DHCP leases' />
   </ContentList>
   <ContentData key='nl_cd'>{this.state.content}</ContentData>
  </Fragment>
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
  post_call('api/ipam/network_info',{id:this.props.id}).then(result => this.setState(result))
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
       {this.state.servers.map((row,idx) => <option key={'ni_srv_'+idx} value={row.id}>{`${row.service}@${row.node}`}</option>)}
      </SelectInput>
      <SelectInput key='reverse_zone_id' id='reverse_zone_id' label='Reverse Zone' value={this.state.data.reverse_zone_id} onChange={this.onChange}>
       {this.state.domains.map((row,idx) => <option key={'ni_rzone_'+idx} value={row.id}>{`${row.server} (${row.name})`}</option>)}
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
  post_call('api/ipam/address_list',{network_id:this.props.network_id,dict:'ip_integer',extra:['device_id','dhcp']}).then(result => this.setState({...result, start_address:parseInt(result.network.split('.')[3])}))
 }

 changeContent = (elem) => this.props.changeSelf(elem)

 changeDevice = (id) => import('./device.jsx').then(lib => this.changeContent(<lib.Info key={'di_'+id} id={id} />))

 createDevice = (network,ip) => import('./device.jsx').then(lib =>  this.changeContent(<lib.New key={'dn_new'} ipam_network_id={network} ip={ip} />))

 render(){
  if (!this.state)
   return <Spinner />
  else {
   const data = this.state.data;
   const start = this.state.start;
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

 listItem = (row) => [row.id,row.ip,row.hostname,row.domain,<Fragment key={'ip_button_'+row.id}>
   <StateLeds state={row.state} />
   <ConfigureButton key={'al_btn_info'+row.id} onClick={() => this.changeContent(<AddressInfo key={'address_info_'+row.id} id={row.id} />)} title='Edit address entry' />
   <DeleteButton key={'al_btn_delete'+row.id} onClick={() => this.deleteList(row.id)} title='Delete address entry' />
  </Fragment>]

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

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

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
      <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'ai_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='ip_save' onClick={() => this.updateInfo()} title='Save' />
     <Result key='ip_operation' result={result} />
    </InfoArticle>
  } else
   return <Spinner />
 }
}

// *************** DHCP List ***************
//
class DhcpList extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  post_call('api/dhcp/list',{network_id:this.props.network_id}).then(result => this.setState(result))
 }

 deleteList = (id) => (window.confirm('Really delete DHCP ip?') && post_call('api/dhcp/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 listItem = (row,idx) => [row.id, row.ip,<DeleteButton key={'dhcp_list_delete_'+row.id} onClick={() => this.deleteList(row.id)} />]

 addEntry = () => this.props.changeSelf(<DhcpNew key={'dhcp_new_'+this.props.network_id} network_id={this.props.network_id} changeSelf={this.props.changeSelf} />);

 render() {
  if(this.state.data){
   return <ContentReport key={'dhcp_list_'+this.props.server_id} header='DHCP allocation' thead={['ID','IP','']} trows={this.state.data} listItem={this.listItem}>
    <AddButton key='dhcp_list_add_btn' onClick={() => this.addEntry()} />
   </ContentReport>
  } else
   return <Spinner />
 }
}

// *************** DHCP New ****************
//
class DhcpNew extends Component {
  constructor(props){
  super(props);
  this.state = {}
 }

 render(){
  return <div>TBD</div>
 }
}

