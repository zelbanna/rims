import React, { PureComponent }  from 'react';
import styles from './navigation.module.css';

// ************************** Navigation ******************************
//
export const NavBar = (props) => <nav className={styles.main} id={props.id}><ul className={styles.list}>{props.children}</ul></nav>

export const NavButton = (props) => <li className={styles.item} style={props.style}><button className={styles.button} onClick={props.onClick}>{props.title}</button></li>

export const NavDropButton = (props) => <li className={styles.dropDownItem} style={props.style}><button className={styles.dropbutton} onClick={props.onClick}>{props.title}</button></li>

export class NavDropDown extends PureComponent{
 constructor(props){
  super(props)
  this.state = {height:0};
 }

 expandList = () => this.setState({height:3 * this.props.children.length});
 implodeList = () => this.setState({height:0});

 render(){
  return (
   <li className={styles.item} style={this.props.style} onMouseEnter={() => this.expandList()} onMouseLeave={() => this.implodeList()}>
    <button className={styles.button}>{this.props.title}</button>
    <ul className={styles.dropDownList} style={{maxHeight:`${this.state.height}rem`}}>{this.props.children}</ul>
   </li>
  );
 }
}

export const NavReload = (props) => <li className={styles.item} style={props.style}><button className={styles.button} onClick={props.onClick}><i className='fas fa-redo-alt' style={{fontSize:'2.1rem'}}/></button></li>

export const NavInfo = (props) => <li className={styles.info} style={props.style}><button className={styles.infobutton}>{props.title}</button></li>
