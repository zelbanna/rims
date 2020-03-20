import React, { Fragment, Component } from 'react'
import { rest_call, rnd, int2ip } from './infra/Functions.js';
import { Spinner, InfoCol2, StateMap } from './infra/Generic.js';
import { ListBase, ReportBase, InfoBase, MainBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';
import { Info as DeviceInfo, New as DeviceNew } from './Device.jsx';

// CONVERTED ENTIRELY

// *************** Main ***************
//
export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state.content = <NetworkList key='ipam_list' />
 }
}

// *************** NetworkList ***************
//
export class NetworkList extends ListBase {
 constructor(props){
  super(props)
  this.header='Networks'
  this.thead = ['ID','Network','Description','DHCP','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<NetworkInfo key={'network_new_' + rnd()} id='new' />) } />,
   <InfoButton key='document' type='document' onClick={() => this.changeContent(<Leases key='network_leases' />)} />
  ]
 }

 componentDidMount(){
  rest_call('api/ipam/network_list').then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.netasc,row.description,row.service,<Fragment key={'network_buttons_'+row.id}>
   <InfoButton key={'net_info_'+row.id} type='info'  onClick={() => this.changeContent(<NetworkInfo key={'network_'+row.id} id={row.id} />) } />
   <InfoButton key={'net_items_'+row.id} type='items' onClick={() => this.changeContent(<AddressList changeSelf={this.changeContent} key={'items_'+row.id} network_id={row.id} />) } />
   <InfoButton key={'net_layout_'+row.id} type='devices' onClick={() => this.changeContent(<Layout changeSelf={this.changeContent} key={'items_'+row.id} network_id={row.id} />) } />
   <InfoButton key={'net_delete_'+row.id} type='delete' onClick={() => this.deleteList('api/ipam/network_delete',row.id,'Really delete network') } />
  </Fragment>
 ]
}

// *************** NetworkInfo ***************
//
class NetworkInfo extends InfoBase {

 componentDidMount(){
  rest_call('api/ipam/network_info',{id:this.props.id}).then(result => this.setState(result))
 }

 infoItems = () => [
    {tag:'span', id:'id', text:'ID', value:this.state.data.id},
    {tag:'input', type:'text', id:'description', text:'Description', value:this.state.data.description},
    {tag:'input', type:'text', id:'network', text:'Network', value:this.state.data.network},
    {tag:'input', type:'text', id:'mask', text:'Mask', value:this.state.data.mask},
    {tag:'input', type:'text', id:'gateway', text:'Gateway', value:this.state.data.gateway},
    {tag:'select', id:'server_id', text:'Server', value:this.state.data.server_id, options:this.state.servers.map(row => ({value:row.id, text:`${row.service}@${row.node}`}))},
    {tag:'select', id:'reverse_zone_id', text:'Reverse Zone', value:this.state.data.reverse_zone_id, options:this.state.domains.map(row => ({value:row.id, text:`${row.server} (${row.name})`}))},
   ]

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Network Info</h1>
     <InfoCol2 key='network_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='network_save' type='save' onClick={() => this.updateInfo('api/ipam/network_info')} />
    </article>
   );
  else
   return <Spinner />
 }
}

// *************** Network Layout ***************
//
class Layout extends Component {

 componentDidMount(){
  rest_call('api/ipam/address_list',{network_id:this.props.network_id,dict:'ip_integer',extra:['device_id']}).then(result => this.setState({...result, start_address:parseInt(result.network.split(".")[3])}))
 }

 render(){
  if (!this.state)
   return <Spinner />
  else {
   const layout = [<button key={'btn_' + this.state.start_address} className='info ipam blue'>{this.state.start_address}</button>]
   for (let cnt = 1; cnt < this.state.size; cnt++){
    if (this.state.data.hasOwnProperty(this.state.start + cnt))
     layout.push(<button key={'btn_' + this.state.start + cnt} className='info ipam red' onClick={() => this.props.changeSelf(<DeviceInfo key={this.state.data[this.state.start + cnt].device_id} id={this.state.data[this.state.start + cnt].device_id} />)} >{cnt%256}</button>)
    else
     layout.push(<button key={'btn_' + this.state.start + cnt} className='info ipam green' onClick={() => this.props.changeSelf(<DeviceNew key={this.state.start + cnt} ipam_network_id={this.props.network_id} ip={int2ip(this.state.start + cnt)} />)} >{cnt%256}</button>)
   }
   layout.push(<button key={'btn_' + (this.state.start + this.state.size - 1)} className='info ipam blue'>{(this.state.start + this.state.size - 1) % 256}</button>)
   return (
    <article>
     <h1>{this.state.network}/{this.state.mask}</h1>
     {layout}
    </article>
   );
  }
 }
}

// *************** Leases ***************
//
class Leases extends ReportBase {
 constructor(props){
  super(props)
  this.header = 'Leases'
  this.thead = ['IP','Mac','Hostname','OUI','Starts','End']
 }

 componentDidMount(){
  rest_call('api/ipam/server_leases',{type:'active'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.ip,row.mac,row.hostname,row.oui,row.starts,row.ends]

}

// *************** Address List ***************
//
class AddressList extends ReportBase{
 constructor(props){
  super(props)
  this.header = 'Allocated IP Addresses'
  this.thead = ['ID','IP','Hostname','Domain','A_id','PTR_id','','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.props.changeSelf(<AddressInfo key={'address_new_' + rnd()} network_id={this.props.network_id} id='new' />) } />,
  ]
 }

 componentDidMount(){
  rest_call('api/ipam/address_list',{network_id:this.props.network_id,extra:['a_id','ptr_id','hostname','a_domain_id','device_id']}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.ip,row.hostname,row.domain,row.a_id,row.ptr_id,<StateMap key={'ip_state_'+row.id} state={row.state} />,<Fragment key={'ip_button_'+row.id}>
   <InfoButton type='info' onClick={() => this.props.changeSelf(<AddressInfo id={row.id} />)} />
   <InfoButton type='delete' onClick={() => this.deleteList('api/ipam/address_delete',row.id,'Really delete address?')} />
  </Fragment>]
}

// *************** Address Info ***************
//
class AddressInfo extends InfoBase {

 componentDidMount(){
  rest_call('api/ipam/address_info',{id:this.props.id,network_id:this.props.network_id}).then(result => this.setState(result))
  rest_call('api/dns/domain_list',{'filter':'forward'}).then(result => this.setState({domains:result.data}))
 }

 infoItems = () => [
  {tag:'span', id:'id', text:'ID', value:this.state.data.id},
  {tag:'span', id:'network', text:'Network', value:this.state.extra.network},
  {tag:'input', type:'text', id:'ip', text:'IP', value:this.state.data.ip},
  {tag:'input', type:'text', id:'a_id', text:'A_id', value:this.state.data.a_id},
  {tag:'input', type:'text', id:'ptr_id', text:'PTR_id', value:this.state.data.ptr_id},
  {tag:'input', type:'text', id:'hostname', text:'Hostname', value:this.state.data.hostname},
  {tag:'select', id:'a_domain_id', text:'Domain', value:this.state.data.a_domain_id, options:this.state.domains.map(row => ({value:row.id, text:row.name}))}
 ]

 render() {
  if (this.state && this.state.data && this.state.domains)
   return (
    <article className='info'>
     <h1>IP Address</h1>
     <InfoCol2 key='ip_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='ip_save' type='save' onClick={() => this.updateInfo('api/ipam/address_info')} />
     <span className='results' id='ip_operation'>{this.state.status} {this.state.info}</span>
    </article>
   );
  else
   return <Spinner />
 }
}
