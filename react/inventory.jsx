import React, { Fragment, Component } from 'react'
import { post_call, rnd } from './infra/Functions.js';
import { RimsContext, Spinner, LineArticle, InfoArticle, InfoColumns, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextInput, SearchInput, SelectInput, DateInput, CheckboxInput } from './infra/Inputs.jsx';
import { AddButton, DeleteButton, InfoButton, ReloadButton, SaveButton, SearchButton, HrefButton } from './infra/Buttons.jsx';
import { NavBar, NavButton, NavDropDown, NavDropButton } from './infra/Navigation.jsx';

// ************** Main **************
//
export class Main extends Component {

 componentDidMount(){
  this.compileNavItems()
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.compileNavItems()
 }

 compileNavItems = () => this.context.loadNavigation(<NavBar key='inventory_navbar'>
   <NavDropDown key='inv_nav_inv' title='Inventory'>
    <NavDropButton key='inv_nav_srch' title='Search' onClick={() => this.changeContent(<Search key='search_list' changeSelf={this.changeContent} />)} />
    <NavDropButton key='inv_nav_vend' title='Vendor' onClick={() => this.changeContent(<Vendor key='vendor_list' changeSelf={this.changeContent} />)} />
    <NavDropButton key='inv_nav_list' title='List'   onClick={() => this.changeContent(<List key='list' changeSelf={this.changeContent} />)} />
   </NavDropDown>
   <NavButton key='inv_nav_loc' title='Locations' onClick={() => this.changeLocation()} />
  </NavBar>)

 changeLocation = () => import('./location.jsx').then(lib => this.setState(<lib.List key='location_list' />));

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
  this.state = {searchfield:''}
 }

 componentDidMount(){
  post_call('api/inventory/list',this.props.args).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.serial,row.model,<Fragment key={'inventory_buttons_'+row.id}>
   <InfoButton key={'inv_btn_info_'+row.id}  onClick={() => this.changeContent(<Info key={'inventory_'+row.id} id={row.id} />) } title='View inventory item' />
   <DeleteButton key={'inv_btn_delete_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete inventory item' />
  </Fragment>]

 searchHandler = (e) => this.setState({searchfield:e.target.value})
 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete item') && post_call('api/inventory/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
  if (!this.state.data)
   return <Spinner />
  else {
   let inv_list = this.state.data.filter(row => (row.model.includes(this.state.searchfield) || row.serial.includes(this.state.searchfield)));
   return <Fragment key='inv_fragment'>
    <ContentList key='inv_cl' header='Inventory' thead={['ID','Serial','Model','']} trows={inv_list} listItem={this.listItem} result={this.state.result}>
     <ReloadButton key='inv_btn_reload' onClick={() => this.componentDidMount() } />
     <AddButton key='inv_btn_add' onClick={() => this.changeContent(<Info key={'inventory_new_' + rnd()} id='new' />) } title='Add inventory item' />
     <SearchInput key='dl_search' searchHandler={this.searchHandler} value={this.state.searchfield} placeholder='Search inventory (case sensitive)' />
    </ContentList>
    <ContentData key='inv_cd'>{this.state.content}</ContentData>
   </Fragment>
  }
 }
}

// ************** Search **************
//
class Search extends Component {
 constructor(props){
  super(props)
  this.state = {data:{field:'serial',search:''}}
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})

 render() {
  return <LineArticle key='inv_srch_art' header='Inventory search'>
   <SelectInput key='field' id='field' value={this.state.data.field} onChange={this.onChange}><option value='serial'>Serial</option><option value='vendor'>Vendor</option></SelectInput>
   <TextInput key='search' id='search' value={this.state.data.search} placeholder='search' onChange={this.onChange} />
   <SearchButton key='inv_btn_search' onClick={() => this.changeContent(<List key='inventory_list' args={this.state.data} />)} title='Search inventory' />
  </LineArticle>
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
  post_call('api/inventory/info',{id:this.props.id}).then(result => this.setState(result))
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target[(e.target.type !== 'checkbox') ? 'value' : 'checked']}})

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => post_call('api/inventory/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 render() {
  if (this.state.data){
   const data = this.state.data;
   return <InfoArticle key='inv_article' header='Inventory Item'>
     <InfoColumns key='inv_content'>
      <TextInput key='vendor' id='vendor' value={data.vendor} onChange={this.onChange} />
      <TextInput key='serial' id='serial' label='S/N' value={data.serial} onChange={this.onChange} />
      <TextInput key='product' id='product' value={data.product} onChange={this.onChange} />
      <TextInput key='model' id='model' value={data.model} onChange={this.onChange} />
      <TextInput key='description' id='description' value={data.description} onChange={this.onChange} />
      <SelectInput key='location_id' id='location_id' label='Location' value={data.location_id} onChange={this.onChange}>{this.state.locations.map((row,idx) => <option key={'ii_'+idx} value={row.id}>{row.name}</option>)}</SelectInput>
      <DateInput key='receive_date' id='receive_date' label='Received' value={data.receive_date} onChange={this.onChange} />
      <TextInput key='purchase_order' id='purchase_order' label='Purchase Order' value={data.purchase_order} onChange={this.onChange} />
      <CheckboxInput key='license' id='license' value={data.license} onChange={this.onChange} />
      {(data.license && <TextInput key='license_key' id='license_key' label='Key' value={data.license_key} onChange={this.onChange} />)}
      <CheckboxInput key='support_contract' id='support_contract' value={data.support_contract} onChange={this.onChange} />
      {(data.support_contract && <DateInput key='support_end_date' id='support_end_date' label='Contract End' value={data.support_end_date} onChange={this.onChange} />)}
      <TextInput key='comments' id='comments' value={data.comments} onChange={this.onChange} />
     </InfoColumns>
     <ReloadButton key='inv_btn_reload' onClick={() => this.componentDidMount() } />
     <SaveButton key='inv_btn_save' onClick={() => this.updateInfo()} title='Save' />
    </InfoArticle>
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
  post_call('api/inventory/vendor_list').then(result => this.setState(result))
 }

 changeContent = (elem) => this.props.changeSelf(elem);

 listItem = (row) => [<HrefButton key={'search_' +row.vendor} text={row.vendor} onClick={() => this.changeContent(<List key='inventory_list' args={{field:'vendor', search:row.vendor}} />)} />,row.count]

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
  post_call('api/inventory/list', { extra:['vendor','product','description'], sort:'vendor'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.id,row.serial,row.vendor,row.model,row.product,row.description]

 render(){
  return <ContentReport key='inv_cr' header='Inventory' thead={['ID','Serial','Vendor','Model','Product','Description']} trows={this.state.data} listItem={this.listItem} />
 }
}
