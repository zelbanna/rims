import React, { Component, Fragment } from 'react';
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { NavBar }     from './infra/Navigation.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain, ContentTable } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

// ************** Main **************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:null, id:null, name:null}
 }

 content = (elem) => {
  this.setState({content:elem})
 }

 render() {
  const navitems = [
   {title:'Activities', onClick:() => { this.content(<List  />)}},
   {title:'Report', onClick:() => { this.content(<Report />)}}
  ]
  return (
   <Fragment key='activity_main'>
    <NavBar key='activity_navbar' items={navitems} />
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
  rest_call(rest_base + 'api/master/activity_list')
   .then((result) => { this.setState(result); })
 }

 contentRight = (elem) => {
  this.setState({contentright:elem});
 }

 listItem = (row) => {
  const cells = [row.date + ' - ' + row.time,row.type,<Fragment key='activity_buttons'>
   <InfoButton key='act_info'   type='info'   onClick={() => { this.contentRight('info'); }} />
   <InfoButton key='act_delete' type='delete' onClick={() => { this.contentRight('delete'); }} />
   </Fragment>
  ]
  return cells

 }

 render(){
  return (
   <ContentMain key='activity_content' base='activity' header='Activities' thead={['Date','Type','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='activity_header_buttons'>
       <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />
       <InfoButton key='add' type='add' onClick={() => {this.componentDidMount()}} />
       <InfoButton key='info' type='info' onClick={() => {this.componentDidMount()}} />
    </Fragment>}
    />
  );
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
  return (
   <ContentTable key='activity_report' base='activity' header='Activities' thead={['Time','User','Type','Event']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={[]} />
  );
 }
}
