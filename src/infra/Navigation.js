import React, { Component }  from 'react';

// ************************** Navigation ******************************
//
// with children
//
const NavButton = (props) =>  <li className={props.className}><button className={('className' in props) ? `nav ${props.className}` : 'nav'} onClick={props.onClick}>{('icon' in props) ? <img src={props.icon} alt={props.title} draggable='false' /> : props.title}</button></li>

export const NavBar = (props) => {
 return <nav><ul>{props.children && props.children.map(row => (row.type === 'dropdown') ? <NavDropDown key={'nd_' + row.title} {...row}>{row.items}</NavDropDown> : <NavButton key={'nb_' + row.title} {...row} /> )}</ul></nav>
}

class NavDropDown extends Component{
 constructor(props){
  super(props)
  this.state = {height:0};
 }

 changeSize = (size) => this.setState({height:size});

 render(){
  return (
   <li className={(this.props.className) ? 'dropdown ' + this.props.className : 'dropdown'} onMouseEnter={() => this.changeSize(`calc(var(--nav-height) * ${this.props.children.length})`)} onMouseLeave={() => this.changeSize(0)}>
    <label>{this.props.title}</label>
    <ul style={{maxHeight:this.state.height}}>{this.props.children.map((row) => <NavButton key={'ndb_'+this.props.title+'_'+row.title} {...row} /> )}</ul>
   </li>
  );
 }
}
