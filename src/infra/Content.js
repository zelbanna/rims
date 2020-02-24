import React, { Fragment } from 'react';
import { Spinner } from './Generic.js';

// ***************************** Content ********************************
//
// base,header,buttons,thead,trows,content,listItem
//
export const ContentMain = (props) => {
 return (
  <Fragment key={'content_main_fragment'}>
   <section className='content-left'><ContentList key={'content_list'} {...props} /></section>
   <section className='content-right'><ContentData key={'content_data'} content={props.content} /></section>
  </Fragment>
 );
}

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

const ContentData = (props) => {
 return <Fragment key='content_data_fragment'>{props.content}</Fragment>
}

// ***************************** Table ********************************

export const TableHead = (props) => {
 return <div className='thead'>{props.headers.map((row,index) => { return <div key={'th_'+index}>{row}</div> })}</div>
}

export const TableRow = (props) => {
 return <div>{props.cells.map((row,index) => { return <div key={'tr_'+index}>{row}</div> })}</div>
}
