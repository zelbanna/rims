import React from 'react';
import { NavButton } from './Buttons.js';

// ************************** Navigation ******************************

export const NavBar = (props) => {
 let items = [];
 try {
  items = props.items.map((row) => {
   if (row.type === 'dropdown')
    return <NavDropDown key={'ndd_'+row.title} {...row} />
   else
    return <NavButton key={'nb_'+row.title} {...row} />
  });
 } catch(err) {
  items = [];
 }
 return <nav><ul>{items}</ul></nav>
}

const NavDropDown = (props) => {
 return (
  <li className={(props.className) ? 'dropdown ' + props.className : 'dropdown'}>
   <label>{props.title}</label>
   <ul className='dropdown-content'>
    {props.items.map((row) => { return <NavButton key={'nb_'+row.title} {...row} /> }) }
   </ul>
  </li>
 );
}
