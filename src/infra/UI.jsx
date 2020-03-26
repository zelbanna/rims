import React, { createContext } from 'react';

export const Header = (props) => <header>{props.children}</header>

// **************************** Generic ********************************

export const RimsContext = createContext({setCookie:()=>{},clearCookie:()=>{},cookie:null,changeMain:()=>{},loadNavigtion:()=>{}})
RimsContext.displayName = "RimsContext";

export const Spinner = () => <div className='overlay'><div className='loader'></div></div>

export const StateMap = (props) =>  <div className={'state '+ {unknown:'grey',up:'green',down:'red',undefined:'orange',null:'orange'}[props.state] || 'orange'} />

export const SearchField = (props) => <input type='text' className='searchfield' onChange={props.searchHandler} value={props.value} placeholder={props.placeholder} />

export const Result = (props) => <span className='results'>{props.result}</span>

export const InfoColumns = (props) => <div className={'info col' + props.columns + (('className' in props) ? ' ' + props.className : '')}>{props.children}</div>
InfoColumns.defaultProps = {columns:2};

export const InfoArticle = (props) => <article className='info'>{props.children}</article>

// ***************************** Table ********************************

export const TableHead = (props) => <div className='thead'>{props.headers.map((row,index) => <div key={'th_'+index}>{row}</div> )}</div>

export const TableRow = (props) => <div>{props.cells.map((row,index) => <div key={'tr_'+index}>{row}</div> )}</div>

// ***************************** Content ********************************

// base,header,buttons,thead,trows,listItem
export const ContentList = (props) => <section id='div_content_left' className='content-left'>{content('table',props)}</section>
export const ContentData = (props) => <section id='div_content_right' className='content-right'>{props.children}</section>
export const ContentReport = (props) => content('report',props)

const content = (type,props) => {
 if (props.trows)
  return <article className={(props.hasOwnProperty('articleClass')) ? props.articleClass : type}>
    <h1>{props.header}</h1>
    {props.children}
    <Result key='con_result' result={props.result} />
    <div className={(props.hasOwnProperty('tableClass')) ? props.tableClass : 'table'}>
     <TableHead key={'con_thead'} headers={props.thead} />
     <div className='tbody'>
      {props.trows.map((row,index) => <TableRow key={'tr_'+index} cells={props.listItem(row)} /> )}
     </div>
    </div>
   </article>
 else
  return <Spinner />
}
