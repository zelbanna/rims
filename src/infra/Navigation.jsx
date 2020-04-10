import React, { Component }  from 'react';

// ************************** Navigation ******************************
//
// with children
//

export const NavBar = (props) => <nav id={props.id}><ul className='nav'>{props.children}</ul></nav>

export const NavButton = (props) => <li className='nav' style={props.style}><button className='nav' onClick={props.onClick}>{props.title}</button></li>

export const NavDropButton = (props) => <li className='dropdown' style={props.style}><button className='nav' onClick={props.onClick}>{props.title}</button></li>

export class NavDropDown extends Component{
 constructor(props){
  super(props)
  this.state = {height:0};
 }

 changeSize = (size) => this.setState({height:size});

 render(){
  return (
   <li className='nav' style={this.props.style} onMouseEnter={() => this.changeSize(`${3 * this.props.children.length}rem`)} onMouseLeave={() => this.changeSize(0)}>
    <label className='nav'>{this.props.title}</label>
    <ul className='dropdown' style={{maxHeight:this.state.height}}>{this.props.children}</ul>
   </li>
  );
 }
}

export const NavReload = (props) => <li style={props.style}><button className='nav nav-fa' onClick={props.onClick}><i className='nav-fa fas fa-redo-alt' /></button></li>

export const NavInfo = (props) => <li className='navinfo right' style={props.style}><button className='nav navinfo' onClick={props.onClick}>{props.title}</button></li>
