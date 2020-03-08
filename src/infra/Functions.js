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

export const rnd = () => Math.floor(Math.random() * 10)
