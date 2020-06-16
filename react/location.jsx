import React, { Component } from 'react'
import { post_call, rnd } from './infra/Functions.js';
import { Spinner, InfoArticle, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
import { AddButton, DeleteButton, ConfigureButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';
import { TextInput } from './infra/Inputs.jsx';

// ************** List **************
//
export class List extends Component {
constructor(props){
  super(props)
  this.state = {}
 }

 componentDidMount(){
  post_call('api/location/list',).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete location?') && post_call('api/location/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 listItem = (row) => [row.id,row.name,<>
   <ConfigureButton key='conf' onClick={() => this.changeContent(<Info key={'location_'+row.id} id={row.id} />)} title='Edit location' />
   <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete location' />
   </>]

 render(){
  return <>
   <ContentList key='loc_cl' header='Locations' thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<Info key={'location_new_' + rnd()} id='new' />)} title='Add location' />
   </ContentList>
   <ContentData key='loc_cd'>{this.state.content}</ContentData>
  </>
 }
}

// *************** Info ***************
//
export class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 onChange = (e) => this.setState({data:{...this.state.data, [e.target.name]:e.target.value}});

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = () => post_call('api/location/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  post_call('api/location/info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <InfoArticle key='loc_removed'>Location id: {this.props.id} removed</InfoArticle>
  else if (this.state.data)
   return <InfoArticle key='loc_article' header='Location'>
     <InfoColumns key='loc_content'>
     <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='loc_btn_save' onClick={() => this.updateInfo()} title='Save' />
    </InfoArticle>
  else
   return <Spinner />
 }
}
