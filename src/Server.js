import React, { Component, Fragment } from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';
import { NavBar }   from './infra/Navigation.js';

// ************** List **************
//
export class List extends Component {
 constructor(props){
  super(props);
  this.state = {data:null, contentright:null }
 }

 componentDidMount(){
  const args = (this.props.type) ? {type:this.props.type} : {}
  rest_call(rest_base + 'api/master/server_list',args)
   .then((result) => this.setState(result) )
 }

 contentRight = (elem) => {
  this.setState({contentright:elem});
 }

 deleteItem = (id,msg)  => {
  if(window.confirm(msg)){
   rest_call(rest_base + 'api/master/server_delete',{id:id})
    .then((result) => {
     if(result.deleted)
      this.setState({data:this.state.data.filter((row,index,arr) => row.id !== id)})
    })
  }
 }

 listItem = (row) => {
  var buttons = [
   <InfoButton key='srv_info'   type='info'   onClick={() => this.contentRight(<Info key={'server_info_'+row.id} id={row.id} />) } />,
   <InfoButton key='srv_delete' type='trash'  onClick={() => this.deleteItem(row.id,'Are you really sure?')  } />,
  ]
  if (('ui' in row) && (row.ui.length > 0))
   buttons.push(<InfoButton key='srv_www' type='ui' onClick={() =>  window.open(row.ui,'_blank') } />)

  return [row.node,row.service,row.type,<Fragment key='srv_buttons'>{buttons}</Fragment>]
 }

 render(){
  return <ContentMain key='srv_content' base='node' header='Nodes' thead={['Node','Service','Type','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='srv_header_buttons'>
     <InfoButton key='srv_reload' type='reload' onClick={() => this.componentDidMount() } />
     <InfoButton key='srv_add'    type='add' title='Add server'  onClick={() => this.contentRight(<Info key={'srv_add_' + Math.floor(Math.random() * 10)} id='new' type={this.props.type} />)  } />
    </Fragment>} />
 }
}

// *************** Info ***************
//
class Info extends Component {
  constructor(props) {
  super(props)
  this.state = {data:null,found:true,contentbelow:null}
 }

 handleChange = (e) => {
  var data = {...this.state.data}
  data[e.target.name] = e.target.value
  this.setState({data:data})
 }

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

 updateInfo = () => {
  rest_call(rest_base + 'api/master/server_info',{op:'update', ...this.state.data})
   .then((result) => {
    this.setState(result)
   })
 }

 contentBelow = (elem) => {
  this.setState({contentbelow:elem});
 }

 infoItems = () => {
  return [
    {tag:'span', id:'server', text:'ID', value:this.state.data.id},
    {tag:'select', id:'node', text:'Node', value:this.state.data.node, options:this.state.nodes.map(row => {return {value:row, text:row}})},
    {tag:'select', id:'type_id', text:'Service', value:this.state.data.type_id, options:this.state.services.map(row => {return {value:row.id, text:`${row.service} (${row.type})`} })},
    {tag:'input', type:'text', id:'ui', text:'UI', value:this.state.data.ui}
   ]
 }

 render() {
  if (this.state.found === false)
   return <article>Server with id: {this.props.id} removed</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <Fragment key='srv_info_fragment'>
    <article className='info'>
     <h1>Server Info ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='srv_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='srv_save' type='save' onClick={this.updateInfo} />
     <InfoButton key='srv_sync' type='sync' onClick={() => {      this.contentBelow(<Operation key={'srv_op_sync'} id={this.props.id} operation='sync' />) }} />
     <InfoButton key='srv_restart' type='reload' onClick={() => { this.contentBelow(<Operation key={'srv_op_rst'}  id={this.props.id} operation='restart' />) }} />
     <InfoButton key='srv_status'  type='items'  onClick={() => { this.contentBelow(<Operation key={'srv_op_stat'} id={this.props.id} operation='status' />) }} />
    </article>
    <NavBar key='srv_navbar' items={null} />
    {this.state.contentbelow}
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
