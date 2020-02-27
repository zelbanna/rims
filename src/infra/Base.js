import React, { Component, Fragment } from 'react';
import { rest_call, rest_base } from './Functions.js';
import { ContentData, ContentList } from './Generic.js';

// ************** Main Base ****************
//
export class MainBase extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 changeMain = (elem) => this.setState({content:elem})

 render = () => <Fragment key='main_base'>{this.state.content}</Fragment>
}

// ************** List Base ****************
//
export class ListBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, content:null}
  this.base = 'listbase'
  this.thead = ['']
  this.header = 'ListBase'
  this.buttons = []
 }

 changeList = (elem) => this.setState({content:elem})

 deleteList = (api,id,msg) => {
  if (window.confirm(msg)){
   rest_call(rest_base + api, {id:id})
    .then((result) => {
     if(result.deleted)
      this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id ),content:null})
    })
  }
 }

 listItem = (row) => []

 render = () => <Fragment key={'listbase_content_fragment'}>
   <section className='content-left'><ContentList key={this.base+'_content_list'} base={this.base} header={this.header} thead={this.thead} trows={this.state.data} listItem={this.listItem} buttons=<Fragment key={this.base+'_buttons'}>{this.buttons}</Fragment>/></section>
   <section className='content-right'><ContentData key={this.base+'_content_data'} content={this.state.content} /></section>
  </Fragment>
}

// ************** Info Base ****************
//
export class InfoBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true, content:null}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

 changeInfo = (elem) => this.setState({content:elem})

 updateInfo = (api) => {
  rest_call(rest_base + api,{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }
}

// ************** Report Base ****************
//
export class ReportBase extends Component {
 constructor(props){
  super(props);
  this.state = {data:null}
  this.base = 'reportbase'
  this.thead = ['']
  this.header = 'ReportBase'
  this.buttons = []
 }

 listItem = (row) => []

 render = () => <ContentList key={this.base+'_content_list'} base={this.base} header={this.header} thead={this.thead} trows={this.state.data} listItem={this.listItem} buttons=<Fragment key={this.base+'_buttons'}>{this.buttons}</Fragment> />
}
