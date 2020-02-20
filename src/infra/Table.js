import React from 'react';

// ***************************** Table ********************************

export const TableHead = (props) => {
 return <div className='thead'>{props.headers.map((row,index) => { return <div key={'th_'+index}>{row}</div> })}</div>
}

export const TableRow = (props) => {
 return <div>{props.cells.map((row,index) => { return <div key={'tr_'+index}>{row}</div> })}</div>
}
