import React, { Fragment } from 'react';
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner, InfoCol2, CookieContext } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.jsx';

// CONVERTED ENTIRELY

// ************** Main **************
//
export class Main extends MainBase {
 componentDidMount(){
  this.props.loadNavigation([
   {title:'Activities', onClick:() => { this.changeMain(<List key='activity_list' />)}},
   {title:'Types', onClick:() => { this.changeMain(<TypeList key='activity_type_list' />)}},
   {title:'Report', onClick:() => { this.changeMain(<Report key='activity_report' />)}}
  ])
 }
}

// ************** List **************
//
class List extends ListBase {
 constructor(props){
  super(props)
  this.thead = ['Date','Type','']
  this.header = 'Activities'
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<Info key={'activity_new_' + Math.floor(Math.random() * 10)} id='new' />) } />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.date + ' - ' + row.time,row.type,<Fragment key={'activity_buttons_'+row.id}>
   <InfoButton key={'act_info_'+row.id} type='info'  onClick={() => this.changeContent(<Info key={'activity_'+row.id} id={row.id} />) } />
   <InfoButton key={'act_delete_'+row.id} type='trash' onClick={() => this.deleteList('api/master/activity_delete',row.id,'Really delete activity') } />
   </Fragment>
  ]

}

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_info',{id:this.props.id})
   .then((result) => {
   if (result.data.user_id === null)
    result.data.user_id = this.context.cookie.id
   if (result.data.type_id === null)
    result.data.type_id = result.types[0].id
   this.setState(result);
   })
 }

 infoItems = () => [
    {tag:'select', id:'user_id', text:'User', value:this.state.data.user_id, options:this.state.users.map(row => ({value:row.id, text:row.alias}))},
    {tag:'select', id:'type_id', text:'Type', value:this.state.data.type_id, options:this.state.types.map(row => ({value:row.id, text:row.type}))},
    {tag:'input', type:'date', id:'date', text:'Date', value:this.state.data.date},
    {tag:'input', type:'time', id:'time', text:'Time', value:this.state.data.time}
   ]

 render() {
  if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Activity</h1>
     <InfoCol2 key='activity_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <textarea id='event' name='event' className='info' onChange={this.changeHandler} value={this.state.data.event} />
     <InfoButton key='activity_save' type='save' onClick={() => this.updateInfo('api/master/activity_info')} />
    </article>
   );
  }
 }
}
Info.contextType = CookieContext;

// ************** Report **************
//
export class Report extends ReportBase{
 constructor(props){
  super(props)
  this.header = 'Activities'
  this.thead = ['Time','User','Type','Event']
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_list',{group:'month',mode:'full'})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => [row.date + ' - ' + row.time,row.user,row.type,row.event]
}

// ************** TypeList **************
//
class TypeList extends ListBase {
 constructor(props){
  super(props);
  this.thead = ['ID','Type','']
  this.header= 'Activity Types'
  this.buttons=[
   <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='add' type='add' onClick={() => this.changeContent(<TypeInfo key={'activity_type_new_' + Math.floor(Math.random() * 10)} id='new' />) } />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_type_list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.id,row.type,<Fragment key='activity_buttons'>
   <InfoButton key='act_tp_info'   type='info'  onClick={() => this.changeContent(<TypeInfo key={'activity_type_'+row.id} id={row.id} />) } />
   <InfoButton key='act_tp_delete' type='trash' onClick={() => this.deleteList('api/master/activity_type_delete',row.id,'Really delete type?') } />
   </Fragment>]

}

// *************** TypeInfo ***************
//
class TypeInfo extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/master/activity_type_info',{id:this.props.id})
   .then((result) => {
   this.setState(result);
   })
 }

 infoItems = () => [ {tag:'input', type:'text', id:'type', text:'Type', value:this.state.data.type, placeholder:'name'} ]

 render() {
  if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Activity Type</h1>
     <InfoCol2 key='activity_type_content' griditems={this.infoItems()} changeHandler={this.changeHandler} />
     <InfoButton key='activity_type_save' type='save' onClick={() => this.updateInfo('api/master/activity_type_info')} />
    </article>
   );
  }
 }
}
