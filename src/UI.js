import React from 'react';

// ************************* UI functions ****************************

// ***************************** Menu ********************************
export const MenuButton = (props) => {
 const className = ('className' in props) ? 'menu ' + props.className : 'menu';
 const view = ('icon' in props) ? <img src={props.icon} alt={props.title} /> : props.title
 return (
  <button className={className} title={props.title} form={props.form} onClick={props.onClick} style={props.style}>
   {view}
  </button>
 )
}

// ***************************** Info ********************************

export const DivInfoCol2 = (props) => {
 const className = ('className' in props) ? 'info col2 ' + props.className : 'info col2';
 const griditems = props.griditems.map((row,index) => {
  let second = ''
  switch(row.element) {
   case 'input':
    second = <input type={row.type} id={row.id} name={row.id} onChange={props.changeHandler} value={row.value} placeholder={row.placeholder} />
    break;
   case 'span':
    second = <span id={row.id}>{row.content}</span>
    break;
   case 'select':
    second = <select name={row.id} onChange={props.changeHandler}>{
     row.options.map((opt,index) => {
     if (row.selected)
      return (<option key={row.id + '_'+index} selected='selected' value={opt.value}>{opt.text}</option>)
     else
      return (<option key={row.id + '_'+index} value={opt.value}>{opt.text}</option>)
     })
    }</select>
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

export const InfoButton = (props) => {
 let className = ('className' in props) ? 'info ' + props.className : 'info';
 if ('type' in props) {
  className = className + ' type-' + props.type;
  return(<button className={className} onClick={props.onClick} />);
 } else {
  alert("implement text button");
  return (<button>TBD</button>);
 }
}

// ************************** Navigation ******************************

export const NavBar = (props) => {
 let items = [];
 try {
  items = props.items.map((row,index) => {
   return (
    <li key={'navitem_'+index} className={row.className}>
     <NavButton key={row.title} {...row} />
    </li>
   );
  });
 } catch(err) {
  items = [];
 }
 return (
   <nav><ul>{items}</ul></nav>
 );
}

export const NavButton = (props) => {
 const className = ('className' in props) ? 'nav ' + props.className : 'nav';
 return (
  <button className={className} onClick={props.onClick}>
   {props.title}
  </button>
 )
}

// ***************************** Table ********************************

export const TableHead = (props) => {
 const thlist = props.headers.map((row,index) => {
  return (
   <div key={'th_'+index}>{row}</div>
  )
 });
 return (
  <div className='thead'>
   {thlist}
  </div>
 );
}

export const TableRow = (props) => {
 const cells = props.cells.map((row,index) => { return (<div key={'tr_'+index}>{row}</div>); });
 return (<div>{cells}</div>);
}


// **************************** Generic ********************************
export const Spinner = () => {
 return (
  <div key='spinner' className='overlay'>
   <div className='loader'></div>
  </div>
 )
}


