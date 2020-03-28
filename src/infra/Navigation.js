import React, { Component }  from 'react';

// ************************** Navigation ******************************
//
// with children
//

export const NavBar = (props) => <nav id={props.id}><ul>{props.children}</ul></nav>

export const NavButton = (props) => <li style={props.style}><button className='nav' onClick={props.onClick}>{props.title}</button></li>

export class NavDropDown extends Component{
 constructor(props){
  super(props)
  this.state = {height:0};
 }

 changeSize = (size) => this.setState({height:size});

 render(){
  return (
   <li className='dropdown' style={this.props.style} onMouseEnter={() => this.changeSize(`calc(var(--nav-height) * ${this.props.children.length})`)} onMouseLeave={() => this.changeSize(0)}>
    <label>{this.props.title}</label>
    <ul style={{maxHeight:this.state.height}}>{this.props.children}</ul>
   </li>
  );
 }
}

export const NavReload = (props) => <li style={props.style}><button className='nav fontawesome' onClick={props.onClick}><i className='fas fa-redo-alt' /></button></li>

export const NavInfo = (props) => <li className='navinfo' style={props.style}><button className='nav navinfo' onClick={props.onClick}>{props.title}</button></li>
