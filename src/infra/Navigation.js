import React from 'react';
import { NavButton } from './Buttons.js';

// ************************** Navigation ******************************

export const NavBar = (props) => {
 let items = [];
 try {
  items = props.items.map((row,index) => {
   if (row.type === 'dropdown')
    return <NavDropDown key={'ndd_'+index} {...row} />
   else
    return <NavItem key={'ni_'+index} {...row} />
   });
 } catch(err) {
  items = [];
 }
 return <nav><NavList key='nl' items={items} /></nav>
}

const NavDropDown = (props) => {
 return (
  <li className={(props.className) ? 'dropdown ' + props.className : 'dropdown'}>
   <label>{props.title}</label>
   <ul className='dropdown-content'>
    {props.items.map((row,index) => { return <NavItem key={'ndd_'+index} {...row} /> }) }
   </ul>
  </li>
 );
}

const NavList = (props) => {
 return <ul>{props.items}</ul>
}

const NavItem = (props) => {
 return <li className={props.className}><NavButton key={props.title} {...props} /></li>
}
