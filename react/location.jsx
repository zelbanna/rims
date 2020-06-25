import React, { Component } from 'react'
import { post_call } from './infra/Functions.js';
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

 deleteList = (id) => (window.confirm('Really delete location?') && post_call('api/location/delete', {id:id}).then(result => {
  if (result.deleted){
   this.setState({data:this.state.data.filter(row => (row.id !== id))});
   this.changeContent(null);
  }}))

 listItem = (row) => [row.id,row.name,<>
   <ConfigureButton key='conf' onClick={() => this.changeContent(<Info key='location' id={row.id} />)} title='Edit location' />
   <DeleteButton key='del' onClick={() => this.deleteList(row.id)} title='Delete location' />
   </>]

 render(){
  return <>
   <ContentList key='cl' header='Locations' thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='reload' onClick={() => this.componentDidMount() } />
    <AddButton key='add' onClick={() => this.changeContent(<Info key='location' id='new' />)} title='Add location' />
   </ContentList>
   <ContentData key='cda' mountUpdate={(fun) => this.changeContent = fun} />
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

 updateInfo = () => post_call('api/location/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidUpdate(prevProps,prevState){
  if (prevProps !== this.props){
   this.componentDidMount()
  }
 }

 componentDidMount(){
  post_call('api/location/info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <InfoArticle key='ia_loc'>Location id: {this.props.id} removed</InfoArticle>
  else if (this.state.data)
   return <InfoArticle key='ia_loc' header='Location'>
     <InfoColumns key='ic'>
     <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='save' onClick={() => this.updateInfo()} title='Save' />
    </InfoArticle>
  else
   return <Spinner />
 }
}
