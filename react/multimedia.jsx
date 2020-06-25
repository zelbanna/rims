import React, { Component } from 'react'
import { post_call, rnd } from './infra/Functions.js';
import { RimsContext, Spinner, CodeArticle, InfoArticle, InfoColumns, ContentList, ContentData, ContentReport } from './infra/UI.jsx';
import { CheckboxInput, TextLine,TextInput } from './infra/Inputs.jsx';
import { NavBar, NavInfo } from './infra/Navigation.jsx';
import { DocButton, DeleteButton, InfoButton, ReloadButton, SearchButton, StartButton, SyncButton } from './infra/Buttons.jsx';

// ************* Main ************
//
export class Main extends Component {
 constructor(props){
  super(props)
  this.state = {ip:undefined}
 }

 componentDidMount(){
  post_call('api/system/external_ip').then(result => {
   Object.assign(this.state,{ip:(result && result.status === 'OK') ? result.ip : '0.0.0.0'})
   this.compileNavItems()
  })
  this.reloadList()
 }

 componentDidUpdate(prevProps){
  if(prevProps !== this.props)
   this.compileNavItems()
 }

 compileNavItems = () => this.context.loadNavigation(<NavBar key='multimedia_navbar'><NavInfo key='mm_nav_ip' title={this.state.ip} /></NavBar>)

 reloadList = () => post_call('api/multimedia/list').then(result => this.setState(result));

 deleteList = (obj) => (window.confirm('Delete file '+obj.file+'?') && post_call('api/multimedia/delete',obj).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (!(row.path === obj.path && row.file === obj.file)))});
   this.changeContent(null);
  }}))

 listItem = (row,idx) => [row.file,<>
   <InfoButton key='info' onClick={() => this.changeContent(<Title key={'multimedia_title_'+idx} path={row.path} file={row.file} />)} title='Title info' />
   <SearchButton key='lookup' onClick={() => this.changeContent(<Lookup key={'multimedia_lookup_'+idx} path={row.path} file={row.file} />)} title='Lookup info' />
   <DocButton key='subs' onClick={() => this.changeContent(<Subtitles key={'multimedia_subs_'+idx} path={row.path} file={row.file} />)} title='Subtitles' />
   <DeleteButton key='del' onClick={() => this.deleteList(row)} title='Delete file' />
  </>]

 render(){
  if(this.state.data)
   return <>
    <ContentList key='cl' header='Media files' thead={['File','']} trows={this.state.data} listItem={this.listItem} result={this.state.result}>
     <ReloadButton key='reload' onClick={() => this.reloadList()} />
     <DeleteButton key='cleanup' onClick={() => (window.confirm('Really clean up files?') && this.changeContent(<Cleanup key={'multimedia_cleanup_'+rnd()} />))} title='Cleanup multimedia directory' />
    </ContentList>
    <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
   </>
  else
   return <Spinner />
 }
}
Main.contextType = RimsContext;

// ************* Title ************
//
class Title extends Component {
 constructor(props){
  super(props)
  this.state = {thread:true,wait:null}
 }

 componentDidMount(){
  post_call('api/multimedia/check_title',{path:this.props.path,file:this.props.file}).then(result => this.setState(result));
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 threadChange = (e) => this.setState({[e.target.name]:e.target.checked});

 updateInfo = () => post_call('api/multimedia/check_titlt',{op:'update', ...this.state.data}).then(result => this.setState(result))

 transferFile = () => {
  if (window.confirm('Transfer file to repository?')){
   if(this.state.thread)
    post_call('api/system/worker',{module:'multimedia',function:'transfer',output:true,args:{path:this.props.path,file:this.props.file}}).then(result => this.setState({op:'transfer',result:result}));
   else {
    this.setState({wait:<Spinner />})
    post_call('api/multimedia/transfer',{path:this.props.path,file:this.props.file}).then(result => this.setState({op:'transfer',result:result,wait:null}));
   }
  }
 }

 processFile = () => {
  if (window.confirm('Process file?')){
   if(this.state.thread)
    post_call('api/system/worker',{module:'multimedia',function:'process',output:true,args:{path:this.props.path,file:this.props.file,...this.state.data}}).then(result => this.setState({op:'process',result:result}));
   else {
    this.setState({wait:<Spinner />})
    post_call('api/multimedia/process',{path:this.props.path,file:this.props.file,...this.state.data}).then(result => this.setState({op:'process',result:result,wait:null}));
   }
  }
 }

 render(){
  if (this.state.op) {
   if(this.state.thread || this.state.op === 'transfer')
    return <InfoArticle key='mm_trans_article' header={(this.state.thread) ? 'Task activation' : 'Transfer'}>
     <TextLine key='mm_trans_res' id='result' text={JSON.stringify(this.state.result)} />
    </InfoArticle>
   else {
    if(this.state.result.status === 'NOT_OK')
     return <CodeArticle key='mm_error_code' header='Process Error'>{JSON.stringify(this.state.result.info,null,2)}</CodeArticle>
    else {
     const data = this.state.result.data;
     return <InfoArticle key='mm_proc_article' header='Process success'>
      Elapsed time for processing file: {this.state.result.seconds} seconds
      <InfoColumns key='mm_proc_ic'>
       <TextLine key='mm_proc_prefix' id='prefix' text={data.prefix} />
       <TextLine key='mm_proc_suffix' id='suffix' text={data.suffix} />
       <TextLine key='mm_proc_dest' id='dest' label='Destination' text={JSON.stringify(data.dest)} />
       <TextLine key='mm_proc_rename' id='rename' text={JSON.stringify(data.rename)} />
       <TextLine key='mm_proc_aac' id='aac' label='Add AAC' text={JSON.stringify(data.aac_probe)} />
       <TextLine key='mm_proc_chg_aac' id='chg_aac' label='Param AAC' text={data.changes.aac} />
       <TextLine key='mm_proc_chg_aud' id='chg_aud' label='Param Audio' text={data.changes.audio} />
       <TextLine key='mm_proc_chg_sub' id='chg_sub' label='Param Subtitles' text={data.changes.subtitle} />
       <TextLine key='mm_proc_chg_srt' id='chg_srt' label='Param SRT files' text={data.changes.srt} />
      </InfoColumns>
     </InfoArticle>
    }
   }
  } else if(this.state.data){
   const data = this.state.data
   return <InfoArticle key='mm_tit_article' header='Title'>
    <InfoColumns key='mm_tit_ic'>
     <TextLine key='mm_tit_type' id='type' text={data.type} />
     <TextLine key='mm_tit_title' id='title' text={data.title} />
     <TextLine key='mm_tit_path' id='path' text={data.path} />
     <TextInput key='mm_tit_name' id='name' value={data.name} onChange={this.onChange} />
     {data.epside && <TextInput key='mm_tit_eposide' id='episode' value={data.episode} onChange={this.onChange} />}
     <TextInput key='mm_tit_info' id='info' value={data.info} onChange={this.onChange} />
     <CheckboxInput key='mm_tit_thread' id='thread' label='Thread' value={this.state.thread} onChange={this.threadChange} title='Thread or direct execution' />
    </InfoColumns>
    <StartButton key='mm_tit_btn_proc' onClick={() => this.processFile()} title='Process file' />
    <SyncButton key='mm_tit_btn_trans' onClick={() => this.transferFile()} title='Transfer file' />
    {this.state.wait}
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* Lookup ************
//
class Lookup extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/multimedia/check_content',{path:this.props.path,file:this.props.file}).then(result => this.setState(result));
 }

 render(){
  if (this.state.data) {
   const data = this.state.data
   return <InfoArticle key='mm_lu_article' header='Lookup'>
    <InfoColumns key='mm_lu_ic'>
     <TextLine key='mm_lu_file' id='file' label='File' text={this.props.file} />
     <TextLine key='mm_lu_status' id='status' label='Result' text={this.state.status} />
     <TextLine key='mm_lu_error' id='error' label='Error' text={this.state.info} />
     <TextLine key='mm_lu_v_def' id='video_default' label='Video default' text={JSON.stringify(!data.video.set_default)} title='Video stream has default language' />
     <TextLine key='mm_lu_v_lang' id='video_lang' label='Video language' text={data.video.language} title='Language set in video stream information' />
     <TextLine key='mm_lu_a_add' id='audio_add' label='Audio keep' text={data.audio.add.join()} />
     <TextLine key='mm_lu_a_rem' id='audio_rem' label='Audio remove' text={data.audio.remove.join()} />
     <TextLine key='mm_lu_a_aac' id='audio_aac' label='Add AAC' text={JSON.stringify(data.audio.add_aac)} />
     <TextLine key='mm_lu_s_add' id='sub_add' label='Subtitle keep' text={data.subtitle.add.join()} />
     <TextLine key='mm_lu_s_rem' id='sub_rem' label='Subtitle remove' text={data.subtitle.remove.join()} />
     <TextLine key='mm_lu_a_lang' id='sub_lang' label='Subtitle languages' text={data.subtitle.languages.join()} />
    </InfoColumns>
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* Subtitles ************
//
class Subtitles extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/multimedia/check_srt',{path:this.props.path,file:this.props.file}).then(result => this.setState(result));
 }

 render(){
  if (this.state.data) {
   return <InfoArticle key='mm_sub_art' header='Extra subtitles'>
    <InfoColumns key='mm_sub_ic'>
     <TextLine key='mm_sub_path' id='path' text={this.props.path} />
     <TextLine key='mm_sub_item' id='item' text={this.props.file} />
     <TextLine key='mm_sub_name' id='name' text={this.state.data.name} />
     <TextLine key='mm_sub_code' id='code' text={this.state.data.code} />
     <TextLine key='mm_sub_file' id='file' text={this.state.data.file} />
    </InfoColumns>
   </InfoArticle>
  } else
   return <Spinner />
 }
}

// ************* Cleanup ************
//
class Cleanup extends Component {
 constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/multimedia/cleanup').then(result => this.setState(result));
 }

 render(){
   return (this.state.data) ? <ContentReport key='mm_clean_cr' header='delete' thead={['Type','Path','Item','Status','Info']} trows={this.state.data} listItem={(row) => [row.type,row.path,row.item,row.status,row.info]} /> : <Spinner />
 }
}
