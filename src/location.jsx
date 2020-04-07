import React, { Fragment, Component } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoColumns, ContentList, ContentData } from './infra/UI.jsx';
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
  rest_call('api/location/list',).then(result => this.setState(result))
 }

 changeContent = (elem) => this.setState({content:elem})
 deleteList = (id) => (window.confirm('Really delete location?') && rest_call('api/location/delete', {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 listItem = (row) => [row.id,row.name,<Fragment key={'location_buttons_'+row.id}>
   <ConfigureButton key={'loc_btn_info_'+row.id} onClick={() => this.changeContent(<Info key={'location_'+row.id} id={row.id} />)} title='Edit location' />
   <DeleteButton key={'loc_btn_delete_'+row.id} onClick={() => this.deleteList(row.id)} title='Delete location' />
   </Fragment>
  ]

 render(){
  return <Fragment key='loc_fragment'>
   <ContentList key='loc_cl' header='Locations' thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='loc_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='loc_btn_add' onClick={() => this.changeContent(<Info key={'location_new_' + rnd()} id='new' />)} title='Add location' />
   </ContentList>
   <ContentData key='loc_cd'>{this.state.content}</ContentData>
  </Fragment>
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

 updateInfo = () => rest_call('api/location/info',{op:'update', ...this.state.data}).then(result => this.setState(result))

 componentDidMount(){
  rest_call('api/location/info',{id:this.props.id}).then(result => this.setState(result))
 }

 render() {
  if (!this.state.found)
   return <article>Location id: {this.props.id} removed</article>
  else if (this.state.data)
   return (
    <article className='info'>
     <h1>Location</h1>
     <InfoColumns key='loc_content'>
     <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
     </InfoColumns>
     <SaveButton key='loc_btn_save' onClick={() => this.updateInfo()} title='Save' />
    </article>
   );
  else
   return <Spinner />
 }
}
