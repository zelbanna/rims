import React, { Fragment, Component } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, RimsContext, ContentList, ContentData, ContentReport } from './infra/Generic.js';
import { InfoButton, TextButton } from './infra/Buttons.jsx';
import { TextInput, SelectInput, DateInput, CheckboxInput } from './infra/Inputs.jsx';

import { List as LocationList } from './Location.jsx'

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends Component {
 componentDidMount(){
  this.context.loadNavigation([
   {title:'Inventory',   type:'dropdown', items:[
    {title:'Search', onClick:() => { this.changeContent(<Search key='search_list' changeSelf={this.changeContent} />)}},
    {title:'Vendor', onClick:() => { this.changeContent(<Vendor key='vendor_list' changeSelf={this.changeContent} />)}},
    {title:'List',   onClick:() => { this.changeContent(<List key='list' changeSelf={this.changeContent} />)}}
   ]},
   {title:'Locations', onClick:() => { this.changeContent(<LocationList key='location_list' />)}}
  ])
 }

 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}
Main.contextType = RimsContext;

// ************** List **************
//
class List extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/inventory/list',this.props.args).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.serial,row.model,<Fragment key={'inventory_buttons_'+row.id}>
   <InfoButton key={'inv_info_'+row.id} type='info'  onClick={() => this.changeContent(<Info key={'inventory_'+row.id} id={row.id} />) } />
   <InfoButton key={'inv_delete_'+row.id} type='delete' onClick={() => this.deleteList('api/inventory/delete',row.id,'Really delete item') } />
   </Fragment>
  ]

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  return <Fragment key='inv_fragment'>
   <ContentList key='inv_cl' header='Inventory' thead={['ID','Serial','Model','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
    <InfoButton key='inv_btn_reload' type='reload' onClick={() => this.componentDidMount() } />
    <InfoButton key='inv_btn_add' type='add' onClick={() => this.changeContent(<Info key={'domain_new_' + rnd()} id='new' />) } />
   </ContentList>
   <ContentData key='inv_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Search **************
//
class Search extends Component {
 constructor(props){
  super(props)
  this.state = {data:{field:'serial',search:''}}
 }

 changeHandler = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 render() {
  return (
   <article className='lineinput'>
    <h1>Inventory Search</h1>
    <div>
     <span>
      <SelectInput key='field' id='field' value={this.state.data.field} changeHandler={this.changeHandler} options={[{value:'serial',text:'Serial'},{value:'vendor',text:'Vendor'}]} />
      <TextInput key='search' id='search' value={this.state.data.search} placeholder='search' changeHandler={this.changeHandler} />
     </span>
     <InfoButton type='search' title='Search' onClick={() => this.props.changeSelf(<List key='inventory_list' args={this.state.data} changeSelf={this.props.changeSelf} />)} />
    </div>
   </article>
  )
 }
}

// ************** Info **************
//
export class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 componentDidMount(){
  rest_call('api/inventory/info',{id:this.props.id}).then(result => this.setState(result))
 }

changeHandler = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (this.state.data){
   const data = this.state.data;
   return (
    <article className='info'>
     <h1>Inventory Item</h1>
     <InfoCol2 key='inventory_content'>
      <TextInput key='vendor' id='vendor' value={data.vendor} changeHandler={this.changeHandler} />
      <TextInput key='serial' id='serial' label='S/N' value={data.serial} changeHandler={this.changeHandler} />
      <TextInput key='product' id='product' value={data.product} changeHandler={this.changeHandler} />
      <TextInput key='model' id='model' value={data.model} changeHandler={this.changeHandler} />
      <TextInput key='description' id='description' value={data.description} changeHandler={this.changeHandler} />
      <SelectInput key='location_id' id='location_id' label='Location' value={data.location_id} options={this.state.locations.map( row => ({value:row.id, text:row.name}))} changeHandler={this.changeHandler} />
      <DateInput key='receive_date' id='receive_date' label='Received' value={data.receive_date} changeHandler={this.changeHandler} />
      <TextInput key='purchase_order' id='purchase_order' label='Purchase Order' value={data.purchase_order} changeHandler={this.changeHandler} />
      <TextInput key='comments' id='comments' value={data.comments} changeHandler={this.changeHandler} />
      <CheckboxInput key='license' id='license' value={data.license} changeHandler={this.changeHandler} />
      {(data.license && <TextInput key='license_key' id='license_key' label='Key' value={data.license_key} changeHandler={this.changeHandler} />)}
      <CheckboxInput key='support_contract' id='support_contract' value={data.support_contract} changeHandler={this.changeHandler} />
      {(data.support_contract && <DateInput key='support_end_date' id='support_end_date' label='Contract End' value={data.support_end_date} changeHandler={this.changeHandler} />)}
     </InfoCol2>
     <InfoButton key='inventory_reload' type='reload' onClick={() => this.componentDidMount() } />
     <InfoButton key='inventory_save' type='save' onClick={() => this.updateInfo('api/inventory/info') } />
    </article>
   );
  } else
   return <Spinner />
 }
}

// ************** Vendor **************
//
class Vendor extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/inventory/vendor_list').then(result => this.setState(result))
 }

 listItem = (row) => [<TextButton key={'search_' +row.vendor} text={row.vendor} onClick={() => this.props.changeSelf(<List key='inventory_list' args={{field:'vendor', search:row.vendor}} changeSelf={this.props.changeSelf} />)} />,row.count]

 render(){
  return <Fragment key='inv_fragment'>
   <ContentList key='inv_cl' header='Vendors' thead={['Name','Count']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='inv_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Report **************
//
export class Report extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  rest_call('api/inventory/list', { extra:['vendor','product','description'], sort:'vendor'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.serial,row.vendor,row.model,row.product,row.description]

 render(){
  return <ContentReport key='inv_cr' header='Inventory' thead={['ID','Serial','Vendor','Model','Product','Description']} trows={this.state.data} listItem={this.listItem} />
 }
}
