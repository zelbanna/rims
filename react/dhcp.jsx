import React, { Component, Fragment } from 'react'
import { post_call } from './infra/Functions.js';
import { ContentList, ContentData } from './infra/UI.jsx';
import { InfoButton } from './infra/Buttons.jsx';

// ************** Server **************
//
export class Servers extends Component {
 constructor(props){
  super(props)
  this.state = {content:null}
 }

 changeServer = (svr) => this.setState({content:<List key={'dhcp_list_'+svr} server_id={svr} />})

 componentDidMount(){
  post_call('api/master/server_list',{type:'DHCP'}).then(result => this.setState(result))
 }

 listItem = (row) => [row.node,row.service,<InfoButton key={'dhcp_btn_info_'+row.id} onClick={() => this.changeServer(row.id)} title='DHCP server allocated addresses' />]

 render(){
  return <Fragment key='dhcp_fragment'>
   <ContentList key='dhcp_cl' header='Servers' thead={['Node','Service','Type','']} trows={this.state.data} listItem={this.listItem} />
   <ContentData key='dhcp_cd'>{this.state.content}</ContentData>
  </Fragment>
 }
}

// *************** List ***************
//
class List extends Component {
 constructor(props){
  super(props);
  this.state = {}
 }

 render() {
  return <div>TBD</div>
 }
}
