import React, { Fragment, Component } from 'react'
import { rest_call, rnd,  } from './infra/Functions.js';
import { Spinner, InfoColumns, TableHead, TableRow, ContentList, ContentData, ContentReport, Result } from './infra/UI.jsx';
import { TextLine, SelectInput, TextInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, LogButton, ConfigureButton, ItemsButton, ReloadButton, SaveButton, SyncButton } from './infra/Buttons.jsx';

// CONVERTED ENTIRELY

// *************** Main ***************
//
export class Main extends Component {
 componentDidMount(){
  this.setState(<DomainList key='domain_list' />)
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}

// *************** Domain List ***************
//
export class DomainList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/dns/domain_list').then(result => {
   result.result = 'OK';
   this.setState(result);
  })
 }

 syncDomains(){
  rest_call('api/dns/domain_list',{sync:true}).then(result => {
   result.result = JSON.stringify(result.result);
   this.setState(result);
  })
 }

 listItem = (row) => [row.id,row.name,row.service,<Fragment key={'domain_buttons_'+row.id}>
   <ConfigureButton key={'net_info_'+row.id} onClick={() => this.changeContent(<DomainInfo key={'domain_'+row.id} id={row.id} />) } title='Edit domain information' />
   <ItemsButton key={'net_items_'+row.id} onClick={() => this.changeContent(<RecordList changeSelf={this.changeContent} key={'items_'+row.id} domain_id={row.id} />) } title='View domain records' />
   <DeleteButton key={'net_delete_'+row.id} onClick={() => this.deleteList(row.id) } title='Delete domain' />
   </Fragment>
  ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete domain') && rest_call('api/dns/domain_delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='dl_fragment'>
   <ContentList key='dl_cl' header='Domains' thead={['ID','Domain','Server','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='dl_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='dl_btn_add' onClick={() => this.changeContent(<DomainInfo key={'domain_new_' + rnd()} id='new' />) } title='Add domain' />
    <SyncButton key='dl_btn_sync' onClick={() => this.syncDomains()} title='Sync external DNS servers with cache' />
    <LogButton key='dl_btn_document' onClick={() => this.changeContent(<Status key='domain_status' />)} title='View DNS statistics' />
   </ContentList>
   <ContentData key='dl_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// *************** Domain Info ***************
//
class DomainInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true };
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/dns/domain_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <article>Domain with id: {this.props.id} removed</article>
  else if (this.state.data) {
   const old = (this.state.data.id !== "new");
   return (
    <article className='info'>
     <h1>Domain</h1>
     <InfoColumns key='domain_content'>
      {old && <TextLine key='node' id='node' text={this.state.infra.node} />}
      {old && <TextLine key='service' id='service' text={this.state.infra.service} />}
      {old && <TextLine key='foreign_id' id='foreign_id' label='Foreign ID' text={this.state.infra.foreign_id} />}
      {!old && <SelectInput key='server_id' id='server_id' label='Server' value={this.state.data.server_id} onChange={this.onChange}>{this.state.servers.map((row,idx) => <option key={'srv_'+idx} value={row.id}>{`${row.service}@${row.node}`}</option>)}</SelectInput>}
      <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
      <TextInput key='master' id='master' value={this.state.data.master} onChange={this.onChange} />
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} />
      <TextInput key='notified_serial' id='notified_serial' label='Notified Serial' value={this.state.data.notified_serial} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='domain_save' onClick={() => this.updateInfo('api/dns/domain_info')} title='Save domain information' />
    </article>
   );
  } else
   return <Spinner />
 }
}

// *************** Status ***************
//
class Status extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/dns/status').then(result => this.setState(result))
 }

 topTable = (node_service,rows) => {
  const ns = node_service.split('_');
  return (
  <div className='table'>
   <TableHead key={'top_thead_' + ns[0]} headers={['Node','Service','Hit','FQDN']} />
   <div className='tbody'>
    {rows.map((row,index) => <TableRow key={'top_trow_'+ ns[0] + '_' + index} cells={[ns[0],ns[1],row.count,row.fqdn]} /> )}
   </div>
  </div>
  )
 }

 whoTable = (node_service,rows) => {
  const ns = node_service.split('_');
  return (
  <div className='table'>
   <TableHead key={'top_thead_' + ns[0]} headers={['Node','Service','Hit','Who','FQDN']} />
   <div className='tbody'>
    {rows.map((row,index) => <TableRow key={'top_trow_'+ ns[0] + '_' + index} cells={[ns[0],ns[1],row.count,row.who,row.fqdn]} /> )}
   </div>
  </div>
  )
 }

 render(){
  if (this.state.top && this.state.who)
   return (
    <div style={{display:'flex'}}>
     <article className='report'>
      <h1>Top looked up FQDN</h1>
      {Object.keys(this.state.top).map(key => this.topTable(key, this.state.top[key]))}
     </article>
     <article className='report'>
      <h1>Top looked up WHO</h1>
      {Object.keys(this.state.who).map(key => this.whoTable(key, this.state.who[key]))}
     </article>
    </div>
   )
  else
   return <Spinner />
 }
}

// *************** Record List ***************
//
class RecordList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/dns/record_list',{domain_id:this.props.domain_id}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [row.id,row.name,row.content,row.type,row.ttl,<Fragment key={'rl_buttons_'+row.id}>
   <ConfigureButton key={'record_info_btn_' + row.id} onClick={() => this.changeContent(<RecordInfo key={'record_info_'+row.id} domain_id={this.props.domain_id} id={row.id} />)} title='Configure record' />
   {['A','CNAME','PTR'].includes(row.type) && <DeleteButton key={'record_del_btn_' + row.id} onClick={() => this.deleteList(row.id)} title='Delete record' />}
  </Fragment>]

 deleteList = (id) => (window.confirm('Delete record?') && rest_call('api/dns/record_delete', {domain_id:this.props.domain_id,id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 render(){
  return <ContentReport key='rl_cr' header='Records' thead={['ID','Name','Content','Type','TTL','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   <ReloadButton key='rl_btn_reload' onClick={() => this.componentDidMount() } />
   <AddButton key='rl_btn_add' onClick={() => this.changeContent(<RecordInfo key={'record_new_' + rnd()} domain_id={this.props.domain_id} id='new' />)} title='Add DNS record' />
  </ContentReport>
 }
}

// *************** Record Info ***************
//
class RecordInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true };
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  this.setState({info:undefined})
  rest_call('api/dns/record_info',{id:this.props.id,domain_id:this.props.domain_id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data) {
   return (
    <article className='info'>
     <h1>Record</h1>
     <InfoColumns key='record_content'>
      <TextInput key='name' id='name' value={this.state.data.name} title='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa' onChange={this.onChange} />
      <TextInput key='content' id='content' value={this.state.data.content} title='E.g. A:IP, PTR:FQDN' onChange={this.onChange} />
      <TextInput key='ttl' id='ttl' label='TTL' value={this.state.data.ttl} onChange={this.onChange} />
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} placeholder={'A, PTR or CNAME typically'} />
     </InfoColumns>
     <SaveButton key='record_save' onClick={() => this.updateInfo('api/dns/record_info')} title='Save record information' />
     <Result key='record_result' result={(this.state.status !== 'OK') ? this.state.info : 'OK'} />
    </article>
   );
  } else
   return <Spinner />
 }
}