import React, { Fragment, Component } from 'react';
import { rest_call, RimsContext } from './infra/Functions.js';
import { InfoArticle, InfoColumns, Spinner, ContentList, ContentData, Result } from './infra/UI.jsx';
import { TextInput, TextLine } from './infra/Inputs.jsx';
import { HrefButton, ReloadButton, SaveButton, SearchButton, StartButton, StopButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavInfo } from './infra/Navigation.jsx';

// ************** Manage **************
//
export class Manage extends Component {
 componentDidMount(){
  rest_call('api/device/hostname',{id:this.props.device_id}).then(result => {
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
  return  <Fragment key='manage_base'>{this.state}</Fragment>
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
  rest_call('api/'+this.props.type+'/info',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 lookupSlots = () => rest_call('api/'+this.props.type+'/info',{device_id:this.props.device_id,op:'lookup'}).then(result => this.setState(result))

 render(){
  if (this.state.data){
   let slots = [];
   for (let i = 0; i < this.state.data.slots; i++){
    slots.push(<TextLine key={'pi_slot_name_' + i} id={'pi_slot_name_' + i} label={'Slot ' + i + ' Name'} text={this.state.data[i + '_slot_name']} />);
    slots.push(<TextLine key={'pi_slot_id_' + i} id={'pi_slot_id_' + i} label={'Slot ' + i + ' ID'} text={this.state.data[i + '_slot_id']} />);
   }
   return (<div className='flexdiv centered'>
    <InfoArticle key='pi_article'>
     <h1>PDU Device Info ({this.props.type})</h1>
     <InfoColumns key='pi_info'>
      <TextLine key='pi_slots' id='slots' label='Right/Left slots' text={JSON.stringify(this.state.data.slots === 2)} />
      {slots}
     </InfoColumns>
     <ReloadButton key='pi_btn_reload' onClick={() => this.componentDidMount() } />
     <SearchButton key='pi_btn_search' onClick={() => this.lookupSlots() } />
    </InfoArticle>
   </div>)
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
  rest_call('api/' + this.props.type + '/inventory',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})

 listItem = (row,idx) => [`${row.slotname}.${row.unit}`,<HrefButton key={'pdu_inv_btn_' + idx} onClick={() => this.changeContent(<Unit key={'pdu_unit_'+idx} device_id={this.props.device_id} type={this.props.type} {...row} />)} text={row.name} title='Edit port info' />,<Operation key={'pdu_state'+idx} idx={idx} device_id={this.props.device_id} type={this.props.type} {...row} />]

 render(){
  if (this.state.data){
   return <Fragment key='pdu_fragment'>
    <ContentList key='pdu_cl' header='Inventory' thead={['Position','Device','State']} trows={this.state.data} listItem={this.listItem}>
     <ReloadButton key='pdu_btn_reload' onClick={() => {this.setState({data:undefined}); this.componentDidMount()} } />
    </ContentList>
    <ContentData key='pdu_cd'>{this.state.content}</ContentData>
   </Fragment>
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
  rest_call('api/'+this.props.type+'/op',{device_id:this.props.device_id, slot:this.props.slot, unit:this.props.unit, state:state}).then(result => this.setState({...result, wait:null}));
 }

 render(){
   const off = (this.state.state === 'off');
   return <Fragment key={'pdu_frag_'+this.props.idx}>
    {off && <StartButton key={'pdu_btn_start_'+this.props.idx} onClick={() => this.operation('on')} title={this.state.status} />}
    {!off && <StopButton key={'pdu_btn_stop_'+this.props.idx} onClick={() => this.operation('off')} title={this.state.status} />}
    {!off && <ReloadButton key={'pdu_btn_reload_'+this.props.idx} onClick={() => this.operation('reboot')} title={this.state.status} />}
    {this.state.wait}
   </Fragment>
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
  rest_call('api/'+this.props.type+'/update',{op:'update',device_id:this.props.device_id,slot:this.props.slot,unit:this.props.unit,text:this.state.text}).then(result => this.setState({...result,wait:null}));
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
