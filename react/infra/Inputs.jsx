import React, { Fragment, PureComponent } from 'react';
import { StateLeds } from './UI.jsx';
import styles from './input.module.css';

const auto_label = (props) => (props.label) ? props.label : props.id;

const input_template = (type,props) => <><label htmlFor={props.id} title={props.title} className={styles.label}>{auto_label(props)}:</label><input className={styles.input} type={type} id={props.id} name={props.id} onChange={props.onChange} value={(props.value !== null) ? props.value : ''} placeholder={props.placeholder} title={props.extra} size={props.size} /></>
const line_template = (content,props) => <><label htmlFor={props.id} title={props.title} className={styles.label}>{auto_label(props)}:</label>{content}</>

//
// Display Only
//
export const TextLine = (props) =>  line_template(<span id={props.id} style={props.style} title={props.extra} className={styles.span}>{props.text}</span>,props);
export const StateLine = (props) => line_template(StateLeds(props),props);

//
// Inputs
//
export const TextInput = (props) => input_template('text',props);
export const UrlInput = (props) => input_template('url',props);
export const EmailInput = (props) => input_template('email',props);
export const PasswordInput = (props) => input_template('password',props);
export const DateInput = (props) => input_template('date',props);
export const TimeInput = (props) => input_template('time',props);

export const TextAreaInput = (props) => <><label htmlFor={props.id} className={styles.label} title={props.title}>{auto_label(props)}:</label><textarea id={props.id} name={props.id} onChange={props.onChange} className={styles.textarea} value={props.value} /></>

export const CheckboxInput = (props) => <><label htmlFor={props.id} className={styles.label} title={props.title}>{auto_label(props)}:</label><input type='checkbox' id={props.id} name={props.id} onChange={props.onChange} defaultChecked={props.value} placeholder={props.placeholder} title={props.extra} className={styles.checkbox} /></>

export const RadioInput = (props) => <><label htmlFor={props.id} className={styles.label} title={props.title}>{auto_label(props)}:</label><div>{
  props.options.map((opt,idx) => <Fragment key={idx}>
   <label htmlFor={'ri_'+props.id+'_'+idx}>{opt.text}</label>
   <input type='radio' id={'ri_'+props.id+'_'+idx} name={props.id} onChange={props.onChange} value={opt.value} checked={(props.value.toString() === opt.value.toString()) ? 'checked' : ''}/>
  </Fragment>)
 }</div></>

export const SelectInput = (props) => <>
  <label htmlFor={props.id} title={props.title} className={styles.label}>{auto_label(props)}:</label>
  <select name={props.id} onChange={props.onChange} value={(props.value !== null && props.value !== undefined) ? props.value : 'NULL'} className={styles.input}>
  {(props.value === null || props.value === undefined) && props.children.find(child => child.props.value === 'NULL') === undefined && <option value='NULL'>{'<Empty>'}</option>}
  {props.children}
  </select>
 </>

//
// SearchInput
// - property: function 'searchFire' which takes one argument that is the current value of the input
// - text: text use in the searchfield. A means for external input
//
export class SearchInput extends PureComponent{
 constructor(props){
  super(props)
  this.state = {text:(this.props.text) ? this.props.text : ''}
  this.timer = null;
 }

 componentDidUpdate (prevProps, prevState) {
  if(prevState.text !== this.state.text) {
   this.handleInput();
  }
  if(prevProps.text !== this.props.text){
   this.setState({text:this.props.text})
  }
 }

 componentWillUnmount(){
  clearTimeout(this.timer);
 }

 handleInput = () => {
  // Clears running timer and starts a new one each time the user types
  clearTimeout(this.timer);
  this.timer = setTimeout(() => this.props.searchFire(this.state.text), 400);
 }

 render(){
  return <input type='text' className={styles.searchfield} onChange={(e) => this.setState({text:e.target.value})} value={this.state.text} placeholder={this.props.placeholder} autoFocus />
 }
}

