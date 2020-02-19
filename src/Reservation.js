import React, { Component, Fragment } from 'react';
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Info as UserInfo } from './User.js';
import { Spinner }    from './infra/Generic.js';
import { InfoButton, TextButton }    from './infra/Buttons.js';
import { ContentMain, ContentTable } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';


// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  const cookie = read_cookie('rims')
  this.state = {data:null, contentright:null, cookie_id:cookie.id}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/reservation/list')
   .then((result) => { this.setState(result); })
 }

 contentRight = (elem) => {
  this.setState({contentright:elem})
 }

 extendLease = (device_id,user_id,days) => {
  rest_call(rest_base + 'api/reservation/update',{op:'extend', device_id:device_id,user_id:user_id,days:days})
 }

 deleteLease = (device_id,user_id)  => {
  rest_call(rest_base + 'api/reservation/update',{op:'delete', device_id:device_id,user_id:user_id})
   .then((result) => {
   this.setState({found:false});
   console.log(JSON.stringify(result));
  });
 }

 listItem = (row) => {
  const cells = [
   <TextButton key={'user_' + this.state.cookie_id} text={row.alias} onClick={() => { this.contentRight(<UserInfo key={'user_info'+this.state.cookie_id} id={this.state.cookie_id} />)}} />,
   row.hostname,
   <div className={(row.valid) ? '' : 'orange'}>{row.end}</div>
  ]
  if ((this.state.cookie_id === row.user_id) || (row.valid === false)) {
   cells.push(
    <Fragment key='reservation_buttons'>
     <InfoButton type='info' key={'rsv_info_'+row.device_id} onClick={() => { this.contentRight(<Info key={'rsv_device_'+row.device_id} device_id={row.device_id} user_id={row.user_id} />) }} title='Info'/>
     <InfoButton type='add'  key={'rsv_ext_'+row.device_id}  onClick={() => { this.extendLease(row.device_id,row.user_id,14) }} title='Extend reservation' />
     <InfoButton type='delete' key={'rsv_del_'+row.device_id}  onClick={() => { this.deleteLease(row.device_id,row.user_id) }} title='Remove reservation' />
    </Fragment>
   )
  }
  return cells;
 }

 render(){
  return (
   <ContentMain key='reservation_content' base='reservation' header='Reservations' thead={['User','Device','Until','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='reservation_header_buttons'>
       <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />
    </Fragment>}
    />
  );
 }
}

// ************** Info **************
//
export class Info extends Component {
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
  rest_call(rest_base + 'api/reservation/info',{device_id:this.props.device_id})
   .then((result) => { this.setState(result); })
 }

 updateInfo = (event) => {
  rest_call(rest_base + 'api/reservation/info',{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }

 render() {
  if (this.state.found === false)
   return(<article>Reservation deleted</article>);
  else if (this.state.data === null)
   return (<Spinner />);
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
     <p>Reservation ({this.state.data.device_id})</p>
     <form>
      <InfoCol2 key={'user_content'} griditems={griditems} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='reservation_save' type='save' onClick={this.updateInfo} />
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
  rest_call(rest_base + 'api/reservation/list',{extended:true})
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => { return [row.alias,row.hostname,row.start,row.end,row.info]; }

 render(){
  return(<ContentTable key='reservation_content' base='reservation' header='Reservations' thead={['User','Device','Start','End','Info']}
    trows={this.state.data} listItem={this.listItem} />
  );
 }
}
