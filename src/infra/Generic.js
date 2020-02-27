import React, { Fragment } from 'react';

// **************************** Generic ********************************

export const Spinner = () => <div className='overlay'><div className='loader'></div></div>

export const StateMap = (props) => <div className={'state '+ {unknown:'grey',up:'green',down:'red'}[props.state] || 'orange'} />

// ***************************** Table ********************************

export const TableHead = (props) => <div className='thead'>{props.headers.map((row,index) => <div key={'th_'+index}>{row}</div> )}</div>

export const TableRow = (props) => <div>{props.cells.map((row,index) => <div key={'tr_'+index}>{row}</div> )}</div>

// ***************************** Content ********************************

// base,header,buttons,thead,trows,listItem
export const ContentList = (props) => {
 if (props.trows === null)
  return <Spinner />
 else {
  return <article className='table'>
    <h1>{props.header}</h1>
    {props.buttons}
    <div className='table'>
     <TableHead key={'content_thead'} headers={props.thead} />
     <div className='tbody'>
      {props.trows.map((row,index) => <TableRow key={'content_trow_'+props.base+'_'+index} cells={props.listItem(row)} /> )}
     </div>
    </div>
   </article>
 }
}

export const ContentData = (props) => <Fragment key='content_data_fragment'>{props.content}</Fragment>
