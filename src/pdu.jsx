import React, { Fragment, Component } from "react";
import { rest_call } from "./infra/Functions.js";
import { InfoColumns, Spinner, RimsContext, ContentList, ContentData, Result } from "./infra/UI.jsx";
import { TextInput, TextLine } from "./infra/Inputs.jsx";
import { HrefButton, ReloadButton, SearchButton, SaveButton } from "./infra/Buttons.jsx";
import { NavBar, NavButton, NavInfo } from "./infra/Navigation.js";

/*

def op(aWeb):

*/

// ************** Manage **************
//
export class Manage extends Component {
 componentDidMount(){
  rest_call("api/device/hostname",{id:this.props.id}).then(result => {
   this.context.loadNavigation(<NavBar key="pdu_navbar">
    <NavInfo key="pdu_nav_name" title={result.data} style={{float:'right'}} />
    <NavButton key="pdu_nav_inv" title="Inventory" onClick={() => this.changeContent(<Inventory key="pdu_inventory" id={this.props.id} type={this.props.type} />)} />
    <NavButton key="pdu_nav_info" title="Info" onClick={() => this.changeContent(<Info key="pdu_info" id={this.props.id} type={this.props.type} />)} />
   </NavBar>)
  })
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key="manage_base">{this.state}</Fragment>
 }
}
Manage.contextType = RimsContext;

// ************** Info **************
//
class Info extends Component{

 componentDidMount(){
  rest_call("api/"+this.props.type+"/info",{id:this.props.id}).then(result => this.setState(result))
 }

 lookupSlots = () => rest_call("api/"+this.props.type+"/info",{id:this.props.id,op:"lookup"}).then(result => this.setState(result))

 render(){
  if (this.state){
   let slots = [];
   for (let i = 0; i < this.state.data.slots; i++){
    slots.push(<TextLine key={"pi_slot_name_" + i} id={"pi_slot_name_" + i} label={"Slot " + i + " Name"} text={this.state.data[i + "_slot_name"]} />);
    slots.push(<TextLine key={"pi_slot_id_" + i} id={"pi_slot_id_" + i} label={"Slot " + i + " ID"} text={this.state.data[i + "_slot_id"]} />);
   }
   return (<div className="flexdiv centered">
    <article className="info">
     <h1>PDU Device Info ({this.props.type})</h1>
     <InfoColumns key="pi_info">
      <TextLine key="pi_slots" id="slots" label="Right/Left slots" text={JSON.stringify(this.state.data.slots === 2)} />
      {slots}
     </InfoColumns>
     <ReloadButton key="pi_btn_reload" onClick={() => this.componentDidMount() } />
     <SearchButton key="pi_btn_search" onClick={() => this.lookupSlots() } />
    </article>
   </div>)
  } else
   return <Spinner />
 }
}

// ************** Inventory **************
//
class Inventory extends Component{
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call("api/" + this.props.type + "/inventory",{id:this.props.id}).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})

 listItem = (row) => [`${row.slotname}.${row.unit}`,<HrefButton key={`pdu_inv_btn_unit_${row.slot}.${row.unit}`} onClick={() => this.changeContent(<Unit key={`pdu_unit_${row.slot}.${row.unit}`} id={this.props.id} type={this.props.type} {...row} />)} text={row.name} title='Edit port info' />,row.state]

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

/*
 data = aWeb.rest_call("avocent/inventory",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_left', SPIN='true', URL='avocent_inventory?id=%s&ip=%s'%(aWeb['id'],aWeb['ip'])))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>PDU</DIV><DIV>Position</DIV><DIV>Device</DIV><DIV CLASS=th STYLE='width:63px;'>State</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for counter,value in enumerate(data['inventory'],1):
  aWeb.wr("<DIV><DIV TITLE='Open up a browser tab for {0}'><A TARGET='_blank' HREF='https://{0}:3502'>{0}</A></DIV><DIV>{1}</DIV>".format(aWeb['ip'],'%s.%s'%(value['slotname'],value['unit'])))
  aWeb.wr("<DIV><A CLASS=z-op DIV=div_content_right URL='avocent_unit_info?id={0}&slot={1}&unit={2}&text={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV ID=div_pdu_{5}>&nbsp;".format(aWeb
['id'],value['slot'],value['unit'],value['name'], value['slotname'],counter))
  url = 'avocent_op?id=%s&slot=%s&unit=%s&div_pdu_id=%i&nstate={}'%(aWeb['id'],value['slot'],value['unit'],counter)
  div = 'div_pdu_%i'%counter
  if value['state'] == "off":
   aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on')))
  else:
   aWeb.wr(aWeb.button('stop',    DIV=div, SPIN='div_content_left', URL=url.format('off')))
   aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot')))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

*/

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
  rest_call("api/"+this.props.type+"/update",{op:'update',id:this.props.id,slot:this.props.slot,unit:this.props.unit,text:this.state.text}).then(result => this.setState({...result,wait:null}));
 }

 render(){
  let result = ''
  if (this.state.status)
   result = (this.state.status === 'OK') ? 'OK' : this.state.info;
  return <article className='info'>
   <InfoColumns key='pu_info'>
    <TextLine key='pu_slot_unit' id='su' label='Slot.Unit' text={`${this.props.slotname}.${this.props.unit}`} />
    <TextInput key='pu_slot_text' id='text' value={this.state.text} onChange={this.onChange} />
   </InfoColumns>
   <Result key='pu_result' result={result} />
   <SaveButton key='pu_btn_save' onClick={() => this.updatePDU()} title='Update pdu' />
   {this.state.wait}
  </article>
 }
}
