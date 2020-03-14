import React, { Fragment, Component } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, TableHead, TableRow } from './infra/Generic.js';
import { ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';

// CONVERTED ENTIRELY

// *************** Domain List ***************
//
export class DomainList extends ListBase {
 constructor(props){
  super(props)
  this.header='Domains'
  this.thead = ['ID','Domain','Server','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<DomainInfo key={'domain_new_' + rnd()} id='new' />) } />,
   <InfoButton key='sync' type='sync' onClick={() => this.syncDomains()} />,
   <InfoButton key='document' type='document' onClick={() => this.changeContent(<Status key='domain_status' />)} />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/dns/domain_list')
   .then((result) => {
    result.result = 'OK';
    this.setState(result);
   })
 }

 syncDomains(){
  rest_call(rest_base + 'api/dns/domain_list',{sync:true})
   .then((result) => {
    result.result = JSON.stringify(result.result);
    this.setState(result);
   })
 }

 listItem = (row) => [row.id,row.name,row.service,<Fragment key={'domain_buttons_'+row.id}>
   <InfoButton key={'net_info_'+row.id} type='info'  onClick={() => this.changeContent(<DomainInfo key={'domain_'+row.id} id={row.id} />) } />
   <InfoButton key={'net_items_'+row.id} type='items' onClick={() => this.changeContent(<RecordList changeSelf={this.changeContent} key={'items_'+row.id} domain_id={row.id} />) } />
   <InfoButton key={'net_delete_'+row.id} type='trash' onClick={() => this.deleteList('api/dns/domain_delete',row.id,'Really delete domain') } />
   </Fragment>
  ]
}

// *************** Domain Info ***************
//
class DomainInfo extends InfoBase {
 constructor(props){
  super(props)
  this.state.servers = null
 }

 componentDidMount(){
  rest_call(rest_base + 'api/dns/domain_info',{id:this.props.id})
   .then((result) => {
    result.data.server_id = null;
    this.setState(result); })
 }

 infoItems = () => {
  let items = []
  if (this.state.data.id !== "new") {
   items.push({tag:'span', id:'node', text:'Node', value:this.state.infra.node})
   items.push({tag:'span', id:'service', text:'Service', value:this.state.infra.service})
   items.push({tag:'span', id:'foreign_id', text:'Foreign ID', value:this.state.infra.foreign_id})
  } else
   items.push({tag:'select', id:'server_id', text:'Server', value:this.state.data.server_id, options:this.state.servers.map(row => ({value:row.id, text:`${row.service}@${row.node}`}))})
  items.push(
   {tag:'input', type:'text', id:'name', text:'Name', value:this.state.data.name},
   {tag:'input', type:'text', id:'master', text:'Master', value:this.state.data.master},
   {tag:'input', type:'text', id:'type', text:'Type', value:this.state.data.type},
   {tag:'input', type:'text', id:'notified_serial', text:'Notified_serial', value:this.state.data.notified_serial},
  )
  return items;
 }

 render() {
  if (this.state.found === false)
   return <article>Domain with id: {this.props.id} removed</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Domain Info</h1>
     <InfoCol2 key='domain_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='domain_save' type='save' onClick={() => this.updateInfo('api/dns/domain_info')} />
    </article>
   );
  }
 }
}

// *************** Status ***************
//
class Status extends Component {
 constructor(props){
  super(props)
  this.state = {top:null,who:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/dns/status')
   .then((result) => {
    this.setState(result); })
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
  if ((this.state.top === null) || (this.state.whp === null))
   return <Spinner />
  else {
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
  }
 }
}

// *************** Record List ***************
//
class RecordList extends ReportBase {
 constructor(props){
  super(props)
  this.header = "Records"
  this.thead = ['ID','Name','Content','Type','TTL','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.props.changeSelf(<RecordInfo key={'record_new_' + rnd()} domain_id={this.props.domain_id} id='new' />)} />,
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/dns/record_list',{domain_id:this.props.domain_id})
   .then((result) => {
    this.setState(result); })
 }

 listItem = (row) => {
  var buttons = [<InfoButton key={'record_info_btn_' + row.id} type='info' onClick={() => this.props.changeSelf(<RecordInfo key={'record_info_'+row.id} domain_id={this.props.domain_id} id={row.id} />)} />]
  if (['A','CNAME','PTR'].includes(row.type )) {
   buttons.push(<InfoButton key={'record_del_btn_' + row.id} type='trash' onClick={() => this.deleteList('api/dns/record_delete',row.id,'Really delete record?')} />)
  }
  return [row.id,row.name,row.content,row.type,row.ttl,<Fragment key={'record_buttons_'+row.id}>{buttons}</Fragment>]
 }

 deleteList = (api,id,msg) => {
  if (window.confirm(msg)){
   rest_call(rest_base + api, {domain_id:this.props.domain_id,id:id})
    .then((result) => {
     if(result.deleted)
      this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id )})
    })
  }
 }
}

// *************** Record Info ***************
//
class RecordInfo extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/dns/record_info',{id:this.props.id,domain_id:this.props.domain_id})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => [
  {tag:'input', type:'text', id:'name', text:'Name', value:this.state.data.name, title:'E.g. A:FQDN, PTR:x.y.z.in-addr.arpa'},
  {tag:'input', type:'text', id:'content', text:'Content', value:this.state.data.content, title:'E.g. A:IP, PTR:FQDN'},
  {tag:'input', type:'text', id:'ttl', text:'TTL', value:this.state.data.ttl},
  {tag:'input', type:'text', id:'type', text:'Type', value:this.state.data.type}
 ]

 render() {
  if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Record Info</h1>
     <InfoCol2 key='record_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='record_save' type='save' onClick={() => this.updateInfo('api/dns/record_info')} />
    </article>
   );
  }
 }
}
