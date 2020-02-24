import React, { Component, Fragment } from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
import { Spinner }    from './infra/Generic.js';
import { InfoButton } from './infra/Buttons.js';
import { ContentMain } from './infra/Content.js';
import { InfoCol2 }   from './infra/Info.js';

/*

def status(aWeb):
def restart(aWeb):
def delete(aWeb):
def help(aWeb):
*/

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
   <InfoButton key='server_info'   type='info'   onClick={() => this.contentRight(<Info key={'server_info_'+row.id} id={row.id} />) } />,
   <InfoButton key='server_delete' type='trash'  onClick={() => this.deleteItem(row.id,'Are you really sure?')  } />,
   <InfoButton key='server_sync'   type='sync'   onClick={() => { this.contentRight(<Sync key={'server_sync_'+row.id} id={row.id} />) }} />,
   <InfoButton key='server_restart' type='reload' onClick={() => { this.contentRight(<Restart key={'server_restart_'+row.id} id={row.id} />) }} />
  ]
/*
   aWeb.wr(aWeb.button('items',DIV='div_content_right',URL='server_status?id=%s'%(srv['id']), SPIN='true', TITLE='Server status'))
*/
  return [row.node,row.service,row.type,<Fragment key='server_buttons'>{buttons}</Fragment>]
 }

 render(){
  return <ContentMain key='server_content' base='node' header='Nodes' thead={['Node','Service','Type','']}
    trows={this.state.data} content={this.state.contentright} listItem={this.listItem} buttons={<Fragment key='server_header_buttons'>
     <InfoButton key='reload' type='reload' onClick={() => this.componentDidMount() } />
     <InfoButton key='add'  type='add' title='Add server'  onClick={() => this.contentRight(<Info key={'server_new_' + Math.floor(Math.random() * 10)} id='new' type={this.props.type} />)  } />
    </Fragment>} />
 }
}

// *************** Info ***************
//
class Info extends Component {
  constructor(props) {
  super(props)
  this.state = {data:null,found:true}
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
    <article className='info'>
     <h1>Server Info ({this.state.data.id})</h1>
     <form>
      <InfoCol2 key='server_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='server_save' type='save' onClick={this.updateInfo} />
    </article>
   );
  }
 }
}

// *************** Sync ***************
//
class Sync extends Component {

 componentDidMount(){
  rest_call(rest_base + 'api/master/server_sync',{id:this.props.id})
   .then((result) => {
    this.setState(result)
   })
 }

 render(){
  if (this.state === null)
   return <Spinner />
  else
   return <article className='code'>{JSON.stringify(this.state)}</article>
 }
}


/*
#
#
def status(aWeb):
 from json import dumps
 res = aWeb.rest_call("master/server_status",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s<PRE></ARTICLE>"%dumps(res,indent=2,sort_keys=True))

#
#
def restart(aWeb):
 from json import dumps
 res = aWeb.rest_call("master/server_restart",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s<PRE></ARTICLE>"%dumps(res,indent=2,sort_keys=True))
 */

// *************** Reload ***************
//
class Restart extends Component {

 componentDidMount(){
  rest_call(rest_base + 'api/master/server_restart',{id:this.props.id})
   .then((result) => { this.setState(result) })
 }

 render(){
  if (this.state === null)
   return <Spinner />
  else
   return <article className='code'>{JSON.stringify(this.state)}</article>
 }
}
