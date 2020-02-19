import React from 'react';

// ********************* Portal Pages ***********************
import * as Activity from './Activity.js';
import * as Device   from './Device.js';
import * as Hypervisor from './Hypervisor.js';
import * as Inventory  from './Inventory.js';
import * as Rack     from  './Rack.js';
import * as Reservation from './Reservation.js';
import * as Resource from './Resource.js';
import * as System   from './System.js';
import * as User     from './User.js';
import * as Visualize from './Visualize';

export const library = {
 activity:Activity,
 device:Device,
 hypervisor:Hypervisor,
 inventory:Inventory,
 rack:Rack,
 reservation:Reservation,
 resource:Resource,
 system:System,
 user:User,
 visualize:Visualize
}

export const mapper = (params) => {
 let elem = null;
 try {
  const args = params.args;
  const parts = params.module.split('_');
  const module = library[parts[0]];
  const Elem = module[parts[1].charAt(0).toUpperCase() + parts[1].substring(1)];
  elem = <Elem key={params.module} {...args} />
 } catch(err) {
  console.log("Mapper error: "+params);
  alert(err);
 }
 return elem;
}

export const rest_base = 'http://172.16.36.129:8080/'

// ************************ Javascript ************************

export async function rest_call(url = '', args = {}) {
 const response = await fetch(url, { method:'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(args) })
 // console.log(response)
 return await response.json();
}

export const read_cookie = () => {
 var cookies = document.cookie.split("; ");
 for(var i=0;i < cookies.length;i++) {
  var c = cookies[i];
  if (c.indexOf("rims=") === 0)
   // Parse from 5th letter to end
   return JSON.parse(atob(c.substring(5,c.length)));
 }
 return null;
}

export const set_cookie = (cookie,expires) => {
 console.log("Creating cookie: 'rims' expires:" + expires);
 const encoded = btoa(JSON.stringify(cookie));
 document.cookie = "rims=" + encoded + "; expires=" + expires + "; Path=/";
}

export const erase_cookie = () => {
 console.log("Erasing cookie 'rims'");
 document.cookie = "rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
}
