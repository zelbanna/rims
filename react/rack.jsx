import React, { Component } from 'react';
import { post_call, rnd } from './infra/Functions.js';
import { RimsContext, Spinner, InfoArticle, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
import { TextInput, SelectInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, GoButton, InfoButton, ItemsButton, ReloadButton, SaveButton, HrefButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton } from './infra/Navigation.jsx'
import styles from './infra/rack.module.css';

import { Main as DeviceMain, Info as DeviceInfo } from './device.jsx';
import { List as LocationList, Info as LocationInfo } from './location.jsx';

// *************** Main ***************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = <List key='rack_list' />
 }

 componentDidMount(){
  this.compileNavItems()
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.compileNavItems();
 }

 compileNavItems = () => this.context.loadNavigation(<NavBar key='rack_navbar'>
   <NavDropDown key='dev_nav_racks' title='Rack'>
    <NavDropButton key='dev_nav_all_rack' title='Racks' onClick={() => this.changeContent(<List key='rack_list' />)} />
    <NavDropButton key='dev_nav_all_pdu' title='PDUs' onClick={() => this.changeContent(<Infra key='pdu_list' type='pdu' />)} />
    <NavDropButton key='dev_nav_all_con' title='Consoles' onClick={() => this.changeContent(<Infra key='console_list' type='console' />)} />
   </NavDropDown>
   <NavButton key='dev_nav_loc' title='Locations' onClick={() => this.changeContent(<LocationList key='location_list' />)}/>
  </NavBar>)

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <>{this.state}</>
 }
}
Main.contextType = RimsContext;

// *************** List ***************
//
export class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/rack/list',{sort:'name'}).then(result => this.setState(result))
 }

 listItem = (row) => [<HrefButton key={'rl_btn_loc_'+row.id} text={row.location} onClick={() => this.changeContent(<LocationInfo key={'li_'+row.location_id} id={row.location_id} />)} />,row.name,<>
   <InfoButton key='info' onClick={() => this.changeContent(<Info key={'rack_info_'+row.id} id={row.id} />)} title='Rack information' />
   <GoButton key='go' onClick={() => this.context.changeMain(<DeviceMain key={'rack_device_'+row.id} rack_id={row.id} />)} title='Rack inventory' />
   <ItemsButton key='items' onClick={() => this.changeContent(<Layout key={'rack_layout_'+row.id} id={row.id} changeSelf={this.changeContent} />)} title='Rack layout'/>
   <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete rack' />
  </>]

 deleteList = (id) => (window.confirm('Really delete rack?') && post_call('api/rack/delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 render(){
  return <>
   <ContentList key='cl' header='Racks' thead={['Location','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount()} />
    <AddButton key='add' onClick={() => this.changeContent(<Info key={'rack_new_' + rnd()} id='new' />)} title='Add rack' />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </>
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

 updateInfo = () =>  post_call('api/rack/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  post_call('api/rack/info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (this.state.data)
   return <InfoArticle key='rack_article' header='Rack'>
    <InfoColumns key='rack_content'>
     <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
     <TextInput key='size' id='size' value={this.state.data.size} onChange={this.onChange} />
     <SelectInput key='console' id='console' value={this.state.data.console} onChange={this.onChange}>{this.state.consoles.map(row => <option key={row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
     <SelectInput key='location_id' id='location_id' label='Location' value={this.state.data.location_id} onChange={this.onChange}>{this.state.locations.map(row => <option key={row.id} value={row.id}>{row.name}</option>)}</SelectInput>
     <SelectInput key='pdu_1' id='pdu_1' label='PDU1' value={this.state.data.pdu_1} onChange={this.onChange}>{this.state.pdus.map(row => <option key={row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
     <SelectInput key='pdu_2' id='pdu_2' label='PDU2' value={this.state.data.pdu_2} onChange={this.onChange}>{this.state.pdus.map(row => <option key={row.id} value={row.id}>{row.hostname}</option>)}</SelectInput>
    </InfoColumns>
    <SaveButton key='ri_btn_save' onClick={() => this.updateInfo()} title='Save' />
   </InfoArticle>
  else
   return <Spinner />
 }
}

// *************** Layout ***************
//
export class Layout extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/rack/devices',{id:this.props.id}).then(result => this.setState(result))
 }

 changeContent = (elem) => {
  if(this.props.changeSelf)
   this.props.changeSelf(elem);
 }

 createRack(id,content,sign){
  const rack = [];
  for (let i = 1; i < this.state.size+1; i++)
   rack.push(<div key={'left_'+i} className={styles.rackLeft} style={{gridRow:-i}}>{i}</div>,<div key={'right_'+i} className={styles.rackRight} style={{gridRow:-i}}>{i}</div>)
  content.forEach(dev => rack.push(<div key={'dev_' + dev.id} className={styles.rackItem} style={{gridRowStart:this.state.size+2-sign*dev.rack_unit, gridRowEnd:this.state.size+2-(sign*dev.rack_unit+dev.rack_size)}}><HrefButton key={'rd_btn_'+dev.id} style={{color:'var(--ui-txt-color)'}} onClick={() => this.changeContent(<DeviceInfo key='device_info' id={dev.id} />)} text={dev.hostname} /></div>))
  return <div className={styles.rack} style={{grid:`repeat(${this.state.size-1}, 2vw)/2vw 25vw 2vw`}}>{rack}</div>
 }

 render(){
  if (this.state.size) {
   return <>
    <InfoArticle key='rl_front' header='Front'>
     {this.createRack('front',this.state.front,1)}
    </InfoArticle>
    <InfoArticle key='rl_back' header='Back'>
     {this.createRack('back',this.state.back,-1)}
    </InfoArticle>
   </>
  } else
   return <Spinner />
 }
}

// *************** Infra ***************
//
export class Infra extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/device/list',{field:'base',search:this.props.type,extra:['type']}).then(result => this.setState(result))
 }

 listItem = (row) => [<HrefButton key={'dev_'+row.id} text={row.id} onClick={() => this.changeContent(<DeviceInfo key={'device_' + row.id} id={row.id} />)} title='Device info'/>,row.hostname,<InfoButton key={'rinfra_btn_' + row.id} onClick={() => this.context.changeMain({module:row.type_base,function:'Manage',args:{device_id:row.id, type:row.type_name}})} title='Manage device' />]

 render(){
  return <>
   <ContentList key='cl' header={this.props.type} thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount()} />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
  </>
 }
}
Infra.contextType = RimsContext;
