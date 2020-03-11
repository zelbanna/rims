import React, { Fragment } from 'react';

// **************************** Generic ********************************

export const CookieContext = React.createContext({setCookie:()=>{},clearCookie:()=>{},cookie:null,main:null});
CookieContext.displayName = "RimsCookie";

export const Spinner = () => <div className='overlay'><div className='loader'></div></div>

export const StateMap = (props) =>  <div className={'state '+ {unknown:'grey',up:'green',down:'red',undefined:'orange',null:'orange'}[props.state] || 'orange'} />

// ***************************** Table ********************************

export const TableHead = (props) => <div className='thead'>{props.headers.map((row,index) => <div key={'th_'+index}>{row}</div> )}</div>

export const TableRow = (props) => <div>{props.cells.map((row,index) => <div key={'tr_'+index}>{row}</div> )}</div>

// ***************************** Content ********************************

// base,header,buttons,thead,trows,listItem
export const ContentList = (props) => content('table',props)

export const ContentReport = (props) => content('report',props)

const content = (type,props) => {
 if (props.trows === null)
  return <Spinner />
 else {
  return <article className={(props.hasOwnProperty('articleClass')) ? props.articleClass : type}>
    <h1>{props.header}</h1>
    {props.buttons}
    <span className='results'>{props.status}</span>
    <div className={(props.hasOwnProperty('tableClass')) ? props.tableClass : 'table'}>
     <TableHead key={'content_thead'} headers={props.thead} />
     <div className='tbody'>
      {props.trows.map((row,index) => <TableRow key={'content_trow_'+props.base+'_'+index} cells={props.listItem(row)} /> )}
     </div>
    </div>
   </article>
 }
}

export const ContentData = (props) => <Fragment key='content_data_fragment'>{props.content}</Fragment>

// ***************************** Info ********************************

export const InfoCol2 = (props) => {
 const griditems = props.griditems.map((row,index) => {
  let second = ''
  if (row.tag === 'input') {
   if (["text","url","email","password","date","time"].includes(row.type))
    second = <input type={row.type} id={row.id} name={row.id} onChange={props.changeHandler} value={(row.value !== null) ? row.value : ''} placeholder={row.placeholder} />
   else if (row.type === "checkbox")
    second = <input type="checkbox" id={row.id} name={row.id} onChange={props.changeHandler} defaultChecked={row.value} />
   else if (row.type === "radio"){
    second = <div>{
     row.options.map((opt,index) => <Fragment key={'radio_'+index}>
       <label htmlFor={'radio_'+index}>{opt.text}</label>
       <input type='radio' key={'radio_input_'+index}  id={'radio_'+index} name={row.id} onChange={props.changeHandler} value={opt.value} checked={(row.value === opt.value) ? 'checked' : ''}/>
      </Fragment> )
    }</div>
   } else {
    window.alert("Unknown input type:" + row.type);
    second = <div>UNKNOWN</div>
   }
  } else if (row.tag === 'select'){
   if (row.value === null)
    row.options.push({value:"NULL",text:"N/A"})
   second = <select name={row.id} onChange={props.changeHandler} value={(row.value !== null) ? row.value : "NULL"}>{
    row.options.map((opt,index) => <option key={row.id + '_'+index} value={opt.value}>{opt.text}</option>)
    }</select>
  } else if (row.tag === 'span') {
   second = <span id={row.id}>{row.value}</span>
  } else
   second = <div id={row.id}>{row.content}</div>
  return <Fragment key={index}><label htmlFor={row.id}>{row.text}</label>{second}</Fragment>
 });

 return <div className={('className' in props) ? 'info col2 ' + props.className : 'info col2'} style={props.style}>{griditems}</div>
}
