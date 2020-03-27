import React from 'react';

export const MenuButton = (props) => <button className='menu' title={props.title} form={props.form} onClick={props.onClick} style={props.style}>{('icon' in props) ? <img src={props.icon} alt={props.title} draggable='false' /> : props.title}</button>

export const LinkButton = (props) => <button id={props.id} className='text' style={props.style} onClick={props.onClick} title={props.title}>{props.text}</button>

export const TextButton = (props) => <button id={props.id} className='text info' onClick={props.onClick} title={props.title}>{props.text}</button>

const button_awesome = (type,props) => <button id={props.id} className={'info fontawesome'} onClick={props.onClick} title={props.title}><i className={type} /></button>

// *********************** Button Types *************************

export const AddButton = (props) => button_awesome('fas fa-plus',props);
export const BackButton = (props) => button_awesome('fas fa-arrow-left',props);
export const CheckButton = (props) => button_awesome('fas fa-tasks',props);
export const ConfigureButton = (props) => button_awesome('fas fa-cogs',props);
export const ConnectionButton = (props) => button_awesome('fas fa-arrows-alt',props);
export const DeleteButton = (props) => button_awesome('fas fa-trash-alt',props);
export const DevicesButton = (props) => button_awesome('fas fa-network-wired',props);
export const DocButton = (props) => button_awesome('fas fa-clipboard-list',props);
export const EditButton = (props) => button_awesome('far fa-edit',props);
export const FixButton = (props) => button_awesome('fas fa-thumbtack',props);
export const InfoButton = (props) => button_awesome('fas fa-info',props);
export const ItemsButton = (props) => button_awesome('fas fa-list-ul',props);
export const LogButton = (props) => button_awesome('far fa-file-alt',props);
export const NetworkButton = (props) => button_awesome('fas fa-share-alt',props);
export const ReloadButton = (props) => button_awesome('fas fa-redo-alt',props);
export const SaveButton = (props) => button_awesome('fas fa-download',props);
export const SearchButton = (props) => button_awesome('fas fa-search',props);
export const ShutdownButton = (props) => button_awesome('fas fa-power-off',props);
export const StartButton = (props) => button_awesome('fas fa-play',props);
export const StopButton = (props) => button_awesome('fas fa-stop',props);
export const SyncButton = (props) => button_awesome('fas fa-exchange-alt',props);
export const TermButton = (props) => button_awesome('fas fa-terminal',props);
export const UiButton = (props) => button_awesome('fas fa-globe',props);
export const ViewButton = (props) => button_awesome('fas fa-search-plus',props);
