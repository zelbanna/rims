import React, { Component, Fragment } from 'react'
import { rest_call, rest_base, rnd } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { ListBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.js';
import { InfoCol2 }   from './infra/Info.js';
import { NavBar }   from './infra/Navigation.js';

// ************** List **************
//
export class List extends ListBase {
 constructor(props){
  super(props);
  this.header='Servers'
  this.thead=['Node','Service','Type','']
  this.buttons=[
   <InfoButton key='srv_reload' type='reload' onClick={() => this.componentDidMount() } />,
   <InfoButton key='srv_add'    type='add' title='Add server'  onClick={() => this.changeList(<Info key={'srv_add_' + rnd()} id='new' type={this.props.type} />)  } />
  ]
 }

 componentDidMount(){
  const args = (this.props.type) ? {type:this.props.type} : {}
  rest_call(rest_base + 'api/master/server_list',args)
   .then((result) => this.setState(result) )
 }

 listItem = (row) => {
  var buttons = [
   <InfoButton key='srv_info'   type='info'   onClick={() => this.changeList(<Info key={'server_info_'+row.id} id={row.id} />) } />,
   <InfoButton key='srv_delete' type='trash'  onClick={() => this.deleteList('api/master/server_delete',row.id,'Are you really sure?')  } />,
  ]
  if (row.hasOwnProperty('ui') && (row.ui.length > 0))
   buttons.push(<InfoButton key='srv_www' type='ui' onClick={() =>  window.open(row.ui,'_blank') } />)
  return [row.node,row.service,row.type,<Fragment key='srv_buttons'>{buttons}</Fragment>]
 }
}

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/master/server_info',{id:this.props.id})
   .then((result) => {
    if (result.data.node === null)
     result.data.node = result.nodes[0]
    if (result.data.type_id === null)
     result.data.type_id = result.services[0].id
    this.setState(result)
   })
 }

 infoItems = () => [
  {tag:'span', id:'server', text:'ID', value:this.state.data.id},
  {tag:'select', id:'node', text:'Node', value:this.state.data.node, options:this.state.nodes.map(row => ({value:row, text:row}))},
  {tag:'select', id:'type_id', text:'Service', value:this.state.data.type_id, options:this.state.services.map(row => ({value:row.id, text:`${row.service} (${row.type})`}))},
  {tag:'input', type:'text', id:'ui', text:'UI', value:this.state.data.ui}
 ]

 render() {
  if (this.state.found === false)
   return <article>Server with id: {this.props.id} removed</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   let buttons = [<InfoButton key='srv_save' type='save' onClick={() => this.updateInfo('api/master/server_info')} />]
   if (this.state.data.id !== 'new'){
    buttons.push(<InfoButton key='srv_sync' type='sync' onClick={() => {      this.changeInfo(<Operation key={'srv_op_sync'} id={this.props.id} operation='sync' />) }} />)
    buttons.push(<InfoButton key='srv_restart' type='reload' onClick={() => { this.changeInfo(<Operation key={'srv_op_rst'}  id={this.props.id} operation='restart' />) }} />)
    buttons.push(<InfoButton key='srv_status'  type='items'  onClick={() => { this.changeInfo(<Operation key={'srv_op_stat'} id={this.props.id} operation='status' />) }} />)
   }
   return (
    <Fragment key='srv_info_fragment'>
    <article className='info'>
     <h1>Server Info ({this.state.data.id})</h1>
     <InfoCol2 key='srv_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     {buttons}
    </article>
    <NavBar key='srv_navbar' items={null} />
    {this.state.content}
    </Fragment>
   );
  }
 }
}

// *************** Operation ***************
//
class Operation extends Component {
 componentDidMount(){
  rest_call(rest_base + 'api/master/server_' + this.props.operation,{id:this.props.id})
   .then((result) => {
    this.setState(result)
   })
 }

 render(){
  if (this.state === null)
   return <Spinner />
  else
   return <article className='code'><pre>{JSON.stringify(this.state,null,2)}</pre></article>
 }
}
