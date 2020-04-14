import React from 'react';

// ************************** Link ****************************
export const HrefButton = (props) => <button id={props.id} className='text' style={props.style} onClick={props.onClick} title={props.title}>{props.text}</button>
export const HeaderButton = (props) => <button id={props.id} className='text' style={(props.highlight) ? {color:'var(--high-color)'} : {}} onClick={props.onClick} title={props.title}>{props.text}</button>

// *********************** Info Types *************************

const info_template = (type,props) => <button id={props.id} className='info fa' onClick={props.onClick} title={props.title}><i className={type} /></button>
export const TextButton = (props) => <button id={props.id} className='info text' onClick={props.onClick} title={props.title}>{props.text}</button>
export const AddButton = (props) => info_template('fas fa-plus',props);
export const BackButton = (props) => info_template('fas fa-arrow-left',props);
export const CheckButton = (props) => info_template('fas fa-tasks',props);
export const CloseButton = (props) => <button id={props.id} className='info fa right' onClick={props.onClick} title={props.title}><i className='fas fa-times-circle' /></button>
export const ConfigureButton = (props) => info_template('fas fa-cog',props);
export const ConnectionButton = (props) => info_template('fas fa-arrows-alt',props);
export const DeleteButton = (props) => info_template('fas fa-trash-alt',props);
export const DevicesButton = (props) => info_template('fas fa-network-wired',props);
export const DocButton = (props) => info_template('fas fa-clipboard-list',props);
export const EditButton = (props) => info_template('fas fa-edit',props);
export const FixButton = (props) => info_template('fas fa-thumbtack',props);
export const ForwardButton = (props) => info_template('fas fa-arrow-right',props);
export const GoButton = (props) => info_template('fas fa-share-square',props);
export const InfoButton = (props) => info_template('fas fa-info',props);
export const ItemsButton = (props) => info_template('fas fa-list-ul',props);
export const LinkButton = (props) => info_template('fas fa-link',props);
export const LogButton = (props) => info_template('fas fa-file-alt',props);
export const NetworkButton = (props) => info_template('fas fa-share-alt',props);
export const PauseButton = (props) => info_template('fas fa-pause',props);
export const ReloadButton = (props) => info_template('fas fa-redo-alt',props);
export const RevertButton = (props) => info_template('fas fa-history',props);
export const SaveButton = (props) => info_template('fas fa-download',props);
export const SearchButton = (props) => info_template('fas fa-search',props);
export const ShutdownButton = (props) => info_template('fas fa-power-off',props);
export const SnapshotButton = (props) => info_template('fas fa-camera',props);
export const StartButton = (props) => <button id={props.id} className='info fa green' onClick={props.onClick} title={props.title}><i className='fas fa-play' /></button>;
export const StopButton = (props) => <button id={props.id} className='info fa red' onClick={props.onClick} title={props.title}><i className='fas fa-stop' /></button>;
export const SyncButton = (props) => info_template('fas fa-exchange-alt',props);
export const TermButton = (props) => <button id={props.id} className='info fa' onClick={props.onClick} title={props.title}><i className='fas fa-terminal' /></button>;
export const UiButton = (props) => info_template('fas fa-globe-americas',props);
export const UnlinkButton = (props) => info_template('fas fa-unlink',props);
export const ViewButton = (props) => info_template('fas fa-search-plus',props);
