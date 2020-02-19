import React from 'react';
import { NavButton } from './Buttons.js';

// ************************** Navigation ******************************

export const NavBar = (props) => {
 let items = [];
 try {
  items = props.items.map((row,index) => {
   return (
    <li key={'navitem_'+index} className={row.className}>
     <NavButton key={row.title} {...row} />
    </li>
   );
  });
 } catch(err) {
  items = [];
 }
 return (
   <nav><ul>{items}</ul></nav>
 );
}
