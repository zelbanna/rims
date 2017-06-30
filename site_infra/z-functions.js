// Tools created using javascript
//
// Version: 17.6.15GA
// Author:  Zacharias El Banna
// 

//
// Button functions - accepts proper JScript object:
//  Set attribute log=true to log operation
//
// - [load]   div url spin(true/small/false) [msg = for confirmation] [frm = if doing a post]
// - toggle   div
// - hide     div
// - single   div select
// - empty    div
// - redirect url
// - iload    iframe url
// - submit   frm
// - logout   url
//

function btnoperation(event) {
 button = event.target;
 var op  = $(button).attr("op");
 var div = $("#"+$(button).attr("div"));
 var url = $(button).attr("url");
 var log = $(button).attr("log");
 if (log)
  console.log("Log OP:"+op);

 if (!op || op == 'load') {
  var msg  = button.getAttribute("msg");
  if (msg && !confirm(msg)) return;
  var spin = button.getAttribute("spin");
  if (spin == "true"){
   div.scrollTop(0);
   div.css("overflow-y","hidden");
   div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
  } else if (spin == "small"){
   div.append("<DIV CLASS='z-loader-small'></DIV>");
  }
  var frm  = button.getAttribute("frm");
  if(frm)
   $.post(url, $("#"+frm).serialize() , function(result) { div.html(result); });
  else
   div.load(url, function(responseTxt, statusTxt, xhr){ div.css("overflow-y","auto"); });
 } else if (op == 'toggle') {
  div.toggle();
 } else if (op == 'hide') {
  div.hide();
 } else if (op == 'empty') {
  div.html('');
 } else if (op == 'single') {
  $(button.getAttribute("selector")).hide();
  div.show();
 } else if (op == 'redirect') {
  location.replace(url);
 } else if (op == 'iload') {
  $("#"+ button.getAttribute("iframe")).attr('src',url);
 } else if (op == 'submit') {
  $("#"+ button.getAttribute("frm")).submit();
 } else if (op == 'logout') {
  var cookies = document.cookie.split(";");
  for(var i=0; i < cookies.length; i++) {
   var equals = cookies[i].indexOf("=");
   var name = equals > -1 ? cookies[i].substr(0, equals) : cookies[i];
   document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
  location.replace(url);
 }
};
