import React, { Component }  from 'react';
import styles from './header.module.css';

// ************************** Header and Menu ******************************
//
// Expanded size is dependand on button height to make sense
//
export const MenuButton = (props) => <li className={styles.menuItem}><button className={styles.menuButton} onClick={props.onClick}>{props.title}</button></li>

export const MenuSeparator = (props) => <li className={styles.menuSeparator}></li>

export class Header extends Component {
 constructor(props){
  super(props)
  this.state = {height:0};
 }

 implodeMenu = () => {
  if (this.state.height > 0)
   this.setState({height:0})
 }

 toggleMenu = () => {
  if (this.state.height === 0)
   this.setState({height:(2.8 * this.props.children.length)})
  else
   this.setState({height:0})
 }

 render(){
  return (<header className={styles.header}>
   <h1 className={styles.title}>{this.props.title}</h1>
   <div className={styles.menu} onMouseLeave={() => this.implodeMenu()}>
    <button className={styles.button} onClick={() => this.toggleMenu()}><i className='fas fa-bars' style={{transform:(this.state.height === 0)?'rotate(0deg)':'rotate(90deg)'}}/></button>
    <ul className={styles.menuList} style={{maxHeight:`${this.state.height}rem`}} >
     {this.props.children}
    </ul>
   </div>
   <button className={styles.button} onClick={this.props.logOut} title='Log out'><i className='fas fa-sign-out-alt' /></button>
  </header>);
 }
}
