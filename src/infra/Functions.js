export const rest_base = 'http://172.16.36.129:8080/'

// ************************ Javascript ************************

export async function rest_call(url = '', args = {}) {
 const response = await fetch(url, { method:'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(args) })
 //console.log(response)
 if (response.status === 200)
  return await response.json();
 else
  return {}
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
 return true;
}

export const erase_cookie = () => {
 console.log("Erasing cookie 'rims'");
 document.cookie = "rims=; Path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
 return true;
}

export const rnd = () => Math.floor(Math.random() * 10)