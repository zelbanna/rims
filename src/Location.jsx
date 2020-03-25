import React, { Fragment, Component } from 'react'
import { rest_call, rnd } from './infra/Functions.js';
import { Spinner, InfoCol2, ContentList, ContentData } from './infra/Generic.js';
import { AddButton, DeleteButton, InfoButton, ReloadButton, SaveButton } from './infra/Buttons.jsx';
import { TextInput } from './infra/Inputs.jsx';

// CONVERTED ENTIRELY

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
 deleteList = (api,id,msg) => (window.confirm(msg) && rest_call(api, {id:id}).then(result => result.deleted && this.setState({data:this.state.data.filter(row => (row.id !== id)),content:null})))

 listItem = (row) => [row.id,row.name,<Fragment key={'location_buttons_'+row.id}>
   <InfoButton key={'loc_btn_info_'+row.id} onClick={() => { this.changeContent(<Info key={'location_'+row.id} id={row.id} />) }} />
   <DeleteButton key={'loc_btn_delete_'+row.id} onClick={() => { this.deleteList('api/location/delete',row.id,'Really delete location') }} />
   </Fragment>
  ]

 render(){
  return <Fragment key='loc_fragment'>
   <ContentList key='loc_cl' header='Locations' thead={['ID','Name','']} trows={this.state.data} listItem={this.listItem}>
    <ReloadButton key='loc_btn_reload' onClick={() => this.componentDidMount() } />
    <AddButton key='loc_btn_add' onClick={() => this.changeContent(<Info key={'location_new_' + rnd()} id='new' />) } />
   </ContentList>
   <ContentData key='loc_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// *************** Info ***************
//
class Info extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, found:true};
 }

 onChange = (e) => {
  var data = {...this.state.data};
  data[e.target.name] = e.target[(e.target.type !== "checkbox") ? "value" : "checked"];
  this.setState({data:data});
 }

 changeContent = (elem) => this.setState({content:elem})

 updateInfo = (api) =>  rest_call(api,{op:'update', ...this.state.data}).then(result => this.setState(result))

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
     <InfoCol2 key='loc_content'>
     <TextInput key='name' id='name' value={this.state.data.name} onChange={this.onChange} />
     </InfoCol2>
     <SaveButton key='loc_btn_save' onClick={() => this.updateInfo('api/location/info')} />
    </article>
   );
  else
   return <Spinner />
 }
}
