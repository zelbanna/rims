import React, { Component, Fragment } from 'react';
import { rest_call, rest_base } from './Functions.js';

// **************************** Generic ********************************

export const Spinner = () => {
 return <div className='overlay'><div className='loader'></div></div>
}

export const StateMap = (props) => {
 return <div className={'state '+ {unknown:'grey',up:'green',down:'red'}[props.state] || 'orange'} />
}

// ************** Main Base ****************
//
export class MainBase extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 changeMain = (elem) => { this.setState({content:elem}) }

 render() {
  return <Fragment key='main_base'>{this.state.content}</Fragment>
 }
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

 changeList = (elem) => { this.setState({content:elem}) }

 deleteList = (api,id,msg) => {
  if (window.confirm(msg)){
   rest_call(rest_base + api, {id:id})
    .then((result) => {
     if(result.deleted)
      this.setState({data:this.state.data.filter((row,index,arr) => { return row.id !== id }),content:null})
    })
  }
 }

 listItem = (row) => { return [] }

 render() {
  return <Fragment key={'listbase_content_fragment'}>
   <section className='content-left'><ContentList key={this.base+'_content_list'} base={this.base} header={this.header} thead={this.thead} trows={this.state.data} listItem={this.listItem} buttons=<Fragment key={this.base+'_buttons'}>{this.buttons}</Fragment>/></section>
   <section className='content-right'><ContentData key={this.base+'_content_data'} content={this.state.content} /></section>
  </Fragment>
 }
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

 changeInfo = (elem) => { this.setState({content:elem}); }

 updateInfo = (api) => {
  rest_call(rest_base + api,{op:'update', ...this.state.data})
   .then((result) => { this.setState(result); })
 }
}

// ***************************** Content ********************************

// base,header,buttons,thead,trows,listItem
export const ContentList = (props) => {
 if (props.trows === null){
  return <Spinner />
 } else {
  return (
   <article className='table'>
    <h1>{props.header}</h1>
    {props.buttons}
    <div className='table'>
     <TableHead key={'content_thead'} headers={props.thead} />
     <div className='tbody'>
      {props.trows.map((row,index) => { return <TableRow key={'content_trow_'+props.base+'_'+index} cells={props.listItem(row)} /> })}
     </div>
    </div>
   </article>
  );
 }
}

export const ContentData = (props) => {
 return <Fragment key='content_data_fragment'>{props.content}</Fragment>
}

// ***************************** Table ********************************

export const TableHead = (props) => {
 return <div className='thead'>{props.headers.map((row,index) => { return <div key={'th_'+index}>{row}</div> })}</div>
}

export const TableRow = (props) => {
 return <div>{props.cells.map((row,index) => { return <div key={'tr_'+index}>{row}</div> })}</div>
}

