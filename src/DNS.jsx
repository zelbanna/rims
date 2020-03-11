import React, { Fragment, Component } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, StateMap } from './infra/Generic.js';
import { ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';
import { Info as DeviceInfo } from './Device.jsx';
/*

dns.py:def domain_delete(aWeb):
dns.py:def domain_save(aWeb):
dns.py:def record_list(aWeb):
dns.py:def record_info(aWeb):
dns.py:def record_delete(aWeb):
dns.py:def sync(aWeb):
dns.py:def status(aWeb):
dns.py:def consistency(aWeb):

*/

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
    result.status = 'OK'
    this.setState(result);
   })
 }

 syncDomains(){
  rest_call(rest_base + 'api/dns/domain_list',{sync:true})
   .then((result) => {
    result.status = JSON.stringify(result.sync)
    this.setState(result)
   })
 }

 listItem = (row) => [row.id,row.name,row.service,<Fragment key={'domain_buttons_'+row.id}>
   <InfoButton key={'net_info_'+row.id} type='info'  onClick={() => this.changeContent(<DomainInfo key={'network_'+row.id} id={row.id} />) } />
   <InfoButton key={'net_items_'+row.id} type='items' onClick={() => this.changeContent(<RecordList changeSelf={this.changeContent} key={'items_'+row.id} network_id={row.id} />) } />
   <InfoButton key={'net_delete_'+row.id} type='trash' onClick={() => this.deleteList('api/dns/domain_delete',row.id,'Really delete domain') } />
   </Fragment>
  ]
}

// *************** Domain Info ***************
//
class DomainInfo extends InfoBase {
 render() {
  return(<div>Domain Info</div>)
 }
}

// *************** Status ***************
//
class Status extends Component {

 render() {
  return(<div>Status</div>)
 }
}

// *************** Record List ***************
//
class RecordList extends ListBase {

 render() {
  return(<div>RecordList</div>)
 }
}
