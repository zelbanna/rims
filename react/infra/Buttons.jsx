import React, { memo } from 'react';
import styles from './button.module.css';

// ************************** Link ****************************

export const HrefButton = memo((props) => <button id={props.id} className={styles.href} style={props.style} onClick={props.onClick} title={props.title}>{props.text}</button>);
export const HeaderButton = (props) => <button id={props.id} className={styles.href} style={(props.highlight) ? {color:'var(--high-color)'} : {}} onClick={props.onClick} title={props.title}>{props.text}</button>

// *********************** Info Types *************************

const info_template = (type,props) => <button id={props.id} className={styles.info} onClick={props.onClick} title={props.title}><i className={type} /></button>
export const TextButton = (props) => <button id={props.id} className={styles.text} onClick={props.onClick} title={props.title}>{props.text}</button>
export const AddButton = (props) => info_template('fas fa-plus',props);
export const BackButton = (props) => info_template('fas fa-arrow-left',props);
export const CheckButton = (props) => info_template('fas fa-tasks',props);
export const CloseButton = (props) => <button id={props.id} className={styles.info} style={{float:'right'}} onClick={props.onClick} title={props.title}><i className='fas fa-times-circle' /></button>
export const ConfigureButton = (props) => info_template('fas fa-cog',props);
export const DeleteButton = memo((props) => info_template('fas fa-trash-alt',props));
export const DevicesButton = (props) => info_template('fas fa-network-wired',props);
export const DocButton = (props) => info_template('fas fa-clipboard-list',props);
export const EditButton = (props) => info_template('fas fa-edit',props);
export const FixButton = (props) => info_template('fas fa-thumbtack',props);
export const ForwardButton = (props) => info_template('fas fa-arrow-right',props);
export const GoButton = (props) => info_template('fas fa-share-square',props);
export const InfoButton = memo((props) => info_template('fas fa-info',props));
export const ItemsButton = (props) => info_template('fas fa-list-ul',props);
export const LinkButton = (props) => info_template('fas fa-link',props);
export const LogButton = (props) => info_template('fas fa-file-alt',props);
export const NetworkButton = (props) => info_template('fas fa-share-alt',props);
export const PauseButton = (props) => info_template('fas fa-pause',props);
export const ReloadButton = (props) => info_template('fas fa-redo-alt',props);
export const RemoveButton = (props) => info_template('fas fa-minus',props);
export const ReserveButton = (props) => info_template('fas fa-clipboard-check',props);
export const RevertButton = (props) => info_template('fas fa-history',props);
export const SaveButton = (props) => info_template('fas fa-download',props);
export const SearchButton = (props) => info_template('fas fa-search',props);
export const ServeButton = (props) => info_template('fas fa-hand-holding',props);
export const ShutdownButton = (props) => info_template('fas fa-power-off',props);
export const SnapshotButton = (props) => info_template('fas fa-camera',props);
export const StartButton = (props) => <button id={props.id} className={styles.info} style={{backgroundColor:'#26CB20'}} onClick={props.onClick} title={props.title}><i className='fas fa-play' /></button>;
export const StopButton = (props) => <button id={props.id} className={styles.info} style={{backgroundColor:'#CB2026'}} onClick={props.onClick} title={props.title}><i className='fas fa-stop' /></button>;
export const SyncButton = (props) => info_template('fas fa-exchange-alt',props);
export const TermButton = (props) => info_template('fas fa-terminal',props);
export const UiButton = (props) => info_template('fas fa-globe-americas',props);
export const UnlinkButton = (props) => info_template('fas fa-unlink',props);
export const ViewButton = (props) => info_template('fas fa-search-plus',props);

// ************************** IPAM ****************************

const ipam_template = (color,props) => <button id={props.id} className={styles.ipam} style={{backgroundColor:color}} onClick={props.onClick} title={props.title}>{props.text}</button>
export const IpamGreenButton = (props) => ipam_template('#26CB20',props)
export const IpamGreyButton = (props) => ipam_template('#9CA6B0',props)
export const IpamRedButton = (props) => ipam_template('#CB2026',props)
