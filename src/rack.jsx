import React, { Fragment, Component } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoColumns, RimsContext, ContentList, ContentData } from './infra/UI.jsx';
import { TextInput, SelectInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, GoButton, InfoButton, ItemsButton, ReloadButton, SaveButton, HrefButton } from './infra/Buttons.jsx';

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
  rest_call('api/rack/list',{sort:'name'}).then(result => this.setState(result))
 }

 listItem = (row) => [<HrefButton key={'rl_btn_loc_'+row.id} text={row.location} onClick={() => this.changeContent(<LocationInfo key={'li_'+row.location_id} id={row.location_id} />)} />,row.name,<Fragment key='rack_list_buttons'>
   <InfoButton key={'rl_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)} title='Rack information' />
   <GoButton key={'rl_btn_go_'+row.id} onClick={() => this.context.changeMain(<DeviceMain key={'rack_device_'+row.id} rack_id={row.id} />)} title='Rack inventory' />
   <ItemsButton key={'rl_btn_list_'+row.id} onClick={() => this.changeContent(<Layout key={'rack_layout_'+row.id} id={row.id} />)} title='Rack layout'/>
   <DeleteButton key={'rl_btn_del_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete rack' />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete rack?') && rest_call('api/rack/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='rack_fragment'>
   <ContentList key='rack_cl' header='Racks' thead={['Location','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='rl_btn_reload' onClick={() => this.componentDidMount()} />
    <AddButton key='rl_btn_add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />)} title='Add rack' />
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

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = () =>  rest_call('api/rack/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

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
     <SaveButton key='ri_btn_save' onClick={() => this.updateInfo()} title='Save' />
    </article>
   )
  else
   return <Spinner />
 }
}

// *************** Layout ***************
//
// TODO
//
export class Layout extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/rack/devices',{id:this.props.id}).then(result => this.setState(result))
 }

 render(){
  return (<div>Rack Layout (TODO)</div>);
 }
}

// *************** Infra ***************
//
// TODO: fix up links on hostname so that they go to the Layout for that type
//
export class Infra extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/device/list',{field:'base',search:this.props.type,extra:['type']}).then(result => this.setState(result))
 }

 listItem = (row) => [<HrefButton key={'rinfra_dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} title='Device info'/>,
   row.hostname,<Fragment key='rinfra_buttons'>
   <InfoButton key={'rinfra_btn_' + row.id} onClick={() => this.context.changeMain({module:row.type_base,function:'Manage',args:{device_id:row.id, type:row.type_name}})} title='Manage device' />
   </Fragment>]

 changeContent = (elem) => this.setState({content:elem})

 render(){
  return <Fragment key='rinfra_fragment'>
   <ContentList key='rinfra_cl' header={this.props.type.toUpperCase()} thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='rinfra_btn_reload' onClick={() => this.componentDidMount()} />
   </ContentList>
   <ContentData key='rinfra_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}
Infra.contextType = RimsContext;
