import React, { Component } from 'react';
import { post_call } from './infra/Functions.js';
import { RimsContext, Flex, InfoArticle, InfoColumns, Spinner, ContentList, ContentData, Result } from './infra/UI.jsx';
import { TextInput, TextLine } from './infra/Inputs.jsx';
import { HrefButton, ReloadButton, SaveButton, SearchButton, StartButton, StopButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavInfo } from './infra/Navigation.jsx';

// ************** Manage **************
//
export class Manage extends Component {
 componentDidMount(){
  post_call('api/device/hostname',{id:this.props.device_id}).then(result => {
   this.context.loadNavigation(<NavBar key='pdu_navbar'>
    <NavInfo key='pdu_nav_name' title={result.data} />
    <NavButton key='pdu_nav_inv' title='Inventory' onClick={() => this.changeContent(<Inventory key='pdu_inventory' device_id={this.props.device_id} type={this.props.type} />)} />
    <NavButton key='pdu_nav_info' title='Info' onClick={() => this.changeContent(<Info key='pdu_info' device_id={this.props.device_id} type={this.props.type} />)} />
   </NavBar>)
  })
  this.setState(<Inventory key='pdu_inventory' device_id={this.props.device_id} type={this.props.type} />);
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <>{this.state}</>
 }
}
Manage.contextType = RimsContext;

// ************** Info **************
//
class Info extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/devices/'+this.props.type+'/info',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 lookupSlots = () => post_call('api/devices/'+this.props.type+'/info',{device_id:this.props.device_id,op:'lookup'}).then(result => this.setState(result))

 render(){
  if (this.state.data){
   let slots = [];
   for (let i = 0; i < this.state.data.slots; i++){
    slots.push(<TextLine key={'pi_sn_' + i} id={'pi_slot_name_' + i} label={'Slot ' + i + ' Name'} text={this.state.data[i + '_slot_name']} />);
    slots.push(<TextLine key={'pi_si_' + i} id={'pi_slot_id_' + i} label={'Slot ' + i + ' ID'} text={this.state.data[i + '_slot_id']} />);
   }
   return <Flex key='pi_flex' style={{justifyContent:'space-evenly'}}>
    <InfoArticle key='pi_article' header={'PDU Device Info - '+this.props.type}>
     <InfoColumns key='pi_info'>
      <TextLine key='pi_slots' id='slots' label='Right/Left slots' text={JSON.stringify(this.state.data.slots === 2)} />
      {slots}
     </InfoColumns>
     <ReloadButton key='pi_btn_reload' onClick={() => this.componentDidMount() } />
     <SearchButton key='pi_btn_search' onClick={() => this.lookupSlots() } />
    </InfoArticle>
   </Flex>
  } else
   return <Spinner />
 }
}

// ************** Inventory **************
//
export class Inventory extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/devices/' + this.props.type + '/inventory',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 listItem = (row,idx) => [`${row.slotname}.${row.unit}`,<HrefButton key={'inv_' + idx} onClick={() => this.changeContent(<Unit key={'pdu_unit_'+idx} device_id={this.props.device_id} type={this.props.type} {...row} />)} text={row.name} title='Edit port info' />,<Operation key={'state_'+idx} idx={idx} device_id={this.props.device_id} type={this.props.type} {...row} />]

 render(){
  if (this.state.data){
   return <>
    <ContentList key='cl' header='Inventory' thead={['Position','Device','State']} trows={this.state.data} listItem={this.listItem}>
     <ReloadButton key='reload' onClick={() => {this.setState({data:undefined}); this.componentDidMount()} } />
    </ContentList>
    <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
   </>
  } else
   return <Spinner />
 }
}

// *************** Operation ***************
//
class Operation extends Component{
 constructor(props){
  super(props)
  this.state = {state:this.props.state, status:'',wait:null};
 }

 operation = (state) => {
  this.setState({wait:<Spinner />})
  post_call('api/devices/'+this.props.type+'/op',{device_id:this.props.device_id, slot:this.props.slot, unit:this.props.unit, state:state}).then(result => this.setState({...result, wait:null}));
 }

 render(){
  const off = (this.state.state === 'off');
  return <>
   {off && <StartButton key='start' onClick={() => this.operation('on')} title={this.state.status} />}
   {!off && <StopButton key='stop' onClick={() => this.operation('off')} title={this.state.status} />}
   {!off && <ReloadButton key='reload' onClick={() => this.operation('reboot')} title={this.state.status} />}
   {this.state.wait}
  </>
 }
}

// ************** Unit **************
//
class Unit extends Component {
 constructor(props){
  super(props)
  this.state = {text:this.props.name,wait:null}
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 updatePDU = () => {
  this.setState({wait:<Spinner />, info:undefined});
  post_call('api/devices/'+this.props.type+'/update',{op:'update',device_id:this.props.device_id,slot:this.props.slot,unit:this.props.unit,text:this.state.text}).then(result => this.setState({...result,wait:null}));
 }

 render(){
  let result = ''
  if (this.state.status)
   result = (this.state.status === 'OK') ? 'OK' : this.state.info;
  return <InfoArticle key='pu_article'>
   <InfoColumns key='pu_info'>
    <TextLine key='pu_slot_unit' id='su' label='Slot.Unit' text={`${this.props.slotname}.${this.props.unit}`} />
    <TextInput key='pu_slot_text' id='text' value={this.state.text} onChange={this.onChange} />
   </InfoColumns>
   <Result key='pu_result' result={result} />
   <SaveButton key='pu_btn_save' onClick={() => this.updatePDU()} title='Update pdu' />
   {this.state.wait}
  </InfoArticle>
 }
}
