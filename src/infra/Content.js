import React, { Fragment } from 'react';
import { Spinner } from './Generic.js';
import { TableHead, TableRow } from './Table.js';

// ***************************** Content ********************************
//
// base,header,buttons,thead,trows,content,listItem
//
export const ContentMain = (props) => {
 return (
  <Fragment key={props.base + '_list'}>
   <section className='content-left'>
    <ContentTable key={props.base+'_table'} {...props} />
   </section>
   <section className='content-right'>
    {props.content}
   </section>
  </Fragment>
 );
}

// base,header,buttons,thead,trows,listItem
export const ContentTable = (props) => {
 if (props.trows === null){
  return <Spinner />
 } else {
  return (
   <article className='table'>
    <p>{props.header}</p>
    {props.buttons}
    <div className='table'>
     <TableHead key={'thead_' + props.base} headers={props.thead} />
     <div className='tbody'>
      {props.trows.map((row,index) => { return <TableRow key={'tr_'+props.base+'_'+index} cells={props.listItem(row)} /> })}
     </div>
    </div>
   </article>
  );
 }
}
