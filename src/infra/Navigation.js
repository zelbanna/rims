import React from 'react';
import { NavButton } from './Buttons.jsx';

// ************************** Navigation ******************************

export const NavBar = (props) => {
 return (props.items) ?  <nav><ul>{props.items.map((row) => (row.type === 'dropdown') ? <NavDropDown key={'nd_' + row.title} {...row} /> : <NavButton key={'nb_' + row.title} {...row} /> )}</ul></nav> : <nav><ul></ul></nav>
}

const NavDropDown = (props) => {
 return (
  <li className={(props.className) ? 'dropdown ' + props.className : 'dropdown'}>
   <label>{props.title}</label>
   <ul>{props.items.map((row) => <NavButton key={'ndb_'+props.title+'_'+row.title} {...row} /> )}</ul>
  </li>
 );
}
