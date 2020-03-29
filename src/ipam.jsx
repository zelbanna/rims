import React, { Fragment, Component } from 'react'
import { rest_call, rnd, int2ip } from './infra/Functions.js';
import { Spinner, InfoColumns, StateMap, Result, RimsContext, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, ViewButton, LogButton, ConfigureButton, ItemsButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';

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
   <ConfigureButton key={'net_btn_info_'+row.id} onClick={() => this.changeContent(<NetworkInfo key={'network_'+row.id} id={row.id} />) } />
   <ItemsButton key={'net_btn_items_'+row.id} onClick={() => this.changeContent(<AddressList changeSelf={this.changeContent} key={'items_'+row.id} network_id={row.id} />) } />
   <ViewButton key={'net_btn_layout_'+row.id} onClick={() => this.changeContent(<Layout changeSelf={this.changeContent} key={'items_'+row.id} network_id={row.id} />) } />
   <DeleteButton key={'net_btn_delete_'+row.id} onClick={() => this.deleteList('api/ipam/network_delete',row.id,'Really delete network') } />
  </Fragment>
 ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='nl_fragment'>
   <ContentList key='nl_cl' header='Networks' thead={['ID','Network','Description','DHCP','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='nl_btn_reload'  onClick={() => this.componentDidMount() } />
    <AddButton key='nl_btn_add' onClick={() => this.changeContent(<NetworkInfo key={'network_new_'+rnd()} id='new' />) } />
    <LogButton key='nl_btn_doc' onClick={() => this.changeContent(<Leases key='network_leases' />)} />
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

 onChange = (e) => {
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
     <h1>Network</h1>
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
     <SaveButton key='network_btn_save' onClick={() => this.updateInfo('api/ipam/network_info')} />
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

 changeDevice(id){
  import('./device.jsx').then(lib => {
   var Device = lib.Info;
   this.props.changeSelf(<Device key={'di_'+id} id={id} changeSelf={this.props.changeSelf} />);
  })
 }

 createDevice(network,ip){
  import('./device.jsx').then(lib => {
   var New = lib.New;
   this.props.changeSelf(<New key={'dn_new'} ipam_network_id={network} ip={ip} />);
  })
 }

 render(){
  if (!this.state)
   return <Spinner />
  else {
   const layout = [];
   for (let cnt = 0; cnt <= this.state.size; cnt++){
    if (this.state.data.hasOwnProperty(this.state.start + cnt))
     layout.push(<button key={'btn_' + this.state.start + cnt} className='info ipam red' onClick={() => this.changeDevice(this.state.data[this.state.start + cnt].device_id)}>{cnt%256}</button>)
    else
     layout.push(<button key={'btn_' + this.state.start + cnt} className='info ipam green' onClick={() => this.createDevice(this.props.network_id,int2ip(this.state.start + cnt))}>{cnt%256}</button>)
   }
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
   <ConfigureButton key={'al_btn_info'+row.id} onClick={() => this.props.changeSelf(<AddressInfo id={row.id} />)} />
   <DeleteButton key={'al_btn_delete'+row.id} onClick={() => this.deleteList('api/ipam/address_delete',row.id,'Really delete address?')} />
  </Fragment>]

 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 render(){
  return <ContentReport key='al_cr' header='Allocated IP Addresses' thead={['ID','IP','Hostname','Domain','A','PTR','','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <ReloadButton key='al_btn_reload' onClick={() => this.componentDidMount() } />
   <AddButton key='al_btn_add' onClick={() => this.props.changeSelf(<AddressInfo key={'address_new_' + rnd()} network_id={this.props.network_id} id='new' />) } />
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

 onChange = (e) => {
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
     <InfoColumns key='ip_content'>
      <TextLine key='id' id='id' label='ID' text={this.state.data.id} />
      <TextLine key='network' id='network' text={this.state.extra.network} />
      <TextInput key='ip' id='ip' label='IP'  value={this.state.data.ip} onChange={this.onChange} />
      <TextInput key='a_id' id='a_id' label='A_id' value={this.state.data.a_id} onChange={this.onChange} />
      <TextInput key='ptr_id' id='ptr_id' label='PTR_id' value={this.state.data.ptr_id} onChange={this.onChange} />
      <TextInput key='hostname' id='hostname' value={this.state.data.hostname} onChange={this.onChange} />
      <SelectInput key='a_domain_id' id='a_domain_id' label='Domain' value={this.state.data.a_domain_id} onChange={this.onChange}>{this.state.domains.map((row,idx) => <option key={'ai_dom_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='ip_save' onClick={() => this.updateInfo('api/ipam/address_info')} />
     <Result key='ip_operation' result={this.state.hasOwnProperty('info') ? `${this.state.status} ${this.state.info}` : this.state.status} />
    </article>
   );
  else
   return <Spinner />
 }
}
