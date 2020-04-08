import React, { Component, Fragment } from 'react'
import { rest_call } from './infra/Functions.js';
import { Spinner, InfoColumns, RimsContext, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { TextLine } from './infra/Inputs.jsx';
import { NavBar, NavInfo } from './infra/Navigation.js';
import { DocButton, DeleteButton, InfoButton, ReloadButton, SearchButton } from './infra/Buttons.jsx';

// ************* Main ************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {content:undefined,ip:undefined}
 }

 changeContent = (elem) => this.setState({content:elem});

 componentDidMount(){
  rest_call('api/system/external_ip').then(result => {
   const ip = (result && result.status === 'OK') ? result.ip : '0.0.0.0'
   this.context.loadNavigation(<NavBar key='multimedia_navbar'><NavInfo key='mm_nav_ip' title={ip} /></NavBar>)
  })
  this.reloadList()
 }

 reloadList = () => rest_call('api/multimedia/list').then(result => this.setState(result));

 deleteList = (obj) => (window.confirm('Delete file '+obj.file+'?') && rest_call('api/multimedia/delete',obj).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (!(row.path === obj.path && row.file === obj.file))),content:null})));

 listItem = (row,idx) => [row.file,<Fragment key={'mm_buttons_'+idx}>
   <InfoButton key={'mm_btn_info_'+idx} onClick={() => this.changeContent(<Title key={'multimedia_title_'+idx} path={row.path} file={row.file} />)} title='Title info' />
   <SearchButton key={'mm_btn_lookup_'+idx} onClick={() => this.changeContent(<Lookup key={'multimedia_lookup_'+idx} path={row.path} file={row.file} />)} title='Lookup info' />
   <DocButton key={'mm_btn_subs_'+idx} onClick={() => this.changeContent(<Subtitles key={'multimedia_subs_'+idx} path={row.path} file={row.file} />)} title='Subtitles' />
   <DeleteButton key={'mm_btn_delete_'+idx} onClick={() => this.deleteList(row)} title='Delete file' />
  </Fragment>]

 render(){
  if(this.state.data)
   return <Fragment key='mm_fragment'>
    <ContentList key='mm_cl' header='Media files' thead={['File','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
     <ReloadButton key='mm_btn_reload' onClick={() => this.reloadList()} />
     <DeleteButton key='mm_btn_cleanup' onClick={() => (window.confirm('Really clean up files?') && this.changeContent(<Cleanup key='multimedia_cleanup' />))} title='Cleanup multimedia directory' />
    </ContentList>
    <ContentData key='mm_cd'>{this.state.content}</ContentData>
   </Fragment>
  else
   return <Spinner />
 }
}
Main.contextType = RimsContext;

// ************* Cleanup ************
//
class Cleanup extends Component {

 componentDidMount(){
  rest_call('api/multimedia/cleanup').then(result => this.setState(result));
 }

 render(){
   return (this.state) ? <ContentReport key='mm_clean_cr' header='delete' thead={['Type','Path','Item','Status','Info']} trows={this.state.data} listItem={(row) => [row.type,row.path,row.item,row.status,row.info]} /> : <Spinner />
 }
}

// ************* Title ************
//
class Title extends Component {
 render(){
  return <div>Title TODO</div>
 }
}

// ************* Lookup ************
//
class Lookup extends Component {
 render(){
  return <div>Lookup TODO</div>
 }
}

// ************* Subtitles ************
//
class Subtitles extends Component {

 componentDidMount(){
  rest_call('api/multimedia/check_srt',{path:this.props.path,file:this.props.file}).then(result => this.setState(result));
 }

 render(){
  if (this.state) {
   return <article className='info'>
    <h1>{this.state.data.file}</h1>
    <InfoColumns key='mm_sub_ic'>
     <TextLine key='mm_sub_name' id='name' text={this.state.data.name} />
     <TextLine key='mm_sub_code' id='code' text={this.state.data.code} />
     <TextLine key='mm_sub_file' id='file' text={this.state.data.file} />
    </InfoColumns>
   </article>
  } else
   return <Spinner />
 }
}
