import React, { Component } from 'react'
import { post_call } from './infra/Functions.js';
import { Flex, Spinner, CodeArticle, InfoArticle, InfoColumns, ContentList, ContentData, ContentReport, Result } from './infra/UI.jsx';
import { TextLine, SelectInput, TextInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, ConfigureButton, HealthButton, ItemsButton, ReloadButton, SaveButton, SyncButton } from './infra/Buttons.jsx';

// *************** Main ***************
//
export class Main extends Component {
 componentDidMount(){
  this.setState(<DomainList key='domain_list' />)
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return <>{this.state}</>
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
  post_call('api/dns/domain_list').then(result => {
   result.result = 'OK';
   this.setState(result);
  })
 }

 syncDomains(){
  post_call('api/dns/domain_list',{sync:true}).then(result => {
   result.result = 'NS:' + result.ns.status + ', Recursors:' + result.rec.status;
   this.setState(result);
  })
 }

 listItem = (row) => [row.id,row.name,row.service,<>
   <ConfigureButton key='info' onClick={() => this.changeContent(<DomainInfo key='domain_info' id={row.id} />) } title='Edit domain information' />
   <ItemsButton key='items' onClick={() => this.changeContent(<RecordList changeSelf={this.changeContent} key='record_list' domain_id={row.id} />) } title='View domain records' />
   <DeleteButton key='del' onClick={() => this.deleteList(row.id) } title='Delete domain' />
  </>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete domain') && post_call('api/dns/domain_delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 render(){
  return <>
   <ContentList key='cl' header='Domains' thead={['ID','Domain','Server','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<DomainInfo key='domain_info' id='new' />) } title='Add domain' />
    <SyncButton key='sync' onClick={() => this.syncDomains()} title='Sync external DNS servers with cache' />
    <HealthButton key='stats' onClick={() => this.changeContent(<Statistics key='recursor_statistics' />)} title='View DNS statistics' />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </>
 }
}

// *************** Domain Info ***************
//
class DomainInfo extends Component {
 constructor(props){
  super(props);
  this.state = { data:null };
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () =>  post_call('api/dns/domain_info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.componentDidMount()
 }

 componentDidMount(){
  post_call('api/dns/domain_info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data) {
   const old = (this.state.data.id !== 'new');
   return <InfoArticle key='ia_dom' header='Domain'>
     <InfoColumns key='ic'>
      {old && <TextLine key='node' id='node' text={this.state.infra.node} />}
      {old && <TextLine key='service' id='service' text={this.state.infra.service} />}
      {old && <TextLine key='foreign_id' id='foreign_id' label='Foreign ID' text={this.state.infra.foreign_id} />}
      {!old && <SelectInput key='server_id' id='server_id' label='Server' value={this.state.data.server_id} onChange={this.onChange}>{this.state.servers.map((row,idx) => <option key={'srv_'+idx} value={row.id}>{`${row.service}@${row.node}`}</option>)}</SelectInput>}
      <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
      <TextInput key='master' id='master' value={this.state.data.master} onChange={this.onChange} />
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} />
      <TextLine  key='serial' id='serial' text={this.state.data.serial} />
     </InfoColumns>
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save domain information' />
    </InfoArticle>
  } else
   return <Spinner />
 }
}

// *************** Status ***************
//
class Statistics extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/dns/statistics').then(result => {
   const queries = []
   for (let [node,rows] of Object.entries(result.queries)){
    const ns = node.split('_');
    rows.forEach(row => queries.push([ns[0],ns[1],row[0],row[1],row[2]]))
   }
   const remotes = []
   for (let [node,rows] of Object.entries(result.remotes)){
    const ns = node.split('_');
    rows.forEach(row => remotes.push([ns[0],ns[1],row[0],row[1]]))
   }
   this.setState({queries:queries,remotes:remotes})
  })
 }

 render(){
  return (this.state.queries && this.state.remotes) ? <Flex key='statistics_flex'>
    <ContentReport key='queries_cr' header='Looked up FQDN' thead={['Node','Service','Hits','FQDN','Type']} trows={this.state.queries} listItem={(row) => row} />
    <ContentReport key='remotes_cr' header='Queriers' thead={['Node','Service','Hits','Who']} trows={this.state.remotes} listItem={(row) => row} />
   </Flex> : <Spinner />
 }
}

// *************** Record List ***************
//
class RecordList extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.componentDidMount();
 }

 componentDidMount(){
  post_call('api/dns/record_list',{domain_id:this.props.domain_id}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [row.name,row.content,row.type,row.ttl,<>
   <ConfigureButton key='info' onClick={() => this.changeContent(<RecordInfo key='record_info' domain_id={this.props.domain_id} op='info' {...row} />)} title='Configure record' />
   {['A','AAAA','CNAME','PTR','DHCID'].includes(row.type) && <DeleteButton key='del' onClick={() => this.deleteList(row.name,row.type)} title='Delete record' />}
  </>]

 deleteList = (name,type) => (window.confirm('Delete record?') && post_call('api/dns/record_delete', {domain_id:this.props.domain_id,name:name,type:type}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => !(row.name === name && row.type === type))})))

 render(){
  const status = this.state.status;
  if (status)
   if (status === 'OK'){
    const data = this.state.data;
    return <ContentReport key='rl_cr' header='Records' thead={['Name','Content','Type','TTL','']} trows={data} listItem={this.listItem} result={this.state.result}>
     <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
     <AddButton key='add' onClick={() => this.changeContent(<RecordInfo key='record_info' domain_id={this.props.domain_id} name='new' op='new' />)} title='Add DNS record' />
    </ContentReport>
   } else
    return <CodeArticle key='ca_rl'>Error retrieving record list: {JSON.stringify(this.state.info)}</CodeArticle>
  else
   return <Spinner />
 }
}

// *************** Record Info ***************
//
class RecordInfo extends Component {
 constructor(props){
  super(props);
  this.state = {data:null,info:undefined };
  if (this.props.op === 'info'){
   this.state.data = {domain_id:this.props.domain_id, name:this.props.name, type:this.props.type, ttl:this.props.ttl, content:this.props.content}
   this.state.op = 'update'
  } else {
   this.state.data = {domain_id:this.props.domain_id, name:'', type:'A', ttl:3600, content:''}
   this.state.op = 'insert'
  }
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = () => post_call('api/dns/record_info',{op:this.state.op, ...this.state.data}).then(result => {
   this.setState({op:(result.status === 'OK') ? 'update' : this.state.op, ...result})
 })

 render() {
  if (this.state.data)
   return <InfoArticle key='rec_art' header='Record'>
     <InfoColumns key='ic'>
      <TextInput key='name' id='name' value={this.state.data.name} title='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa' onChange={this.onChange} placeholder='name' />
      <TextInput key='type' id='type' value={this.state.data.type} onChange={this.onChange} placeholder={'A, PTR or CNAME typically'} />
      <TextInput key='ttl' id='ttl' label='TTL' value={this.state.data.ttl} onChange={this.onChange} />
      <TextInput key='content' id='content' value={this.state.data.content} title='E.g. A:IP, PTR:x.y.x-inaddr.arpa, CNAME:A - remember dot on PTR/CNAME' onChange={this.onChange} placeholder='content' />
      {this.props.serial && <TextLine key='serial' id='serial' text={this.props.serial} />}
     </InfoColumns>
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save record information' />
     <Result key='result' result={(this.state.status !== 'OK') ? JSON.stringify(this.state.info) : 'OK'} />
    </InfoArticle>
  else
   return <Spinner />
 }
}
