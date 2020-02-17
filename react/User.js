import React, { Component } from 'react';
import { List as ReservationList } from './Reservation.js';
import { rest_call, rest_base, read_cookie } from './Functions.js';

export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {loaded:false, content:null}
 }

 componentDidMount(){
  const cookie = read_cookie('rims');
  console.log(cookie.id);
  rest_call(rest_base + 'api/master/user_info',{id:cookie.id})
   .then((result) => {
    this.setState(result)
    console.log(result)
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
      <li className='right navinfo'><a>FULLNAME</a></li>
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
  return (<div>User User {this.props}</div>);
 }
}

export class List extends Component {

 render() {
  return (<div>User List</div>);
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
