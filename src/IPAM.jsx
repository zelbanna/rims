import React, { Fragment, Component } from 'react'
import { rest_call, rnd, int2ip } from './infra/Functions.js';
import { Spinner, InfoCol2, StateMap, Result, RimsContext, ContentList, ContentData, ContentReport } from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.jsx';
import { TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { Info as DeviceInfo, New as DeviceNew } from './Device.jsx';

// CONVERTED ENTIRELY

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
Main.contextType = RimsContext;

// *************** NetworkList ***************
//
export class NetworkList extends Component {
 constructor(props){
  super(props)
  this.state = {}
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

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='nl_fragment'>
   <ContentList key='nl_cl' header='Networks' thead={['ID','Network','Description','DHCP','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <InfoButton key='nl_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='nl_btn_add' type='add' onClick={() => this.changeContent(<NetworkInfo key={'network_new_' + rnd()} id='new' />) } />
    <InfoButton key='nl_btn_document' type='document' onClick={() => this.changeContent(<Leases key='network_leases' />)} />
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

 changeHandler = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/ipam/network_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Network Info</h1>
     <InfoCol2 key='network_content'>
      <TextLine key='id' id='id' label='ID' text={this.state.data.id} />
      <TextInput key='description' id='description'  value={this.state.data.description} changeHandler={this.changeHandler} />
      <TextInput key='network' id='network' value={this.state.data.network} changeHandler={this.changeHandler} />
      <TextInput key='mask' id='mask' value={this.state.data.mask} changeHandler={this.changeHandler} />
      <TextInput key='gateway' id='gateway' value={this.state.data.gateway} changeHandler={this.changeHandler} />
      <SelectInput key='server_id' id='server_id' label='Server' value={this.state.data.server_id} options={this.state.servers.map(row => ({value:row.id, text:`${row.service}@${row.node}`}))} changeHandler={this.changeHandler} />
      <SelectInput key='reverse_zone_id' id='reverse_zone_id' label='Reverse Zone' value={this.state.data.reverse_zone_id} options={this.state.domains.map(row => ({value:row.id, text:`${row.server} (${row.name})`}))} changeHandler={this.changeHandler} />
     </InfoCol2>
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
class Leases extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/ipam/server_leases',{type:'active'}).then(result => this.setState(result))
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
  rest_call('api/ipam/address_list',{network_id:this.props.network_id,extra:['a_id','ptr_id','hostname','a_domain_id','device_id']}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.ip,row.hostname,row.domain,row.a_id,row.ptr_id,StateMap({state:row.state}),<Fragment key={'ip_button_'+row.id}>
   <InfoButton type='info' onClick={() => this.props.changeSelf(<AddressInfo id={row.id} />)} />
   <InfoButton type='delete' onClick={() => this.deleteList('api/ipam/address_delete',row.id,'Really delete address?')} />
  </Fragment>]

 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 render(){
  return <ContentReport key='al_cr' header='Allocated IP Addresses' thead={['ID','IP','Hostname','Domain','A_id','PTR_id','','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />
   <InfoButton key='add' type='add' onClick={() => this.props.changeSelf(<AddressInfo key={'address_new_' + rnd()} network_id={this.props.network_id} id='new' />) } />
  </ContentReport>
 }
}

// *************** Address Info ***************
//
class AddressInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 changeHandler = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/ipam/address_info',{id:this.props.id,network_id:this.props.network_id}).then(result => this.setState(result))
  rest_call('api/dns/domain_list',{'filter':'forward'}).then(result => this.setState({domains:result.data}))
 }

 render() {
  if (this.state && this.state.data && this.state.domains)
   return (
    <article className='info'>
     <h1>IP Address</h1>
     <InfoCol2 key='ip_content'>
      <TextLine key='id' id='id' label='ID' text={this.state.data.id} />
      <TextLine key='network' id='network' text={this.state.extra.network} />
      <TextInput key='ip' id='ip' label='IP'  value={this.state.data.ip} changeHandler={this.changeHandler} />
      <TextInput key='a_id' id='a_id' label='A_id' value={this.state.data.a_id} changeHandler={this.changeHandler} />
      <TextInput key='ptr_id' id='ptr_id' label='PTR_id' value={this.state.data.ptr_id} changeHandler={this.changeHandler} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} changeHandler={this.changeHandler} />
      <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.data.a_domain_id} options={this.state.domains.map(row => ({value:row.id, text:row.name}))} changeHandler={this.changeHandler} />
     </InfoCol2>
     <InfoButton key='ip_save' type='save' onClick={() => this.updateInfo('api/ipam/address_info')} />
     <Result key='ip_operation' result={this.state.hasOwnProperty('info') ? `${this.state.status} ${this.state.info}` : this.state.status} />
    </article>
   );
  else
   return <Spinner />
 }
}
