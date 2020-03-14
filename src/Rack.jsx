import React, { Fragment, Component } from 'react';
import { rest_call, rest_base, rnd } from './infra/Functions.js';
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
  this.thead = ['Location','Name','Size','']
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />) } />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/rack/list',{sort:"name"})
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.location,row.name,row.size,<Fragment key='rack_list_buttons'>
  <InfoButton key={'rack_info_'+row.id} type='info'  onClick={() => { this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)}} />
  <InfoButton key={'rack_show_'+row.id} type='show' onClick={() => { this.context.changeMain({content:<DeviceMain key={'Device_Main'} rack_id={row.id} />})}} />
  <InfoButton key={'rack_del_'+row.id} type='trash' onClick={() => { this.deleteList('api/rack/delete',row.id,'Really delete rack?')}} />
 </Fragment>]
}
List.contextType = RimsContext;

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/rack/info',{id:this.props.id})
   .then((result) => {
    this.setState(result); })
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
  if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Rack Info</h1>
     <InfoCol2 key='rack_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='rack_save' type='save' onClick={() => this.updateInfo('api/rack/info')} />
    </article>
   )
  }
 }
}

// *************** Inventory ***************
//
export class Inventory extends Component {

 componentDidMount(){
  rest_call(rest_base + 'api/rack/devices',{id:this.props.id})
   .then((result) => {
    this.setState(result); })
 }

 render() {
  return (<div>Rack Inventory (TODO)</div>);
 }
}

// *************** Infra ***************
//
// TODO: fix up links to the type view
//
export class Infra extends ListBase {
 constructor(props){
  super(props)
  this.header = this.props.type.toUpperCase();
  this.thead = ['ID','Name','']
  this.buttons = [<InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} /> ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/list',{field:'base',search:this.props.type,extra:['type']})
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => {
  const buttons = []
  if (row.url)
   buttons.push(<InfoButton key={'rack_url_'+row.id} type='ui' onClick={() => { window.open(row.url,'_blank'); }} />)
  return [
   <TextButton key={'infra_dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} />,
   row.hostname,<Fragment key='rack_infra_buttons'>{buttons}</Fragment>
  ]
 }
}

/*
def list_infra(aWeb):
 type = aWeb['type']
 devices = aWeb.rest_call("device/list",{'field':'base','search':type,'extra':['type']})['data']
 aWeb.wr("<ARTICLE><P>%ss</P>"%type.title())
 aWeb.wr(aWeb.button('reload',DIV='div_content_left', URL='rack_list_infra?type=%s'%type))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Name</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for dev in devices:
  aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right URL='device_info?id=%s'>%s</DIV><DIV><A CLASS=z-op DIV=div_content_left URL='%s_inventory?ip=%s'>%s</A></DIV><DIV>"%(dev['id'],dev['id'],dev['
type_name'],dev['ip'],dev['hostname']))
  aWeb.wr(aWeb.button('info',DIV='main',URL='%s_manage?id=%s&ip=%s&hostname=%s'%(dev['type_name'],dev['id'],dev['ip'],dev['hostname'])))
  if dev.get('url'):
   aWeb.wr(aWeb.button('ui', HREF=dev['url'], TARGET='_blank', TITLE='UI'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
*/
