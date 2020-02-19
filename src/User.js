import React, { Component, Fragment } from 'react';
import { List as ReservationList } from './Reservation.js';
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { NavBar }     from './infra/Navigation.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:null, id:null, name:null}
 }

 componentDidMount(){
  const cookie = read_cookie('rims');
  rest_call(rest_base + 'api/master/user_info',{id:cookie.id})
   .then((result) => {
    this.setState({name:result.data.name, id:cookie.id})
   })
 }

 content = (elem) => {
  this.setState({content:elem})
 }

 render() {
  const navitems = [
   {title:'Users', onClick:() => { this.content(<List  />)}},
   {title:'Reservations', onClick:() => { this.content(<ReservationList />)}},
   {title:this.state.name, className:'right navinfo'}
  ]

  return (
   <Fragment key='user_main'>
    <NavBar key='user_navbar' items={navitems} />
    <section className='content' id='div_content'>{this.state.content}</section>
   </Fragment>
  )
 }
}

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, contentright:null}
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/user_list')
   .then((result) => { this.setState(result); })
 }

 contentRight = (elem) => {
  this.setState({contentright:elem})
 }

 listItem = (row) => {
  return [row.id,row.alias,row.name,<InfoButton key={'user_'+row.id} type='info' onClick={() => { this.contentRight(<Info key={'user_info'+row.id} id={row.id} />)}} />];
 }

 render() {
  return (
  <ContentMain key='user_content' base='user' header='Users' thead={['ID','Alias','Name','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='user_header_buttons'>
      <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />
      <InfoButton key='add'    type='add'    onClick={() => {this.contentRight(<Info id='new' />)}} />
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
  const cookie = read_cookie('rims');
  this.state = {data:null, found:true, cookie_id:cookie.id}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/theme_list')
   .then((result) => {
    this.setState({themes:result});
   })
  rest_call(rest_base + 'api/master/user_info',{id:this.props.id})
   .then((result) => { this.setState(result); })
 }

 updateInfo = (event) => {
  rest_call(rest_base + 'api/master/user_info',{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }

 deleteInfo = (event) => {
  rest_call(rest_base + 'api/master/user_delete',{id:this.state.data.id})
   .then((result) => {
    console.log(JSON.stringify(result));
    this.setState({data:null, found:false});
  })
 }

 infoItems = () => {
  return [
    {tag:'input', type:'text', id:'alias', text:'Alias', value:this.state.data.alias},
    {tag:'input', type:'password', id:'password', text:'Password',placeholder:'******'},
    {tag:'input', type:'text', id:'email', text:'e-mail', value:this.state.data.email},
    {tag:'input', type:'text', id:'name', text:'Full name', value:this.state.data.name},
    {tag:'select', id:'theme', text:'Theme', value:this.state.data.theme, options:this.state.themes.map((row) => { return ({value:row, text:row})})}
   ]
 }

 render() {
  if (this.state.found === false){
   return (<article>User with id {this.props.id} removed</article>)
  } else if ((this.state.data === null) || (this.state.themses === [])){
   return (<Spinner />);
  } else {
   return (
    <article className='info'>
     <p>User Info ({this.state.data.id})</p>
     <form>
      <InfoCol2 key={'user_content'} griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='user_save' type='save' onClick={this.updateInfo} />
     { ((this.state.data.id !== 'new' && ((this.state.cookie_id === this.state.data.id) || (this.state.cookie_id === 1))) ? <InfoButton key='user_delete' type='trash' onClick={this.deleteInfo} /> : '') }
    </article>
   );
  }
 }
}

// ************** User **************
//
export class User extends Component {
 render() {
  return (
   <Fragment key='user_user'>
    <NavBar key='user_navbar' items={null} />
    <section className='content' id='div_content'>
     <section className='content-left'>
     </section>
     <section className='content-right'>
      <Info id={this.props.id} />
     </section>
    </section>
   </Fragment>
  )
 }
}
