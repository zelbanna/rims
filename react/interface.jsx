import React, { Component, Fragment } from 'react'
import { post_call } from './infra/Functions.js';
import { Spinner, StateLeds, Article, LineArticle, InfoArticle, InfoColumns, Result, ContentReport } from './infra/UI.jsx';
import { CheckboxInput, TextInput, TextLine, SelectInput } from './infra/Inputs.jsx';
import { AddButton, BackButton, DeleteButton,ForwardButton, GoButton, HealthButton, InfoButton, ItemsButton, LinkButton, ReloadButton, RevertButton, SaveButton, SearchButton, SyncButton, HrefButton, UnlinkButton, TextButton } from './infra/Buttons.jsx';
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

 deleteList = (interface_id,name) => (window.confirm('Really delete interface ' + name) && post_call('api/interface/delete', {interface_id:interface_id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.interface_id !== interface_id)),result:JSON.stringify(result.interfaces)})))

 cleanUp = () => (window.confirm('Clean up empty interfaces?') && post_call('api/interface/cleanup',{device_id:this.props.device_id}).then(result => this.componentDidMount()))

 resetStatus = () => post_call('api/interface/clear',{device_id:this.props.device_id}).then(result => this.componentDidMount())

 discoverInterfaces = () => (window.confirm('Rediscover interfaces?') && post_call('api/interface/snmp',{device_id:this.props.device_id}).then(result => this.componentDidMount()))

 unLink = (interface_id, connection_id) => (window.confirm('Really unlink?') && post_call('api/interface/disconnect', {connection_id:connection_id}).then(result => {
  if (result.clear){
   var data = this.state.data;
   for (var iif of data){
    if (iif.connection_id === connection_id){
     iif.connection_id = null;
     break;
    }
   }
   this.setState({data:data,result:'OK'})
  } else {
   this.setState({result:'NOT_OK'})
  }
 }))

 
 listItem = (row) => [row.snmp_index,row.name,row.mac,(row.ip) ? row.ip : '-',row.description,row.class,
   (row.connection_id) ? <HrefButton key={'conn_btn_'+row.interface_id} text={row.connection_id} onClick={() => this.changeContent(<ConnectionInfo key={'connection_info_' + row.connection_id} id={row.connection_id} device_id={this.props.device_id} changeSelf={this.changeContent} />)} title='Connection information' /> : '-',
   <>
    <StateLeds key='state' state={[row.if_state,row.ip_state]} title='interface and ip state' />
    <InfoButton key='info' onClick={() => this.changeContent(<Info key={row.interface_id} interface_id={row.interface_id} changeSelf={this.props.changeSelf} />)} title='Interface information' />
    {row.snmp_index > 0 && <HealthButton key='stats' onClick={() => this.changeContent(<Statistics key={row.interface_id} device_id={this.props.device_id} interface_id={row.interface_id} name={row.name} />)} title='Interface stats' />}
    <DeleteButton key='del' onClick={() => this.deleteList(row.interface_id,row.name)} title='Delete interface' />
    {!row.connection_id && ['wired','optical'].includes(row.class) && <LinkButton key='link' onClick={() => this.changeContent(<Info key={'interface_info_' + row.interface_id} op='connect_device' interface_id={row.interface_id} name={row.name} changeSelf={this.props.changeSelf} />)} title='Connect interface' />}
    {row.connection_id && <UnlinkButton key='unlink' onClick={() => this.unLink(row.interface_id,row.connection_id)} title='Delete Connection' />}
   </>]

 render(){
  if (this.state.data) {
   return <ContentReport key='il_cl' header='Interfaces' thead={['SNMP','Name','MAC','IP Address','Description','Type','Link','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='il_btn_reload' onClick={() => this.componentDidMount()} />
    <AddButton key='il_btn_add' onClick={() => this.changeContent(<Info key='interface_info' device_id={this.props.device_id} interface_id='new' changeSelf={this.props.changeSelf} />) } title='Add interface' />
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

// *************** Report ****************
//
export class Report extends Component {
 componentDidMount(){
  post_call('api/interface/list').then(result => this.setState(result))
 }

 listItem = (row) => [row.device_id,row.hostname,row.interface_id,row.class,row.ip,row.mac,row.name,row.description,<StateLeds key={'ir_'+row.id} state={[row.if_state,row.ip_state]} title='interface and ip state' />]

 render(){
  return (!this.state) ? <Spinner /> : <ContentReport key='if_cr' header='Devices' thead={['Dev','Hostname','If','Class','IP','MAC','Name','Description','State']} trows={this.state.data} listItem={this.listItem} />
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
  post_call('api/interface/info',{interface_id:this.props.interface_id, mac:this.props.mac, name:this.props.name, description:this.props.description, device_id:this.props.device_id, class:this.props.class, extra:['classes','ip']}).then(result => this.setState({...result, update:undefined}));
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.componentDidMount();
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});
 updateInfo = () => post_call('api/interface/info',{op:'update', ...this.state.data}).then(result => this.setState(result))
 changeIpam = (id) => import('./ipam.jsx').then(lib => this.changeContent(<lib.AddressInfo key={'address_info_'+id} id={id} />));

 // IPAM
 stateIpam = () => {
  this.setState({op:(this.state.domains && this.state.networks) ? 'ipam' : 'wait', ipam:{ip:'<N/A>'}})
  if (!this.state.domains)
   post_call('api/dns/domain_list',{filter:'forward'}).then(result => this.setState({domains:result.data,op:(this.state.networks) ? 'ipam':'wait'}));
  if (!this.state.networks)
   post_call('api/ipam/network_list').then(result => this.setState({networks:result.data,op:(this.state.domains) ? 'ipam':'wait'}));
 }
 ipamSearchIP = () => {
  if (this.state.ipam.network_id)
   post_call('api/ipam/address_find',{network_id:this.state.ipam.network_id}).then(result => this.setState({ipam:{...this.state.ipam, ip:result.ip}}))
 }
 ipamOnChange = (e) => this.setState({ipam:{...this.state.ipam, [e.target.name]:e.target.value}});
 ipamCreate = () => post_call('api/interface/info',{op:'ipam_create',     interface_id:this.state.data.interface_id, record:this.state.ipam}).then(result => this.setState({...result,op:null}))
 ipamPrimary = (id) => post_call('api/interface/info',{op:'ipam_primary', interface_id:this.state.data.interface_id, ipam_id:id}).then(result => this.setState(result));
 ipamDelete = (id) => (window.confirm('Delete IP Address?') && post_call('api/ipam/address_delete',{id:id}).then(result => this.componentDidMount()));
 ipamDnsSync = () => post_call('api/interface/info',{op:'dns_sync',       interface_id:this.state.data.interface_id}).then(result => this.setState(result));

 // Connections
 connectDeviceChange = (e) => {
  this.setState({connect:{...this.state.connect, [e.target.name]:e.target.value}});
  if(e.target.name === 'id' && e.target.value.length > 0)
   post_call('api/device/hostname',{id:e.target.value}).then(result => (result && this.setState({connect:{...this.state.connect, found:(result.status === 'OK'), name:(result.status === 'OK') ? result.data : '<N/A>'}})))
 }
 connectInterfaceChange = (e) => this.setState({connect:{...this.state.connect, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})
 disconnectInterface = () => (this.state.peer && post_call('api/interface/connect',{a_id:this.state.data.interface_id,b_id:this.state.peer.interface_id,disconnect:true}).then(result => this.setState({peer:null})))
 stateInterface = () => (this.state.connect.found && post_call('api/interface/list',{device_id:this.state.connect.id,sort:'name',filter:['connected']}).then(result => this.setState({interfaces:result.data, op:'connect_interface'})))
 connectInterfaceConnect = () => (this.state.connect.interface_id && post_call('api/interface/connect',{a_id:this.state.data.interface_id,b_id:this.state.connect.interface_id,map:this.state.connect.map}).then(result => this.setState({connect:{},op:null})))

 // Render
 render(){
  if(this.state.data){
   if (this.state.op){
    if(this.state.op === 'connect_device')
     return <LineArticle key='ii_cnct_art'>
     Connect {this.state.data.name} to <TextInput key='ii_cnct_dev' id='id' label='Device ID' onChange={this.connectDeviceChange} /> with name '{this.state.connect.name}'
     <BackButton key='back' onClick={() => this.setState({op:null})} title='Back' />
     <ForwardButton key='fwd' onClick={() => this.stateInterface()} title={'Connect interface on ' + this.state.connect.name} />
    </LineArticle>
    else if(this.state.op === 'connect_interface')
     return <LineArticle key='la_cnct'>
      Connect {this.state.data.name} to {this.state.connect.name} on
      <SelectInput key='interface' id='interface_id' label='Interface' value={this.state.connect.interface_id} onChange={this.connectInterfaceChange}>
       {this.state.interfaces.map(row => <option key={row.interface_id} value={row.interface_id}>{`${row.interface_id} (${row.name} - ${row.description})`}</option>)}
      </SelectInput>
      <CheckboxInput key='map' id='map' value={this.state.connect.map} onChange={this.connectInterfaceChange} />
      <BackButton key='back' onClick={() => this.setState({op:'connect_device'})} title='Back' />
      <ForwardButton key='fwd' onClick={() => this.connectInterfaceConnect()} title='Complete connection' />
     </LineArticle>
    else if (this.state.op === 'ipam'){
     return <InfoArticle key='ia_ipam' header='Create IPAM record'>
      <InfoColumns key='ic'>
       <SelectInput key='network' id='network_id' label='Network' value={this.state.ipam.network_id} onChange={this.ipamOnChange}>{this.state.networks.map(row => <option key={row.id} value={row.id}>{`${row.netasc} (${row.description})`}</option>)}</SelectInput>
       <TextInput key='ip' id='ip' value={this.state.ipam.ip} label='IP' onChange={this.ipamOnChange} />
       <SelectInput key='domain' id='a_domain_id' label='Domain' value={this.state.ipam.a_domain_id} onChange={this.ipamOnChange}>{this.state.domains.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}</SelectInput>
      </InfoColumns>
      <BackButton key='back' onClick={() => this.setState({op:null})} title='Back'/>
      <SearchButton key='find_ip' onClick={() => this.ipamSearchIP()} title='Search IP within network' />
      <ForwardButton key='fwd' onClick={() => this.ipamCreate()} title='Create IPAM entry' />
     </InfoArticle>
    } else if (this.state.op === 'wait')
     return <Spinner />
    else
     return <div>Intermediate interface operation state</div>
   } else {
    const primary = (this.state.data.ipam_id);
    const old = (this.state.data.interface_id !== 'new');
    const peer = this.state.peer;
    const opresult = (this.state.update === undefined) ? '' : 'Updated: ' + JSON.stringify(this.state.update)
    return (<InfoArticle key='ia_interface_info' header='Interface'>
     <InfoColumns key='ic' columns={3}>
      <TextLine key='id' id='id' label='Local ID' text={this.state.data.interface_id} /><div />
      <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
      {(primary) ? <SyncButton key='sync' onClick={() => this.ipamDnsSync()} title='sync interface name and IP hostname' /> : <div />}
      <SelectInput key='class' id='class' value={this.state.data.class} onChange={this.onChange}>{this.state.classes.map(row => <option key={row} value={row}>{row}</option>)}</SelectInput><div />
      <TextInput key='description' id='description' value={this.state.data.description} onChange={this.onChange} /><div />
      <TextInput key='snmp_index' id='snmp_index' label='SNMP index' value={this.state.data.snmp_index} onChange={this.onChange} /><div />
      <TextInput key='mac' id='mac' value={this.state.data.mac} onChange={this.onChange} /><div />
      {primary && <><TextLine key='ip' id='ip' label='Primary IP' text={this.state.primary.ip} /><div><GoButton key='go' onClick={() => this.changeIpam(this.state.primary.id)} title='Edit IPAM entry' /><DeleteButton key='delete' onClick={() => this.ipamDelete(this.state.primary.id)} title='Delete IPAM entry' /></div></>}
      {this.state.alternatives.map(row => <Fragment key={row.ip}><TextLine key='ip' id={row.ip} label='Alternative IP' text={row.ip} /><div><GoButton key='go' onClick={() => this.changeIpam(row.id)} title='Edit IPAM entry' /><SyncButton key='primary' onClick={() => this.ipamPrimary(row.id)} title='Make primary' /><DeleteButton key='delete' onClick={() => this.ipamDelete(row.id)} title='Delete IPAM entry' /></div></Fragment>)}
      {peer && <><TextLine key='peer_int_id' id='peer_interface' label='Peer Interface' text={peer.interface_id} /><UnlinkButton key='unlink' onClick={() => this.disconnectInterface()} title='Disconnect from peer' /></>}
      {peer && <><TextLine key='peer_dev_id' id='peer_device' label='Peer Device' text={peer.device_id} /><div/></>}
     </InfoColumns>
     {'changeSelf' in this.props && <ItemsButton key='list' onClick={() => this.props.changeSelf(<List key='interface_list' device_id={this.state.data.device_id} changeSelf={this.props.changeSelf} />)} title='Interfaces' />}
     {this.props.interface_id !== 'new' && <ReloadButton key='reload' onClick={() => this.componentDidMount()} />}
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save interface information' />
     {old && !peer && ['wired','optical'].includes(this.state.data.class) && <LinkButton key='connect' onClick={() => this.setState({op:'connect_device'})} title='Connect peer interface' />}
     {old && <AddButton key='add' onClick={() => this.stateIpam()} title='Add IP' />}
     <Result key='result' result={opresult} />
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
  this.state = {range:1, visibility: {ib:true, ob:true, ip:true, op:true}}
  this.canvas = React.createRef()
  this.graph = null;
  this.vis = null;
 }

 componentDidMount(){
  import('vis-timeline/standalone/esm/vis-timeline-graph2d').then(vis => {
   this.vis = vis;
   const options = { locale:'en', width:'100%', height:'100%', zoomMin:60000, zoomMax:1209600000, clickToUse:true, drawPoints: false, interpolation:false, legend:true, dataAxis:{ alignZeros:false , icons:true, left:{ title:{ text:'kbps' } }, right:{ title:{ text:'packets per second' } } } };
   const groups = new this.vis.DataSet([{id:'ib', content:'In'}, {id:'ob', content:'Out' }, {id:'ip', content:'In', options: { yAxisOrientation: 'right'}},{id:'op', content:'Out', options: { yAxisOrientation: 'right'}}]);
   this.graph = new this.vis.Graph2d(this.canvas.current, [], groups, options);
   this.updateItems(this.state.range);
  })
 }

 updateItems = (range) => post_call('api/statistics/query_interface',{device_id:this.props.device_id, interface_id:this.props.interface_id, range:range}).then(result => {
  if (result.status === 'OK') {
   const pos = {};
   const names = {'in8s':'ib','out8s':'ob','inUPs':'ip','outUPs':'op'};
   result.header.forEach((item,index) => pos[item] = index);
   const dataset = new this.vis.DataSet(result.data.map(params => ({ x:params[pos['_time']], y:params[pos['_value']] * (params[pos['_field']].substr(-2) === '8s' ? 8/1024 : 1), group:names[params[pos['_field']]] })));
   this.graph.setItems(dataset);
   this.graph.fit();
  }
 });

 rangeChange = (e) => {
  this.setState({[e.target.name]:e.target.value})
  this.updateItems(e.target.value);
 }

 checkChange = (e) => {
  this.setState({visibility:{...this.state.visibility, [e.target.name]:e.target.checked}});
  this.graph.setOptions({groups:{visibility:{[e.target.name]:e.target.checked}}})
 }

 gotoNow = () => {
  const today = new Date()
  this.graph.moveTo(today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate()+' '+today.getHours()+':'+today.getMinutes());
 }

 render(){
  const v = this.state.visibility;
  return <Article key='is_art' header='Statistics'>
   <ReloadButton key='reload' onClick={() => this.updateItems(this.state.range)} title='Reload' />
   <RevertButton key='reset' onClick={() => this.gotoNow()} title='Go to now' />
   <br />
   <TextLine key='name' id='name' label='Interface name' text={this.props.name} />
   <br />
   <SelectInput key='range' id='range' label='Time range' value={this.state.range} onChange={this.rangeChange}>
    <option value='1'>1h</option>
    <option value='4'>4h</option>
    <option value='8'>8h</option>
    <option value='24'>24h</option>
   </SelectInput>
   <CheckboxInput key='ib' id='ib' label='In bps' value={v.ib} onChange={this.checkChange} />
   <CheckboxInput key='ob' id='ob' label='Out bps' value={v.ob} onChange={this.checkChange} />
   <CheckboxInput key='ip' id='ip' label='In pps' value={v.ip} onChange={this.checkChange} />
   <CheckboxInput key='op' id='op' label='Out pps' value={v.op} onChange={this.checkChange} />
   <div className={styles.graphs} ref={this.canvas} />
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
   <BackButton key='il_btn_back' onClick={() => this.props.changeSelf(<List key='interface_list' device_id={this.props.device_id} changeSelf={this.props.changeSelf} />)} title='Back' />
   </ContentReport>
  else
   return <Spinner />
 }
}
