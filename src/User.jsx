import React, { Component, Fragment } from 'react';
import { rest_call, rest_base, read_cookie, rnd } from './infra/Functions.js';
import { Spinner } from './infra/Generic.js';
import { ListBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.js';
import { InfoCol2 }   from './infra/Info.js';

// CONVERTED ENTIRELY

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props)
  this.thead = ['ID','Alias','Name','']
  this.header = 'Users'
  this.base = 'user'
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => {this.componentDidMount()}} />,
   <InfoButton key='add'    type='add'    onClick={() => {this.changeList(<Info key={'user_new_'+rnd()} id='new' />)}} />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/master/user_list')
   .then((result) => { this.setState(result); })
 }

 listItem = (row) => [row.id,row.alias,row.name,<Fragment key={'user_buttons_'+row.id}>
   <InfoButton key={'user_info_'+row.id} type='info' onClick={() => { this.changeList(<Info key={'user_info_'+row.id} id={row.id} />)}} />
   <InfoButton key={'user_del_'+row.id} type='trash' onClick={() => { this.deleteList('api/master/user_delete',row.id,'Really delete user?')}} />
  </Fragment>]

}

// ************** Info **************
//
export class Info extends InfoBase {
 constructor(props) {
  super(props)
  const cookie = read_cookie('rims');
  this.state.cookie_id = cookie.id;
  this.state.themes = null;
 }

 componentDidMount(){
  rest_call(rest_base + 'api/system/theme_list')
   .then((result) => {
    this.setState({themes:result});
   })
  rest_call(rest_base + 'api/master/user_info',{id:this.props.id})
   .then((result) => { this.setState(result); })
 }

 infoItems = () => [
    {tag:'input', type:'text', id:'alias', text:'Alias', value:this.state.data.alias},
    {tag:'input', type:'password', id:'password', text:'Password',placeholder:'******'},
    {tag:'input', type:'text', id:'email', text:'e-mail', value:this.state.data.email},
    {tag:'input', type:'text', id:'name', text:'Full name', value:this.state.data.name},
    {tag:'select', id:'theme', text:'Theme', value:this.state.data.theme, options:this.state.themes.map((row) => { return ({value:row, text:row})})}
   ]

 render() {
  if (this.state.found === false)
   return <article>User with id: {this.props.id} removed</article>
  else if ((this.state.data === null) || (this.state.themes === null))
   return <Spinner />
  else {
   const className = (this.props.hasOwnProperty('className')) ? `info ${this.props.className}` : 'info';
   return (
    <article className={className}>
     <h1>User Info ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='user_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='user_save' type='save' onClick={() => this.updateInfo('api/master/user_info') } />
    </article>
   );
  }
 }
}

// ************** User **************
//
export class User extends Component {
 render() {
  return <Fragment key='user_user'><Info className='centered' id={this.props.id} /></Fragment>
 }
}
