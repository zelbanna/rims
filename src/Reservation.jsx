import React, { Fragment, Component } from 'react';
import { rest_call } from './infra/Functions.js';
import { Spinner, InfoColumns, RimsContext, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { AddButton, DeleteButton, InfoButton, ReloadButton, SaveButton, LinkButton }  from './infra/Buttons.jsx';
import { RadioInput, TextInput, TextLine }  from './infra/Inputs.jsx';

import { Info as UserInfo } from './User.jsx';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/reservation/list').then(result => this.setState(result))
 }

 extendItem = (device_id,user_id,days) => {
  rest_call('api/reservation/update',{op:'extend', device_id:device_id,user_id:user_id,days:days}).then(result => this.componentDidMount())
 }

 changeContent = (elem) => this.setState({content:elem})
 deleteItem = (dev,user) => (window.confirm('Remove reservation?') && rest_call('api/reservation/update',{op:'delete', device_id:dev, user_id:user}).then(result => result.result && this.setState({data:this.state.data.filter(row => row.device_id !== dev),content:null})))

 listItem = (row) => {
  const cells = [
   <LinkButton key={'user_' + this.context.cookie.id} text={row.alias} onClick={() => this.changeContent(<UserInfo key={'user_info'+this.context.cookie.id} id={this.context.cookie.id} />) } />,
   row.hostname,
   <div className={(row.valid) ? '' : 'orange'}>{row.end}</div>
  ]
  if ((this.context.cookie.id === row.user_id) || !row.valid) {
   cells.push(
    <Fragment key='reservation_buttons'>
     <InfoButton key={'rsv_btn_info_'+row.device_id} onClick={() => { this.changeContent(<Info key={'rsv_device_'+row.device_id} device_id={row.device_id} user_id={row.user_id} />) }} title='Info'/>
     <AddButton  key={'rsv_btn_ext_'+row.device_id}  onClick={() => { this.extendItem(row.device_id,row.user_id,14) }} title='Extend reservation' />
     <DeleteButton key={'rsv_btn_del_'+row.device_id}  onClick={() => { this.deleteItem(row.device_id,row.user_id) }} title='Remove reservation' />
    </Fragment>
   )
  }
  return cells;
 }

 render(){
  return <Fragment key='rsv_fragment'>
   <ContentList key='rsv_cl' header='Reservations' thead={['User','Device','Until','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='rsv_btn_reload' onClick={() => this.componentDidMount() } />
   </ContentList>
   <ContentData key='rsv_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}
List.contextType = RimsContext;

// ************** Info **************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 componentDidMount(){
  rest_call('api/reservation/info',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (this.state.data){
   return (
    <article className='info'>
     <h1>Reservation</h1>
     <InfoColumns key='reservation_content'>
      <TextLine key='alias' id='alias' text={this.state.data.alias} />
      <TextLine key='time_start' id='Start' text={this.state.data.time_start} />
      <TextLine key='time_end' id='End' text={this.state.data.time_end} />
      <RadioInput key='shutdown' id='shutdown' value={this.state.data.shutdown} options={[{text:'no',value:0},{text:'yes',value:1},{text:'reset',value:2}]} onChange={this.onChange} />
      <TextInput key='info' id='info' value={this.state.data.info} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='rsv_btn_save' onClick={() => this.updateInfo('api/reservation/info')} />
    </article>
   );
  } else
   return <Spinner />
 }
}

// ************** Report **************
//
export class Report extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/reservation/list',{extended:true}).then(result => this.setState(result))
 }

 listItem = (row) => [row.alias,row.hostname,row.start,row.end,row.info]

 render(){
  return <ContentReport key='rsv_cr' header='Reservations' thead={['User','Device','Start','End','Info']} trows={this.state.data} listItem={this.listItem} />
 }
}
