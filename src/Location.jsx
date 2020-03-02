import React, { Fragment } from 'react'
import { rest_call, rest_base } from './infra/Functions.js';
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
  this.thead = ['ID','Name','']
  this.header = 'Locations'
  this.buttons = [
   <InfoButton key='reload' type='reload' onClick={() => { this.componentDidMount() }} />,
   <InfoButton key='add' type='add' onClick={() => { this.changeList(<Info key={'location_new_' + Math.floor(Math.random() * 10)} id='new' />) }} title='Add new location' />
  ]
 }

 componentDidMount(){
  rest_call(rest_base + 'api/location/list',)
   .then((result) => this.setState(result) )
 }

 listItem = (row) => [row.id,row.name,<Fragment key={'location_buttons_'+row.id}>
   <InfoButton key={'loc_info_'+row.id} type='info'  onClick={() => { this.changeList(<Info key={'location_'+row.id} id={row.id} />) }} />
   <InfoButton key={'loc_delete_'+row.id} type='trash' onClick={() => { this.deleteList('api/location/delete',row.id,'Really delete location') }} />
   </Fragment>
  ]

}

// *************** Info ***************
//
class Info extends InfoBase {

 componentDidMount(){
  rest_call(rest_base + 'api/location/info',{id:this.props.id})
   .then((result) =>  this.setState(result) )
 }

 infoItems = () => [{tag:'input', type:'text', id:'name', text:'Name', value:this.state.data.name}]

 render() {
  if (this.state.found === false)
   return <article>Location id: {this.props.id} removed</article>
  else if (this.state.data === null)
   return <Spinner />
  else {
   return (
    <article className='info'>
     <h1>Location</h1>
     <form>
      <InfoCol2 key='location_content' griditems={this.infoItems()} changeHandler={this.handleChange} />
     </form>
     <InfoButton key='location_save' type='save' onClick={() => this.updateInfo('api/location/info')} />
    </article>
   );
  }
 }
}


