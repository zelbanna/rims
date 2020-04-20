import React, { createContext, Component, Fragment } from 'react';
import { auth_call, rest_call } from './Functions.js';
import { CloseButton } from './Buttons.jsx';
import { TextInput, TextLine, TextAreaInput, PasswordInput } from './Inputs.jsx';
import { Header, MenuButton, MenuSeparator } from './Header.jsx';
import { NavBar } from './Navigation.jsx';
import tableStyles from './table.module.css';
import uiStyles from './ui.module.css';

// **************************** Generic ********************************

export const Title = (props) => <h1 className={uiStyles.title}>{props.text}</h1>

export const Flex = (props) => <div className={uiStyles.flex} style={props.style}>{props.children}</div>

export const Spinner = () => <div className={uiStyles.spinOverlay}><div className={uiStyles.loader}></div></div>

const Led = (props) => <div className={{on:uiStyles.stateGreen, off:uiStyles.stateRed, unknown:uiStyles.stateGrey, up:uiStyles.stateGreen, down:uiStyles.stateRed, undefined:uiStyles.stateOrange, null:uiStyles.stateOrange}[props.state] || uiStyles.stateOrange} title={props.state} />

export const StateLeds = (props) => <div>{(Array.isArray(props.state)) ? props.state.map((val,idx) => <Led key={'led_'+idx} state={val} />) : <Led key='led' state={props.state} />}</div>

// ***************************** Info ********************************
//
export const Article = (props) => <article className={uiStyles.article}><h1 className={uiStyles.title}>{props.header}</h1>{props.children}</article>

export const LineArticle = (props) => <article className={uiStyles.line}><h1 className={uiStyles.title}>{props.header}</h1>{props.children}</article>

export const CodeArticle = (props) => <article className={uiStyles.code}><h1 className={uiStyles.title}>{props.header}</h1>{props.children}</article>

export const InfoArticle = (props) => <article className={uiStyles.info}><h1 className={uiStyles.title}>{props.header}</h1>{props.children}</article>

export const InfoColumns = (props) => {
 let start = ['max-content','auto'];
 if (props.columns > 2)
  for (let i = 2; i < props.columns; i++)
   start.push((i % 2 === 0) ? 'max-content' :'auto');
 return <div className={uiStyles.columns} style={{gridTemplateColumns:start.join(' '),...props.style}}>{props.children}</div>
}
InfoColumns.defaultProps = {columns:2};

//*********************** List/Report ************************
//
// header,buttons,thead,trows,listItem(),result
//

export const Result = (props) => <span className={uiStyles.result}>{props.result}</span>

export const Row = (props) => <div className={tableStyles.trow}>{props.cells.map((row,idx) => <div key={'tr_'+idx} className={tableStyles.td}>{row}</div> )}</div>

export const ContentList = (props) => <section className={uiStyles.contentLeft}>{content(tableStyles.list,props)}</section>
export const ContentData = (props) => <section className={uiStyles.contentRight}>{props.children}</section>
export const ContentReport = (props) => content(tableStyles.report,props)

const content = (type,props) => {
 if (props.trows)
  return <article className={type}>
    <h1 className={tableStyles.title}>{props.header}</h1>
    {props.children}
    <Result key='con_result' result={props.result} />
    <div className={tableStyles.table}>
     <div className={tableStyles.thead}>{props.thead.map((row,idx) => <div key={'th_'+idx} className={tableStyles.th}>{row}</div> )}</div>
     <div className={tableStyles.tbody}>
      {props.trows.map((row,idx) => <Row key={'tr_'+idx} cells={props.listItem(row,idx)} /> )}
     </div>
    </div>
   </article>
 else
  return <Spinner />
}

// ********************* Portal Components *********************
//
export const RimsContext = createContext({setCookie:()=>{},clearCookie:()=>{},cookie:null,changeMain:()=>{},loadNavigtion:()=>{}})
RimsContext.displayName = 'RimsContext';

// *** Error boundary for fault management ***
//
class ErrorBoundary extends React.Component {
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
   return <div className={uiStyles.overlay} style={{top:0}}>
    <article className={uiStyles.error}>
     <CloseButton key='error_close' onClick={() => this.setState({hasError: false, error: undefined, info:[]})} />
     <h1 className={uiStyles.title}>UI Error</h1>
     <InfoColumns key='error_ic'>
      <TextLine id='type' text={this.state.error} />
      <TextAreaInput id='info' value={this.state.info.join('\n')} />
     </InfoColumns>
    </article>
   </div>
  else
   return this.props.children;
 }
}

// *** Theme context provider - for writing DOM color values ***
//
class Theme extends Component {

 componentDidMount(){
  this.loadTheme(this.props.theme);
 }

 componentDidUpdate(prevProps){
  if (prevProps.theme !== this.props.theme)
   this.loadTheme(this.props.theme);
 }

 loadTheme = (theme) => {
  rest_call('api/portal/theme_info',{theme:theme}).then(result => {
   if(result && result.status === 'OK')
    for (var [param,val] of Object.entries(result.data))
     document.documentElement.style.setProperty(param, val);
  })
 }

 render(){
  return <Fragment />
 }
}

// ***  Main portal application ***
//
export class Portal extends Component {
 constructor(props){
  super(props)
  this.state = { menu:[], navigation:<NavBar key='portal_navigation_empty' />}
 }

 componentDidMount() {
  this.props.providerMounting({changeMain:this.changeContent,loadNavigation:this.loadNavigation});
  rest_call('api/portal/menu',{id:this.context.cookie.id}).then(result => {
   if(result && result.status === 'OK'){
    const data = result.data
    this.setState(data);
    data.start && this.changeContent(data.menu[data.start]);
    document.title = data.title;
   }})
 }

 loadNavigation = (navbar) => this.setState({navigation:navbar})

 changeContent = (panel) => {
  // Native RIMS or something else?
  if (panel.hasOwnProperty('module')) {
   try {
    import("../"+panel.module+".jsx").then(lib => {
     var Elem = lib[panel.function];
     this.setState({navigation:<NavBar key='portal_navigation_empty' />,content:<Elem key={panel.module + '_' + panel.function} {...panel.args} />,height:0});
    })
   } catch(err) {
    console.error("Mapper error: "+panel);
    alert(err);
   }
  } else
   this.setState({navigation:<NavBar key='portal_navigation_empty' />,content:panel})
 }

 logOut = () => {
  auth_call({destroy:this.context.cookie.token,id:this.context.cookie.id})
  this.context.clearCookie()
 }

 render() {
  let buttons = []
  for (let [key, panel] of Object.entries(this.state.menu)){
   if (panel.type === 'module')
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => this.changeContent(panel)} />)
   else if (panel.type === 'tab')
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => window.open(panel.tab,'_blank')} />)
   else if (panel.type === 'frame')
    buttons.push(<MenuButton key={'hb_'+key} title={key} onClick={() => this.changeContent(<iframe className={uiStyles.frame} title={key} src={panel.frame} />)} />)
  }
  buttons.push(<MenuSeparator key='hs_1' />,
   <MenuButton key='hb_user_info' title='User' onClick={() => this.changeContent({module:'user',function:'User', args:{id:this.context.cookie.id}})} />,
   <MenuButton key='hb_system' title='System' onClick={() => this.changeContent({module:'system',function:'Main'})} />)

  return (
   <React.Fragment key='portal'>
    <Theme key='portal_theme' theme={this.context.cookie.theme} />
    <Header key='portal_header' title={this.state.title} logOut={() => this.logOut()}>
     {buttons}
    </Header>
    {this.state.navigation}
    <ErrorBoundary key='portal_error'>
     <main className={uiStyles.main}>{this.state.content}</main>
    </ErrorBoundary>
  </React.Fragment>
  )
 }
}
Portal.contextType = RimsContext;

// *** Login application ***
//
export class Login extends Component {
 constructor(props){
  super(props)
  this.state = {message:'',username:'username',password:'password'}
 }

 componentDidMount() {
  rest_call('front').then(result => {
   this.setState(result)
   document.title = result.title
  })
 }

 onChange = (e) => this.setState({[e.target.name]:e.target.value});

 handleSubmit = (event) => {
  event.preventDefault();
  auth_call({username:this.state.username,password:this.state.password})
   .then((result) => {
    if (result.status === 'OK')
     this.props.setCookie({node:result.node,token:result.token,id:result.id,theme:result.theme,expires:result.expires});
    else {
     document.getElementById("password").value = "";
     this.setState(prevState => ({ ...prevState,   password : '' }))
    }
   })
 }

 render() {
  return (
   <div className={uiStyles.loginOverlay}>
    <article className={uiStyles.login}>
     <h1 className={uiStyles.title}>{this.state.message}</h1>
     <InfoColumns style={{float:'left'}}>
      <TextInput key='username' id='username' onChange={this.onChange} />
      <PasswordInput key='password' id='password' onChange={this.onChange} />
     </InfoColumns>
     <button className={uiStyles.button} onClick={this.handleSubmit} title='Login'><i className='fas fa-sign-in-alt' /></button>
    </article>
   </div>
  )
 }
}
