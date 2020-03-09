import React, { Fragment } from 'react';
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner, InfoCol2, CookieContext } from './infra/Generic.js';
import { ListBase, ReportBase, InfoBase }    from './infra/Base.jsx';
import { InfoButton, TextButton }  from './infra/Buttons.jsx';

import { Info as UserInfo } from './User.jsx';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props);
  this.thead = ['User','Device','Until','']
  this.header = 'Reservations'
  this.buttons = [<InfoButton key='reload' type='reload' onClick={() => this.componentDidMount()} />]

 }

 componentDidMount(){
  rest_call(rest_base + 'api/reservation/list')
   .then((result) => this.setState(result) )
 }

 extendItem = (device_id,user_id,days) => {
  rest_call(rest_base + 'api/reservation/update',{op:'extend', device_id:device_id,user_id:user_id,days:days})
  this.componentDidMount();
 }

 deleteItem = (device_id,user_id,msg)  => {
  if (window.confirm(msg)){
   rest_call(rest_base + 'api/reservation/update',{op:'delete', device_id:device_id,user_id:user_id})
    .then((result) => {
     if(result.result)
      this.setState({data:this.state.data.filter((row,index,arr) => row.device_id !== device_id),content:null})
    })
  }
 }

 listItem = (row) => {
  const cells = [
   <TextButton key={'user_' + this.context.cookie.id} text={row.alias} onClick={() => this.changeContent(<UserInfo key={'user_info'+this.context.cookie.id} id={this.context.cookie.id} />) } />,
   row.hostname,
   <div className={(row.valid) ? '' : 'orange'}>{row.end}</div>
  ]
  if ((this.context.cookie.id === row.user_id) || (row.valid === false)) {
   cells.push(
    <Fragment key='reservation_buttons'>
     <InfoButton type='info' key={'rsv_info_'+row.device_id} onClick={() => { this.changeContent(<Info key={'rsv_device_'+row.device_id} device_id={row.device_id} user_id={row.user_id} />) }} title='Info'/>
     <InfoButton type='add'  key={'rsv_ext_'+row.device_id}  onClick={() => { this.extendItem(row.device_id,row.user_id,14) }} title='Extend reservation' />
     <InfoButton type='delete' key={'rsv_del_'+row.device_id}  onClick={() => { this.deleteItem(row.device_id,row.user_id,'Remove reservatin?') }} title='Remove reservation' />
    </Fragment>
   )
  }
  return cells;
 }
}
List.contextType = CookieContext;

// ************** Info **************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/reservation/info',{device_id:this.props.device_id})
   .then((result) => this.setState(result) )
 }

 render() {
  if (this.state.found === false)
   return <article>Reservation deleted</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   const griditems = [
    {tag:'span',  id:'alias', text:'Alias', value:this.state.data.alias},
    {tag:'span',  id:'time_start', text:'Start', value:this.state.data.time_start},
    {tag:'span',  id:'time_end',   text:'End',   value:this.state.data.time_end},
    {tag:'input', type:'radio', id:'shutdown', text:'Shutdown', value:this.state.data.shutdown, options:[{text:'no',value:0},{text:'yes',value:1},{text:'reset',value:2}]},
    {tag:'input', type:'text', id:'info', text:'Info', value:this.state.data.info}
   ]
   return (
    <article className='info'>
     <h1>Reservation ({this.state.data.device_id})</h1>
     <InfoCol2 key={'user_content'} griditems={griditems} changeHandler={this.changeHandler} />
     <InfoButton key='reservation_save' type='save' onClick={() => this.updateInfo('api/reservation/info')} />
    </article>
   );
  }
 }
}

// ************** Report **************
//
export class Report extends ReportBase {
 constructor(props){
  super(props);
  this.thead = ['User','Device','Start','End','Info']
 }

 componentDidMount(){
  rest_call(rest_base + 'api/reservation/list',{extended:true})
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.alias,row.hostname,row.start,row.end,row.info]
}
