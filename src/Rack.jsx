import React, { Fragment, Component } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { MainBase, ListBase, InfoBase } from './infra/Base.jsx';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { Spinner, InfoCol2, RimsContext } from './infra/Generic.js';

import { Main as DeviceMain, Info as DeviceInfo } from './Device.jsx';

// *************** Main ***************
//
export class Main extends MainBase {
 constructor(props){
  super(props)
  this.state.content = <List key='rack_list' />
 }
}

// *************** List ***************
//
export class List extends ListBase {
 constructor(props){
  super(props)
  this.header = 'Racks'
  this.thead = ['Location','Name','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />) } />
  ]
 }

 componentDidMount(){
  rest_call('api/rack/list',{sort:"name"}).then(result => this.setState(result))
 }

 listItem = (row) => [row.location,row.name,<Fragment key='rack_list_buttons'>
  <InfoButton key={'rack_info_'+row.id} type='info'  onClick={() => { this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)}} />
  <InfoButton key={'rack_show_'+row.id} type='show' onClick={() => { this.context.changeMain({content:<DeviceMain key={'Device_Main_'+row.id} rack_id={row.id} />})}} />
  <InfoButton key={'rack_del_'+row.id} type='delete' onClick={() => { this.deleteList('api/rack/delete',row.id,'Really delete rack?')}} />
 </Fragment>]
}
List.contextType = RimsContext;

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call('api/rack/info',{id:this.props.id}).then(result => this.setState(result))
 }

 infoItems = () => [
    {tag:'input', type:'text', id:'name', text:'Name', value:this.state.data.name},
    {tag:'input', type:'text', id:'size', text:'Size', value:this.state.data.size},
    {tag:'select', id:'console', text:'Console', value:this.state.data.console, options:this.state.consoles.map(row => ({value:row.id, text:row.hostname}))},
    {tag:'select', id:'location_id', text:'Location', value:this.state.data.location_id, options:this.state.locations.map(row => ({value:row.id, text:row.name}))},
    {tag:'select', id:'pdu_1', text:'PDU1', value:this.state.data.pdu_1, options:this.state.pdus.map(row => ({value:row.id, text:row.hostname}))},
    {tag:'select', id:'pdu_2', text:'PDU2', value:this.state.data.pdu_2, options:this.state.pdus.map(row => ({value:row.id, text:row.hostname}))},
   ]

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Rack Info</h1>
     <InfoCol2 key='rack_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='rack_save' type='save' onClick={() => this.updateInfo('api/rack/info')} />
    </article>
   )
  else
   return <Spinner />
 }
}

// *************** Inventory ***************
//
// TODO
//
export class Inventory extends Component {

 componentDidMount(){
  rest_call('api/rack/devices',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  return (<div>Rack Inventory (TODO)</div>);
 }
}

// *************** Infra ***************
//
// TODO: fix up links on hotname so that they go to the inventory for that type
//
export class Infra extends ListBase {
 constructor(props){
  super(props)
  this.header = this.props.type.toUpperCase();
  this.thead = ['ID','Name','']
  this.buttons = [<InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} /> ]
 }

 componentDidMount(){
  rest_call('api/device/list',{field:'base',search:this.props.type,extra:['type']}).then(result => this.setState(result))
 }

 listItem = (row) => {
  const buttons = []
  if (row.url)
   buttons.push(<InfoButton key={'ri_url_'+row.id} type='ui' onClick={() => { window.open(row.url,'_blank'); }} />)
  return [
   <TextButton key={'ri_dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} />,
   row.hostname,<Fragment key='ri_buttons'>{buttons}</Fragment>
  ]
 }
}

/*
 for dev in devices:
  <A CLASS=z-op DIV=div_content_left URL='%s_inventory?ip=%s'>%s</A></DIV><DIV>"%(dev['type_name'],dev['ip'],dev['hostname']))
  aWeb.button('info',DIV='main',URL='%s_manage?id=%s&ip=%s&hostname=%s'%(dev['type_name'],dev['id'],dev['ip'],dev['hostname'])))
*/
