import React, { Component, Fragment } from 'react';
import { rest_call } from './Functions.js';
import { CloseButton } from './Buttons.jsx';

// **************************** Generic ********************************

export class ErrorBoundary extends React.Component {
 constructor(props) {
  super(props);
  this.state = { hasError: false, error: undefined, info:[] };
 }

 static getDerivedStateFromError(error) {
  return {hasError: true};
 }

 componentDidCatch(error, errorInfo) {
  this.setState({error:error.toString(),info:errorInfo.componentStack.split('\n')})
 }

 render() {
  if (this.state.hasError)
   return <div className='overlay' style={{top:0}}>
    <article className='error'>
     <CloseButton key='error_close' onClick={() => this.setState({hasError: false, error: undefined, info:[]})} />
     <h1>UI Error</h1>
     <InfoColumns key='error_ic'>
      <label htmlFor='type' className='info'>Type</label><span id='type' className='info'>{this.state.error}</span>
      <label htmlFor='info' className='info'>Info:</label><div id='info'>{this.state.info.map((row,idx) => <p key={'error_line'+idx}>{row}</p>)}</div>
     </InfoColumns>
    </article>
   </div>
  else
   return this.props.children;
 }
}

export const Spinner = () => <div className='overlay'><div className='loader'></div></div>

export const StateMap = (props) =>  <div className={'state '+ {on:'green',off:'red',unknown:'grey',up:'green',down:'red',undefined:'orange',null:'orange'}[props.state] || 'orange'} title={props.state} />

export const SearchField = (props) => <input type='text' className='searchfield' onChange={props.searchHandler} value={props.value} placeholder={props.placeholder} />

export const Result = (props) => <span className='results'>{props.result}</span>

export const InfoColumns = (props) => {
 let start = ['max-content','auto'];
 if (props.columns > 2)
  for (let i = 2; i < props.columns; i++)
   start.push((i % 2 === 0) ? 'max-content' :'auto');
 return <div className={('className' in props) ? `info ${props.className}` : 'info'} style={{gridTemplateColumns:start.join(' ')}}>{props.children}</div>
}

InfoColumns.defaultProps = {columns:2};

export const InfoArticle = (props) => <article className='info'>{props.children}</article>

export class Theme extends Component {

 componentDidMount(){
  this.loadTheme(this.props.theme);
 }

 componentDidUpdate(prevProps){
  if (prevProps.theme !== this.props.theme)
   this.loadTheme(this.props.theme);
 }

 loadTheme = (theme) => {
  rest_call('api/system/theme_info',{theme:theme}).then(result => {
   if(result.status === 'OK')
    for (var [param,val] of Object.entries(result.data))
     document.documentElement.style.setProperty(param, val);
  })
 }

 render(){
  return <Fragment key='fragment_theme'>{this.props.children}</Fragment>
 }
}

// ***************************** Table ********************************

export const TableHead = (props) => <div className='thead'>{props.headers.map((row,index) => <div key={'th_'+index}>{row}</div> )}</div>

export const TableRow = (props) => <div className='trow'>{props.cells.map((row,index) => <div key={'tr_'+index}>{row}</div> )}</div>

// ***************************** Content ********************************
//
// base,header,buttons,thead,trows,listItem
//
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
      {props.trows.map((row,idx) => <TableRow key={'tr_'+idx} cells={props.listItem(row,idx)} /> )}
     </div>
    </div>
   </article>
 else
  return <Spinner />
}
