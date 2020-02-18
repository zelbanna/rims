import React from 'react';

// ************************* UI functions ****************************

// Send an update handler for mainUpdate
export const MenuButton = (props) => {
 const className = ('className' in props) ? 'menu ' + props.className : 'menu';
 const view = ('icon' in props) ? <img src={props.icon} alt={props.title} /> : props.title
 return (
  <button className={className} title={props.title} form={props.form} onClick={props.onClick} style={props.style}>
   {view}
  </button>
 )
}

export const DivInfoCol2 = (props) => {
 const className = ('className' in props) ? 'info col2 ' + props.className : 'info col2';
 const griditems = props.griditems.map((row,index) => {
  let second = ''
  switch(row.element) {
   case 'input':
    second = <input type={row.type} id={row.id} name={row.id} onChange={props.changeHandler} />
    break;
   case 'span':
    second = <span id={row.id}>{row.content}</span>
    break;
   default:
    second = <div id={row.id}>{row.content}</div>
  }
  return <React.Fragment key={index}><label htmlFor={row.id}>{row.text}</label>{second}</React.Fragment>
 });

 return(
  <div className={className} style={props.style}>
   {griditems}
  </div>
 );
}

export const Spinner = () => {
 return (
  <div key='spinner' className='overlay'>
   <div className='loader'></div>
  </div>
 )
}


