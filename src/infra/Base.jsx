import React, { Component, Fragment } from 'react';
import { rest_call } from './Functions.js';
import { ContentData, ContentList, ContentReport } from './Generic.js';

// ************** Main Base ****************
//
export class MainBase extends Component {
 changeContent = (elem) => this.setState(elem)

 render(){
  return  <Fragment key='main_base'>{this.state}</Fragment>
 }
}

// ************** List Base ****************
//
export class ListBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, content:null, result:null}
  this.thead = ['']
  this.header = 'ListBase'
  this.buttons = []
 }

 listItem = (row) => []

 changeContent = (elem) => this.setState({content:elem})

 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 render(){
   return <Fragment key='lb_fragment'>
    <ContentList key='lb_cl' header={this.header} thead={this.thead} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
     {this.buttons}
    </ContentList>
    <ContentData key='lb_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// ************** Report Base ****************
//
export class ReportBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null,result:null}
  this.thead = ['']
  this.header = 'ReportBase'
  this.buttons = []
 }

 listItem = (row) => []

 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id))})))

 render(){
  return <ContentReport key='rb_cr' header={this.header} thead={this.thead} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
   {this.buttons}
  </ContentReport>
 }
}

// ************** Info Base ****************
//
export class InfoBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true, content:null};
 }

 changeHandler = (e) => { var data = {...this.state.data}; data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];  this.setState({data:data}); }
 changeContent = (elem) => this.setState({content:elem})
 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))
}
