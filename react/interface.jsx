import React, { Component, Fragment } from 'react'
import { post_call, rnd } from './infra/Functions.js';
import { Spinner, StateLeds, Article, LineArticle, InfoArticle, InfoColumns, Result, ContentReport } from './infra/UI.jsx';
import { CheckboxInput, TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { AddButton, BackButton, DeleteButton,ForwardButton, GoButton, HealthButton, InfoButton, ItemsButton, LinkButton, ReloadButton, RemoveButton, RevertButton, SaveButton, SearchButton, SyncButton, HrefButton, UnlinkButton, TextButton } from './infra/Buttons.jsx';
import styles from './infra/ui.module.css';

// *************** List ****************
//
export class List extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/interface/list',{device_id:this.props.device_id}).then(result => this.setState(result));
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 deleteList = (interface_id,name) => (window.confirm('Really delete interface ' + name) && post_call('api/interface/delete', {interfaces:[interface_id]}).then(result => (result.deleted > 0) && this.setState({data:this.state.data.filter(row => (row.interface_id !== interface_id)),result:JSON.stringify(result.interfaces)})))

 cleanUp = () => (window.confirm('Clean up empty interfaces?') && post_call('api/interface/delete',{device_id:this.props.device_id}).then(result => this.componentDidMount()))

 resetStatus = () => post_call('api/interface/clear',{device_id:this.props.device_id}).then(result => this.componentDidMount())

 discoverInterfaces = () => (window.confirm('Rediscover interfaces?') && post_call('api/interface/snmp',{device_id:this.props.device_id}).then(result => this.componentDidMount()))

 listItem = (row) => [row.snmp_index,row.name,row.mac,(row.ip) ? row.ip : '-',row.description,row.class,
   (row.connection_id) ? <HrefButton key={'conn_btn_'+row.interface_id} text={row.connection_id} onClick={() => this.changeContent(<ConnectionInfo key={'connection_info_' + row.connection_id} id={row.connection_id} device_id={this.props.device_id} changeSelf={this.changeContent} />)} title='Connection information' /> : '-',
   <Fragment>
    <StateLeds key={'il_if_state_' + row.interface_id} state={[row.if_state,row.ip_state]} />
    <InfoButton key={'il_btn_info_' + row.interface_id} onClick={() => this.changeContent(<Info key={row.interface_id} interface_id={row.interface_id} changeSelf={this.props.changeSelf} />)} title='Interface information' />
    {row.snmp_index && <HealthButton key={'il_btn_stats_' + row.interface_id} onClick={() => this.changeContent(<Statistics key={row.interface_id} device_id={this.props.device_id} interface_id={row.interface_id} />)} title='Interface stats' />}
    <DeleteButton key={'il_btn_del_' + row.interface_id} onClick={() => this.deleteList(row.interface_id,row.name)} title='Delete interface' />
    {!row.connection_id && ['wired','optical'].includes(row.class) && <LinkButton key={row.interface_id} onClick={() => this.changeContent(<Info key={'interface_info_' + row.interface_id} op='device' interface_id={row.interface_id} name={row.name} changeSelf={this.props.changeSelf} />)} title='Connect interface' />}
   </Fragment>]

 render(){
  if (this.state.data) {
   return <ContentReport key='il_cl' header='Interfaces' thead={['SNMP','Name','MAC','IP Address','Description','Type','Link','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='il_btn_reload' onClick={() => this.componentDidMount()} />
    <AddButton key='il_btn_add' onClick={() => this.changeContent(<Info key={'interface_info_' + rnd()} device_id={this.props.device_id} interface_id='new' changeSelf={this.props.changeSelf} />) } title='Add interface' />
    <TextButton key='il_btn_rset' onClick={() => this.resetStatus()} title='Reset interface state manually' text='Reset' />
    <TextButton key='il_btn_disc' onClick={() => this.discoverInterfaces()} title='Discover device interfaces' text='Discover' />
    <TextButton key='il_btn_lldp' onClick={() => this.changeContent(<LLDP key='interface_lldp' device_id={this.props.device_id} changeSelf={this.props.changeSelf} />) } title='Map interface connections' text='LLDP' />
    <TextButton key='il_btn_clean' onClick={() => this.cleanUp()} title='Clean up empty interfaces' text='Cleanup' />
    {this.state.loader}
   </ContentReport>
  } else
   return <Spinner />
 }
}

// *************** Info ****************
//
export class Info extends Component {
 constructor(props){
  super(props)
  this.state = {op:this.props.op, connect:{name:'<N/A>',map:false}}
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 componentDidMount(){
  post_call('api/interface/info',{interface_id:this.props.interface_id, mac:this.props.mac, name:this.props.name, device_id:this.props.device_id, class:this.props.class, extra:['classes','ip']}).then(result => this.setState(result));
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});
 updateInfo = () => post_call('api/interface/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 changeIpam = (id) => import('./ipam.jsx').then(lib => this.changeContent(<lib.AddressInfo key={'address_info_'+id} id={id} />));
 deleteIpam = (entry) => (window.confirm('Delete IP mapping?') && post_call('api/ipam/address_delete',{id:this.state.data[entry]}).then(result => ((result.status === 'OK') && this.setState({data:{...this.state.data, [entry]:null}}))));
 clearIpam = (entry) => post_call('api/interface/info',{op:'update', interface_id:this.state.data.interface_id, [entry]:null}).then(result => this.setState(result));
 swapIpam = () => post_call('api/interface/info',{op:'swap', interface_id:this.state.data.interface_id}).then(result => this.setState(result));

 deviceChange = (e) => {
  this.setState({connect:{...this.state.connect, [e.target.name]:e.target.value}});
  if(e.target.name === 'id' && e.target.value.length > 0)
   post_call('api/device/hostname',{id:e.target.value}).then(result => (result && this.setState({connect:{...this.state.connect, found:(result.status === 'OK'), name:(result.status === 'OK') ? result.data : '<N/A>'}})))
 }

 stateInterface = () => (this.state.connect.found && post_call('api/interface/list',{device_id:this.state.connect.id,sort:'name',filter:['connected']}).then(result => this.setState({interfaces:result.data, op:'interface'})))

 interfaceChange = (e) => this.setState({connect:{...this.state.connect, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})
 connectInterface = () => (this.state.connect.interface_id && post_call('api/interface/connect',{a_id:this.state.data.interface_id,b_id:this.state.connect.interface_id,map:this.state.connect.map}).then(result => this.setState({connect:{},op:null})))
 disconnectInterface = () => (this.state.peer && post_call('api/interface/connect',{a_id:this.state.data.interface_id,b_id:this.state.peer.interface_id,disconnect:true}).then(result => this.setState({peer:null})))

 stateIpam = (entry) => {
  if (this.state.domains && this.state.networks)
   this.setState({op:'ipam', entry:entry, ipam:{ip:'<N/A>'}})
  else
   this.setState({op:'wait', entry:entry, ipam:{ip:'<N/A>'}})
  if (!this.state.domains)
   post_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data}));
  if (!this.state.networks)
   post_call('api/ipam/network_list').then(result => this.setState({networks:result.data,op:'ipam'}));
 }

 ipamChange = (e) => this.setState({ipam:{...this.state.ipam, [e.target.name]:e.target.value}});

 searchIP = () => {
  if (this.state.ipam.network_id)
   post_call('api/ipam/address_find',{network_id:this.state.ipam.network_id}).then(result => this.setState({ipam:{...this.state.ipam, ip:result.ip}}))
 }

 createIpam = () => {
  post_call('api/interface/info',{interface_id:this.props.interface_id, op:'update', ipam_record:this.state.ipam, entry:this.state.entry}).then(result => this.setState({...result,op:null}))
 }

 render(){
  if(this.state.data){
   if (this.state.op){
    if(this.state.op === 'device')
     return <LineArticle key='ii_cnct_art'>
     Connect {this.state.data.name} to <TextInput key='ii_cnct_dev' id='id' label='Device ID' onChange={this.deviceChange} /> with name '{this.state.connect.name}'
     <BackButton key='ii_cnct_btn_back' onClick={() => this.setState({op:null})} title='Back' />
     <ForwardButton key='ii_cnct_btn_fwd' onClick={() => this.stateInterface()} title={'Connect interface on ' + this.state.connect.name} />
    </LineArticle>
    else if(this.state.op === 'interface')
     return <LineArticle key='ii_cnct_art'>
      Connect {this.state.data.name} to {this.state.connect.name} on
      <SelectInput key='ii_cnct_int' id='interface_id' label='Interface' value={this.state.connect.interface_id} onChange={this.interfaceChange}>
       {this.state.interfaces.map(row => <option key={row.interface_id} value={row.interface_id}>{`${row.interface_id} (${row.name} - ${row.description})`}</option>)}
      </SelectInput>
      <CheckboxInput key='ii_cnct_map' id='map' value={this.state.connect.map} onChange={this.interfaceChange} />
      <BackButton key='ii_cnct_btn_back' onClick={() => this.setState({op:'device'})} title='Back' />
      <ForwardButton key='ii_cnct_btn_fwd' onClick={() => this.connectInterface()} title='Complete connection' />
     </LineArticle>
    else if (this.state.op === 'ipam'){
     return <InfoArticle key='ii_ipam_article' header='Create IPAM record'>
      <InfoColumns key='ii_ipam_create'>
       <SelectInput key='ii_ipam_net' id='network_id' label='Network' value={this.state.ipam.network_id} onChange={this.ipamChange}>{this.state.networks.map(row => <option key={row.id} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
       <TextInput key='ii_ipam_ip' id='ip' value={this.state.ipam.ip} label='IP' onChange={this.ipamChange} />
       <SelectInput key='ii_ipam_dom' id='a_domain_id' label='Domain' value={this.state.ipam.a_domain_id} onChange={this.ipamChange}>{this.state.domains.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}</SelectInput>
      </InfoColumns>
      <BackButton key='ii_ipam_btn_back' onClick={() => this.setState({op:null})} title='Back'/>
      <SearchButton key='ii_ipam_btn_find' onClick={() => this.searchIP()} title='Search IP within network' />
      <ForwardButton key='ii_ipam_btn_fwd' onClick={() => this.createIpam()} title='Create IPAM entry' />
     </InfoArticle>
    } else if (this.state.op === 'wait')
     return <Spinner />
    else
     return <div>Intermediate interface operation state</div>
   } else {
    const ipam1 = (this.state.data.ipam_id);
    const ipam2 = (this.state.data.ipam_alt_id);
    const peer = (this.state.peer);
    let opresult = '';
    if (this.state.update !== undefined) {
     opresult = 'Updated: ' + JSON.stringify(this.state.update);
    }
    return (<InfoArticle key='ii_article' header='Interface'>
     <InfoColumns key='ii_columns' columns={3}>
      <TextLine key='ii_id' id='id' label='Local ID' text={this.state.data.interface_id} /><div />
      <TextInput key='ii_name' id='name' value={this.state.data.name} onChange={this.onChange} /><div />
      <SelectInput key='ii_class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput><div />
      <TextInput key='ii_description' id='description' value={this.state.data.description} onChange={this.onChange} /><div />
      <TextInput key='ii_snmp_index' id='snmp_index' label='SNMP index' value={this.state.data.snmp_index} onChange={this.onChange} /><div />
      <TextInput key='ii_mac' id='mac' value={this.state.data.mac} onChange={this.onChange} /><div />
      <TextInput key='ii_ipam1_id' id='ipam_id' label='IPAM id' value={this.state.data.ipam_id} onChange={this.onChange} /><div>
       {ipam1 && <GoButton key='ii_btn_ipam1' onClick={() => this.changeIpam(ipam1)} title='Edit IPAM entry' />}
       {ipam1 && <RemoveButton key='ii_btn_remove1' onClick={() => this.clearIpam('ipam_id')} title='Clear IPAM entry' />}
       {ipam1 && <DeleteButton key='ii_btn_delete1' onClick={() => this.deleteIpam('ipam_id')} title='Delete IPAM entry' />}
       {!ipam1 && this.state.data.interface_id !== 'new' && <AddButton key='ii_btn_add1' onClick={() => this.stateIpam('ipam_id')} title='Create IPAM entry' />}
      </div>
      {ipam1 && <Fragment key='ii_ipam1_frag'><TextLine key='ii_ipam1' id='IPAM ip'text={this.state.ip[ipam1]} /><div /></Fragment>}
      <TextInput key='ii_ipam2_id' id='ipam_alt_id' label='IPAM alt id' value={this.state.data.ipam_alt_id} onChange={this.onChange} /><div>
       {ipam2 && <GoButton key='ii_btn_ipam2' onClick={() => this.changeIpam(ipam2)} title='Edit IPAM entry' />}
       {ipam2 && <RemoveButton key='ii_btn_remove2' onClick={() => this.clearIpam('ipam_alt_id')} title='Clear IPAM entry' />}
       {ipam2 && <DeleteButton key='ii_btn_delete2' onClick={() => this.deleteIpam('ipam_alt_id')} title='Delete IPAM entry' />}
       {!ipam2 && this.state.data.interface_id !== 'new' && <AddButton key='ii_btn_add2' onClick={() => this.stateIpam('ipam_alt_id')} title='Create IPAM entry' />}
      </div>
      {ipam2 && <Fragment key='ii_ipam2_frag'><TextLine key='ii_ipam2' id='IPAM alt ip'text={this.state.ip[ipam2]} /><div /></Fragment>}
      {peer && <Fragment key='ii_frag_peer_int'><TextLine key='ii_peer_int_id' id='peer_interface' label='Peer interface' text={this.state.peer.interface_id} /><UnlinkButton key='ii_peer_unlink' onClick={() => this.disconnectInterface()} title='Disconnect from peer' /></Fragment>}
      {peer && <Fragment key='ii_frag_peer_dev'><TextLine key='ii_peer_dev_id' id='peer_device' text={this.state.peer.device_id} /><div/></Fragment>}
     </InfoColumns>
     {'changeSelf' in this.props && <ItemsButton key='ii_btn_list' onClick={() => this.props.changeSelf(<List key='interface_list' device_id={this.state.data.device_id} changeSelf={this.props.changeSelf} />)} title='Interfaces' />}
     <ReloadButton key='ii_btn_reload' onClick={() => this.componentDidMount()} />
     <SaveButton key='ii_btn_save' onClick={() => this.updateInfo()} title='Save interface information' />
     {!peer && this.state.data.interface_id !== 'new' && ['wired','optical'].includes(this.state.data.class) && <LinkButton key='ii_btn_connect' onClick={() => this.setState({op:'device'})} title='Connect peer interface' />}
     {ipam1 && ipam2 && <SyncButton key='ii_btn_swap' onClick={() => this.swapIpam()} title='Swap Primary and Alternative IPAM id' />}
     <Result key='ii_result' result={opresult} />
    </InfoArticle>)
   }
  } else
   return <Spinner />
 }
}

// *************** Statistics ****************
//
class Statistics extends Component {
 constructor(props){
  super(props)
  this.state = {}
  this.canvas = React.createRef()
  this.graph = null
 }

 componentDidMount(){
  import('vis-timeline/standalone/esm/vis-timeline-graph2d').then(vis => post_call('api/statistics/query_interface',{device_id:this.props.device_id, interface_id:this.props.interface_id, range:6}).then(result => {
   if (result.data.length > 0){
    const groups = new vis.DataSet([{id:'in',  content:'In', options: { shaded: { orientation: 'bottom' }}},{id:'out', content:'Out' }]);
    const data = result.data.flatMap(({time, in8s, out8s}) => [{x:new Date(time*1000), y:in8s, group:'in'},{x:new Date(time*1000), y:out8s, group:'out'}]);
    const dataset = new vis.DataSet(data);
    const options = { width:'100%', height:'100%', zoomMin:60000, zoomMax:1209600000, clickToUse:true, drawPoints: false, interpolation:false, legend:true, dataAxis:{ left:{ title:{ text:'kbps' } } } };
    this.graph = new vis.Graph2d(this.canvas.current, dataset, groups, options);
   } else
    this.canvas.current.innerHTML = 'no stats';
  }))
 }

 gotoNow = () => {
  const today = new Date()
  this.graph.moveTo(today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate()+' '+today.getHours()+':'+today.getMinutes());
 }

 render(){
  return <Article key='is_art' header='Statistics'>
   <div className={styles.graphs} ref={this.canvas} />
   <RevertButton key='ae_btn_reset' onClick={() => this.gotoNow()} title='Go to now' />
  </Article>
 }
}

// *************** Connection ****************
//
class ConnectionInfo extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/interface/connection_info',{connection_id:this.props.id}).then(result => this.setState(result));
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})

 updateInfo = () => post_call('api/interface/connection_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render(){
  if(this.state.interfaces){
   return <InfoArticle key='ci_article' header={'Connection '+ this.props.id}>
    <InfoColumns key='ci_columns'>
     <CheckboxInput key='map' id='map' value={this.state.data.map} onChange={this.onChange} />
     {this.state.interfaces.map((row,idx) => <TextLine key={idx} id={'interface_' +idx} text={`${row.device_name} - ${row.interface_name} (${row.interface_id})`} />)}
    </InfoColumns>
    <BackButton key='ci_btn_back' onClick={() => this.props.changeSelf(<List key='interface_list' device_id={this.props.device_id} changeSelf={this.props.changeSelf} />)} title='Back' />
    <SaveButton key='ci_btn_save' onClick={() => this.updateInfo()} title='Save connection information' />
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// *************** LLDP ****************
//
class LLDP extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/interface/lldp_mapping',{device_id:this.props.device_id}).then(result => this.setState({data:Object.values(result.data)}))
 }

 listItem = (row) => [row.chassis_id,row.chassis_type,row.sys_name,row.port_id,row.port_type,row.port_desc,row.snmp_index,row.snmp_name,row.connection_id,row.status]

 render(){
  if(this.state.data)
   return <ContentReport key='il_cr' header='Interface' thead={['Chassis','Type','Name','Port ID','Type','Description','SNMP Index','SNMP Name','Conn','Status']} trows={this.state.data} listItem={this.listItem}>
   <BackButton key='il_btn_back' onClick={() => this.props.changeSelf(<List key='interface_list' device_id={this.props.device_id} />)} title='Back' />
   </ContentReport>
  else
   return <Spinner />
 }
}
