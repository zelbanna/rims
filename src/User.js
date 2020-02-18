import React, { Component } from 'react';
import { List as ReservationList } from './Reservation.js';
import { rest_call, rest_base, read_cookie } from './Functions.js';
import { Spinner } from './UI.js';

export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {loaded:false, content:null, id:null, name:null}
 }

 componentDidMount(){
  const cookie = read_cookie('rims');
  rest_call(rest_base + 'api/master/user_info',{id:cookie.id})
   .then((result) => {
    this.setState({name:result.data.name, id:cookie.id})
   })
 }

 changeContent = (elem) => {
  this.setState(() => { return {content:elem} })
 }

 render() {
  return (
   <React.Fragment key='user_main'>
    <nav>
     <ul>
      <li><a onClick={() => { this.changeContent(<List />)}}>Users</a></li>
      <li><a onClick={() => { this.changeContent(<ReservationList />)}}>Reservations</a></li>
      <li className='right navinfo'><a>{this.state.name}</a></li>
     </ul>
    </nav>
    <section className='content' id='div_content'>{this.state.content}</section>
   </React.Fragment>
  )
 }
}

export class User extends Component {
 constructor(props){
  super(props);
 }

 render() {
  return (<div>User User</div>);
 }
}

export class List extends Component {
 constructor(props){
  super(props);
  this.state = {loaded:false}
 }

 render() {
  if (this.state.loaded == false){
   return (<Spinner />);
  } else {
   return (<div>User List</div>);
  }
 }
}

export class Info extends Component {

 render() {
  return (<div>User Info</div>);
 }
}

export class Delete extends Component {

 render() {
  return (<div>User Delete</div>);
 }
}
