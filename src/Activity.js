import React, { Component, Fragment } from 'react';
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain, ContentList } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 content = (elem) => {
  this.setState({content:elem})
 }

 componentDidMount(){
  this.props.loadNavigation([
   {title:'Activities', onClick:() => { this.content(<List key='activity_list' />)}},
   {title:'Types', onClick:() => { this.content(<TypeList key='activity_type_list' />)}},
   {title:'Report', onClick:() => { this.content(<Report key='activity_report' />)}}
  ])
 }

 render() {
  return (
   <Fragment key='activity_main'>
    {this.state.content}
   </Fragment>
  )
 }
}

// ************** List **************
//
class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, contentright:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_list')
   .then((result) => { this.setState(result); })
 }

 contentRight = (elem) => {
  this.setState({contentright:elem});
 }

 deleteItem = (id,msg)  => {
  if(window.confirm(msg)){
   rest_call(rest_base + 'api/master/activity_delete',{id:id})
    .then((result) => {
    if(result.deleted)
     this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id)})
   })
  }
 }

 listItem = (row) => {
  return [row.date + ' - ' + row.time,row.type,<Fragment key='activity_buttons'>
   <InfoButton key='act_info'   type='info'  onClick={() => { this.contentRight(<Info key={'activity_'+row.id} id={row.id} />) }} />
   <InfoButton key='act_delete' type='trash' onClick={() => { this.deleteItem(row.id,'Really delete activity') }} />
   </Fragment>
  ];
 }

 render(){
  return <ContentMain key='activity_content' base='activity' header='Activities' thead={['Date','Type','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='activity_header_buttons'>
     <InfoButton key='reload' type='reload' onClick={() => { this.componentDidMount() }} />
     <InfoButton key='add' type='add' onClick={() => { this.contentRight(<Info key={'activity_new_' + Math.floor(Math.random() * 10)} id='new' />) }} />
    </Fragment>} />
 }
}

// *************** Info ***************
//
class Info extends Component {
  constructor(props) {
  super(props)
  const cookie = read_cookie('rims')
  this.state = {data:null, found:true, cookie_id:cookie.id}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_info',{id:this.props.id})
   .then((result) => {
   if (result.data.user_id === null)
    result.data.user_id = this.state.cookie_id
   if (result.data.type_id === null)
    result.data.type_id = result.types[0].id
   this.setState(result);
   })
 }

 updateInfo = () => {
  rest_call(rest_base + 'api/master/activity_info',{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => {
  return [
    {tag:'select', id:'user_id', text:'User', value:this.state.data.user_id, options:this.state.users.map((row) => { return ({value:row.id, text:row.alias})})},
    {tag:'select', id:'type_id', text:'Type', value:this.state.data.type_id, options:this.state.types.map((row) => { return ({value:row.id, text:row.type})})},
    {tag:'input', type:'date', id:'date', text:'Date', value:this.state.data.date},
    {tag:'input', type:'time', id:'time', text:'Time', value:this.state.data.time}
   ]
 }

 render() {
  if (this.state.found === false)
   return <article>User with id: {this.props.id} removed</article>
  else if ((this.state.data === null) || (this.state.themses === []))
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Activity ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='activity_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
      <textarea id='event' name='event' className='info' onChange={this.handleChange} value={this.state.data.event} />
     </form>
     <InfoButton key='activity_save' type='save' onClick={this.updateInfo} />
    </article>
   );
  }
 }
}

// ************** Report **************
//
export class Report extends Component{
 constructor(props){
  super(props);
  this.state = {data:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_list',{group:'month',mode:'full'})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => {
  return [row.date + ' - ' + row.time,row.user,row.type,row.event];
 }

 render(){
  return <ContentList key='activity_report' base='activity' header='Activities' thead={['Time','User','Type','Event']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={[]} />
 }
}


// ************** TypeList **************
//
class TypeList extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, contentright:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_type_list')
   .then((result) => { this.setState(result); })
 }

 contentRight = (elem) => {
  this.setState({contentright:elem});
 }

 deleteItem = (id,msg)  => {
  if (window.confirm(msg)){
   rest_call(rest_base + 'api/master/activity_type_delete',{id:id})
    .then((result) => {
    if(result.deleted)
     this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id)})
   })
  }
 }

 listItem = (row) => {
  return [row.id,row.type,<Fragment key='activity_buttons'>
   <InfoButton key='act_tp_info'   type='info'  onClick={() => { this.contentRight(<TypeInfo key={'activity_type_'+row.id} id={row.id} />) }} />
   <InfoButton key='act_tp_delete' type='trash' onClick={() => { this.deleteItem(row.id,'Really delete type?') }} />
   </Fragment>]
 }

 render(){
  return <ContentMain key='activity_type_content' base='activity_type' header='Activity Types' thead={['ID','Type','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='activity_type_header_buttons'>
       <InfoButton key='reload' type='reload' onClick={() => { this.componentDidMount() }} />
       <InfoButton key='add' type='add' onClick={() => { this.contentRight(<TypeInfo key={'activity_type_new_' + Math.floor(Math.random() * 10)} id='new' />) }} />
    </Fragment>} />
 }
}

// *************** TypeInfo ***************
//
class TypeInfo extends Component {
  constructor(props) {
  super(props)
  this.state = {data:null, found:true}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_type_info',{id:this.props.id})
   .then((result) => {
   this.setState(result);
   })
 }

 updateInfo = () => {
  rest_call(rest_base + 'api/master/activity_type_info',{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => {
  return [ {tag:'input', type:'text', id:'type', text:'Type', value:this.state.data.type} ]
 }

 render() {
  if (this.state.found === false)
   return <article>User with id: {this.props.id} removed</article>
  else if ((this.state.data === null) || (this.state.themses === []))
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Activity Type ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='activity_type_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='activity_type_save' type='save' onClick={this.updateInfo} />
    </article>
   );
  }
 }
}
