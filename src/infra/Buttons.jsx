import React from 'react';

export const MenuButton = (props) => {
 const className = ('className' in props) ? `menu ${props.className}` : 'menu';
 const view = ('icon' in props) ? <img src={props.icon} alt={props.title} draggable='false' /> : props.title
 return <button className={className} title={props.title} form={props.form} onClick={props.onClick} style={props.style}>{view}</button>
}

const button_template = (type,props) => <button id={props.id} className={('className' in props) ? `info type-${type} ${props.className}` : `info type-${type}`} onClick={props.onClick} title={props.title}/>

export const TextButton = (props) => <button id={props.id} className={('className' in props) ? `text ${props.className}` : 'text'} onClick={props.onClick} title={props.title}>{props.text}</button>

export const  AddButton = (props) => button_template('add',props);
export const  ConnectionButton = (props) => button_template('connections',props);
export const  DeleteButton = (props) => button_template('delete',props);
export const  DevicesButton = (props) => button_template('devices',props);
export const  DocButton = (props) => button_template('document',props);
export const  EditButton = (props) => button_template('edit',props);
export const  FixButton = (props) => button_template('fix',props);
export const  ViewButton = (props) => button_template('forward',props);
export const  InfoButton = (props) => button_template('info',props);
export const  ItemsButton = (props) => button_template('items',props);
export const  LogButton = (props) => button_template('logs',props);
export const  NetworkButton = (props) => button_template('network',props);
export const  ReloadButton = (props) => button_template('reload',props);
export const  SaveButton = (props) => button_template('save',props);
export const  SearchButton = (props) => button_template('search',props);
export const  ShutdownButton = (props) => button_template('off',props);
export const  StartButton = (props) => button_template('start',props);
export const  StopButton = (props) => button_template('stop',props);
export const  SyncButton = (props) => button_template('sync',props);
export const  TermButton = (props) => button_template('term',props);
export const  UiButton = (props) => button_template('ui',props);
