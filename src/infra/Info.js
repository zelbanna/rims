import React, { Fragment } from 'react';

// ***************************** Info ********************************

export const InfoCol2 = (props) => {
 const className = ('className' in props) ? 'info col2 ' + props.className : 'info col2';
 const griditems = props.griditems.map((row,index) => {
  let second = ''
  switch(row.tag) {
   case 'input':
    if (row.type !== 'radio')
     second = <input type={row.type} id={row.id} name={row.id} onChange={props.changeHandler} value={row.value} placeholder={row.placeholder} />
    else {
     second = <div>{
      row.options.map((opt,index) => { return (
       <Fragment key={'radio_'+index}>
        <label htmlFor={'radio_'+index}>{opt.text}</label>
        <input type='radio' key={'radio_input_'+index}  id={'radio_'+index} name={row.id} onChange={props.changeHandler} value={opt.value} checked={(row.value === opt.value) ? 'checked' : ''}/>
       </Fragment>
      ) })
     }</div>
    }
    break;
   case 'span':
    second = <span id={row.id}>{row.value}</span>
    break;
   case 'select':
    second = <select name={row.id} onChange={props.changeHandler} value={row.value}>{
     row.options.map((opt,index) => { return (<option key={row.id + '_'+index} value={opt.value}>{opt.text}</option>) })
    }</select>
    break;
   default:
    second = <div id={row.id}>{row.content}</div>
  }
  return <Fragment key={index}><label htmlFor={row.id}>{row.text}</label>{second}</Fragment>
 });

 return(
  <div className={className} style={props.style}>
   {griditems}
  </div>
 );
}
