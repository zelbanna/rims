import React, { Component } from 'react';
import { post_call } from './infra/Functions.js';
import { RimsContext, Spinner, InfoArticle, InfoColumns, LineArticle, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { AddButton, DeleteButton, InfoButton, ReloadButton, SaveButton, SearchButton } from './infra/Buttons.jsx';
import { RadioInput, TextInput, TextLine }  from './infra/Inputs.jsx';

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  post_call('api/reservation/list').then(result => this.setState({content:null, ...result}))
 }

 extendItem = (device_id,user_id,days) => {
  post_call('api/reservation/extend',{device_id:device_id, user_id:user_id, days:days}).then(result => this.componentDidMount())
 }

 changeContent = (elem) => this.setState({content:elem})

 deleteItem = (dev,user) => (window.confirm('Remove reservation?') && post_call('api/reservation/delete',{device_id:dev, user_id:user}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => row.device_id !== dev),content:null})))

 listItem = (row) => {
  const buttons = (this.context.settings.id === row.user_id || !row.valid);
  return [row.alias,row.hostname,row.end,<>
   {buttons && <InfoButton key='info' onClick={() => { this.changeContent(<Info key={'rsv_device_'+row.device_id} device_id={row.device_id} user_id={row.user_id} />) }} title='Info'/>}
   {buttons && <AddButton  key='ext' onClick={() => { this.extendItem(row.device_id,row.user_id,14) }} title='Extend reservation' />}
   {buttons && <DeleteButton key='del' onClick={() => { this.deleteItem(row.device_id,row.user_id) }} title='Remove reservation' />}
  </>]
 }

 render(){
  return <>
   <ContentList key='rsv_cl' header='Reservations' thead={['User','Device','Until','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<New key='rsv_new' />)} />
   </ContentList>
   <ContentData key='rsv_cd'>{this.state.content}</ContentData>
  </>
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
  post_call('api/reservation/info',{device_id:this.props.device_id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 updateInfo = () =>  post_call('api/reservation/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 extendItem = (days) => {
  post_call('api/reservation/extend',{device_id:this.state.data.device_id, user_id:this.state.data.user_id, days:days}).then(result => result.status === 'OK' && this.componentDidMount())
 }

 render() {
  if (this.state.data){
   return <InfoArticle key='rsv_article' header='Reservation'>
     <InfoColumns key='reservation_content'>
      <TextLine key='alias' id='alias' text={this.state.data.alias} />
      <TextLine key='time_start' id='Start' text={this.state.data.time_start} />
      <TextLine key='time_end' id='End' text={this.state.data.time_end} />
      <RadioInput key='shutdown' id='shutdown' value={this.state.data.shutdown} options={[{text:'no',value:'no'},{text:'yes',value:'yes'},{text:'reset',value:'reset'}]} onChange={this.onChange} />
      <TextInput key='info' id='info' value={this.state.data.info} onChange={this.onChange} />
     </InfoColumns>
     {this.state.data.user_id === this.context.settings.id && <SaveButton key='rsv_btn_save' onClick={() => this.updateInfo()} title='Save' />}
     {this.state.data.user_id === this.context.settings.id && <AddButton key='rsv_btn_extend' onClick={() => this.extendItem(14)} title='Extend' />}
    </InfoArticle>
  } else
   return <Spinner />
 }
}
Info.contextType = RimsContext;

// ************** Report **************
//
class New extends Component {
 constructor(props){
  super(props)
  this.state = {device:'',device_id:undefined,matching:''}
 }

 onChange = (e) => {
  this.setState({device:e.target.value});
 }

 findDevice = () => post_call('api/device/search',{hostname:this.state.device}).then(result => result.found && this.setState({device_id:result.data.id,matching:result.data.hostname}));

 reserveDevice = () => post_call('api/reservation/new',{device_id:this.state.device_id,user_id:this.context.settings.id}).then(result => result.status === 'OK' && this.setState({device:'',device_id:undefined,matching:''}));

 render(){
  return <LineArticle key='rsv_art' header='New reservation'>
   <TextInput key='device' id='device' label='search device' onChange={this.onChange} value={this.state.device} placeholder='search' /> found <TextLine key='matching' id='matching device' text={this.state.matching} />
   {this.state.device && <SearchButton key='rsv_btn_search' onClick={() => this.findDevice()} title='Find device' />}
   {this.state.device_id && <AddButton key='rsv_btn_new' onClick={() => this.reserveDevice()} title='Reserve device' />}
   </LineArticle>
 }
}
New.contextType = RimsContext;

// ************** Report **************
//
export class Report extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 componentDidMount(){
  post_call('api/reservation/list',{extended:true}).then(result => this.setState(result))
 }

 listItem = (row) => [row.alias,row.hostname,row.start,row.end,row.info]

 render(){
  return <ContentReport key='rsv_cr' header='Reservations' thead={['User','Device','Start','End','Info']} trows={this.state.data} listItem={this.listItem} />
 }
}
