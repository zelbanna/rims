import React, { Component }  from 'react';
import styles from './header.module.css';

// ************************** Header and Menu ******************************
//
// Expanded size is dependand on button height to make sense
//
export const MenuButton = (props) => <li className={styles.menuItem}><button className={styles.menuButton} onClick={props.onClick}>{props.title}</button></li>

export const MenuSeparator = (props) => <li className={styles.menuSeparator}></li>

export const HeaderButton = (props) => <button className={styles.button} onClick={props.onClick} title={props.title}><i className={props.type} style={props.style} /></button>

export class Header extends Component {
 constructor(props){
  super(props)
  this.state = {height:0,zoom:(document.documentElement.style.getPropertyValue('font-size') !== '')};
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

 zoomTxt = () => {
  const size = window.getComputedStyle(document.documentElement).fontSize.replace('px','');
  if(this.state.zoom)
   document.documentElement.style.removeProperty('font-size');
  else
   document.documentElement.style.setProperty('font-size', `${size*1.20}px`);
  this.setState({zoom:!this.state.zoom})
 }
 render(){
  return (<header className={styles.header}>
   <h1 className={styles.title}>{this.props.title}</h1>
   <HeaderButton key={'zoom_'+ this.state.zoom} onClick={() => this.zoomTxt()} title='Zoom' type={(this.state.zoom) ? 'fas fa-search-minus' : 'fas fa-search-plus'} />
   <div className={styles.menu} onMouseLeave={() => this.implodeMenu()}>
    <HeaderButton key={'menu_' + this.state.height} onClick={() => this.toggleMenu()} title='Menu' type='fas fa-bars' style={{transform:(this.state.height === 0)?'rotate(0deg)':'rotate(90deg)'}} />
    <ul className={styles.menuList} style={{maxHeight:`${this.state.height}rem`}} >
     {this.props.children}
    </ul>
   </div>
   <HeaderButton key='logout' onClick={this.props.logOut} title='Log out' type='fas fa-sign-out-alt' />
  </header>);
 }
}
