import React, { Fragment, Component } from 'react';
import { rest_call, rnd } from './infra/Functions.js';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { Spinner, InfoCol2, RimsContext, ContentList, ContentData } from './infra/Generic.js';
import { TextInput, SelectInput } from './infra/Inputs.jsx';
import { Main as DeviceMain, Info as DeviceInfo } from './Device.jsx';

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

 listItem = (row) => [row.location,row.name,<Fragment key='rack_list_buttons'>
   <InfoButton key={'rack_info_'+row.id} type='info'  onClick={() => this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)} />
   <InfoButton key={'rack_fwd_'+row.id} type='forward' onClick={() => this.context.changeMain({content:<DeviceMain key={'Device_Main_'+row.id} rack_id={row.id} />})} />
   <InfoButton key={'rack_items_'+row.id} type='items' onClick={() => this.changeContent(<Inventory key={'rack_inventory_'+row.id} id={row.id} />)} />
   <InfoButton key={'rack_del_'+row.id} type='delete' onClick={() => this.deleteList('api/rack/delete',row.id,'Really delete rack?')} />
  </Fragment>]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='rack_fragment'>
   <ContentList key='rack_cl' header='Racks' thead={['Location','Name','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='rack_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='rack_btn_add' type='add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />) } />
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

 changeHandler = (e) => {
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
     <h1>Rack Info</h1>
     <InfoCol2 key='rack_content'>
      <TextInput key='name' id='name' value={this.state.data.name} changeHandler={this.changeHandler} />
      <TextInput key='size' id='size' value={this.state.data.size} changeHandler={this.changeHandler} />
      <SelectInput key='console' id='console' value={this.state.data.console} options={this.state.consoles.map(row => ({value:row.id, text:row.hostname}))} changeHandler={this.changeHandler} />
      <SelectInput key='location_id' id='location_id' label='Location' value={this.state.data.location_id} options={this.state.locations.map(row => ({value:row.id, text:row.name}))} changeHandler={this.changeHandler} />
      <SelectInput key='pdu_1' id='pdu_1' label='PDU1' value={this.state.data.pdu_1} options={this.state.pdus.map(row => ({value:row.id, text:row.hostname}))} changeHandler={this.changeHandler} />
      <SelectInput key='pdu_2' id='pdu_2' label='PDU2' value={this.state.data.pdu_2} options={this.state.pdus.map(row => ({value:row.id, text:row.hostname}))} changeHandler={this.changeHandler} />
     </InfoCol2>
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
   buttons.push(<InfoButton key={'ri_url_'+row.id} type='ui' onClick={() => { window.open(row.url,'_blank'); }} />)
  return [
   <TextButton key={'ri_dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} />,
   row.hostname,<Fragment key='ri_buttons'>{buttons}</Fragment>
  ]
 }


 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='ri_fragment'>
   <ContentList key='ri_cl' header={this.props.type.toUpperCase()} thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <InfoButton key='ri_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
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
