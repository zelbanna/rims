import React, { Component } from 'react'
import { rest_call, rest_base, read_cookie } from './infra/Functions.js';
import { Spinner,StateMap } from './infra/Generic.js';
import { MainBase, ListBase, ReportBase, InfoBase } from './infra/Base.jsx';
import { InfoButton } from './infra/Buttons.js';
import { InfoCol2 }   from './infra/Info.js';

/*

def main(aWeb):
def logs(aWeb):
def list(aWeb):
def oui_search(aWeb):
def oui_list(aWeb):
def search(aWeb):
def info(aWeb):
def extended(aWeb):
def control(aWeb):
def delete(aWeb):
def type_list(aWeb):
def model_list(aWeb):
def model_info(aWeb):
def logs(aWeb):
def to_console(aWeb):
def conf_gen(aWeb):
def function(aWeb):
def new(aWeb):
def discover(aWeb):
def interface_list(aWeb):
def interface_lldp(aWeb):
def interface_info(aWeb):
def interface_ipam(aWeb):
def interface_connect(aWeb):
def connection_info(aWeb):

*/


export class Main extends Component {

 render() {
  return (<div>Device Main</div>);
 }
}

// ************** Report **************
//
export class Report extends ReportBase {
 constructor(props){
  super(props)
  this.header = 'Devices'
  this.thead = ['ID','Hostname','Class','IP','MAC','OUI','Model','OID','Serial','State']
 }

 componentDidMount(){
  rest_call(rest_base + 'api/device/list', { extra:['system','type','mac','oui','class']})
   .then((result) => { this.setState(result) })
 }

 listItem = (row) => [row.id,row.hostname,row.class,row.ip,row.mac,row.oui,row.model,row.oid,row.serial,StateMap({state:row.state})]
}

// ************** Logs **************
//
export class Logs extends Component {

 render() {
  return (<div>Device Logs</div>);
 }
}
