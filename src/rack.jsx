import React, { Fragment, Component } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoColumns, RimsContext, ContentList, ContentData } from './infra/UI.jsx';
import { TextInput, SelectInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, GoButton, InfoButton, ItemsButton, ReloadButton, SaveButton, LinkButton, UiButton } from './infra/Buttons.jsx';

import { Main as DeviceMain, Info as DeviceInfo } from './device.jsx';
import { Info as LocationInfo } from './location.jsx';

// *************** Main ***************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <List key='rack_list' />
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}

// *************** List ***************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/rack/list',{sort:"name"}).then(result => this.setState(result))
 }

 listItem = (row) => [<LinkButton key={'rl_btn_loc_'+row.id} text={row.location} onClick={() => this.changeContent(<LocationInfo key={'li_'+row.location_id} id={row.location_id} />)} />,row.name,<Fragment key='rack_list_buttons'>
   <InfoButton key={'rl_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)} />
   <GoButton key={'rl_btn_go_'+row.id} onClick={() => this.context.changeMain({content:<DeviceMain key={'Device_Main_'+row.id} rack_id={row.id} />})} />
   <ItemsButton key={'rl_btn_list_'+row.id} onClick={() => this.changeContent(<Inventory key={'rack_inventory_'+row.id} id={row.id} />)} />
   <DeleteButton key={'rl_btn_del_'+row.id} onClick={() => this.deleteList('api/rack/delete',row.id,'Really delete rack?')} />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='rack_fragment'>
   <ContentList key='rack_cl' header='Racks' thead={['Location','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='rl_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='rl_btn_add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />) } />
   </ContentList>
   <ContentData key='rack_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}
List.contextType = RimsContext;

// *************** Info ***************
//
class Info extends Component {
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
  rest_call('api/rack/info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return (
    <article className='info'>
     <h1>Rack</h1>
     <InfoColumns key='rack_content'>
      <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
      <TextInput key='size' id='size' value={this.state.data.size} onChange={this.onChange} />
      <SelectInput key='console' id='console' value={this.state.data.console} onChange={this.onChange}>{this.state.consoles.map(row => <option key={'ri_con_'+row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
      <SelectInput key='location_id' id='location_id' label='Location' value={this.state.data.location_id} onChange={this.onChange}>{this.state.locations.map(row => <option key={'ri_loc_'+row.id} value={row.id}>{row.name}</option>)}</SelectInput>
      <SelectInput key='pdu_1' id='pdu_1' label='PDU1' value={this.state.data.pdu_1} onChange={this.onChange}>{this.state.pdus.map(row => <option key={'ri_pdu1_'+row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
      <SelectInput key='pdu_2' id='pdu_2' label='PDU2' value={this.state.data.pdu_2} onChange={this.onChange}>{this.state.pdus.map(row => <option key={'ri_pdu2_'+row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
     </InfoColumns>
     <SaveButton key='ri_btn_save' onClick={() => this.updateInfo('api/rack/info')} />
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
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/rack/devices',{id:this.props.id}).then(result => this.setState(result))
 }

 render(){
  return (<div>Rack Inventory (TODO)</div>);
 }
}

// *************** Infra ***************
//
// TODO: fix up links on hostname so that they go to the inventory for that type
//
export class Infra extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/device/list',{field:'base',search:this.props.type,extra:['type']}).then(result => this.setState(result))
 }

 listItem = (row) => {
  const buttons = []
  if (row.url)
   buttons.push(<UiButton key={'ri_btn_ui_'+row.id} onClick={() => { window.open(row.url,'_blank'); }} />)
  return [
   <LinkButton key={'ri_dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} />,
   row.hostname,<Fragment key='ri_buttons'>{buttons}</Fragment>
  ]
 }


 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='ri_fragment'>
   <ContentList key='ri_cl' header={this.props.type.toUpperCase()} thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='ri_btn_reload' onClick={() => this.componentDidMount() } />
   </ContentList>
   <ContentData key='ri_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

/*
 for dev in devices:
  <A CLASS=z-op DIV=div_content_left URL='%s_inventory?ip=%s'>%s</A></DIV><DIV>"%(dev['type_name'],dev['ip'],dev['hostname']))
  aWeb.button('info',DIV='main',URL='%s_manage?id=%s&ip=%s&hostname=%s'%(dev['type_name'],dev['id'],dev['ip'],dev['hostname'])))
*/
