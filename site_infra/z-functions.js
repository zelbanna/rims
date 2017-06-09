// Tools created using javascript
//
// Version: 2.1GA
// Author:  Zacharias El Banna
// 

//
// Button functions - accepts proper JScript object:
// - toggle   div
// - hide     div
// - single   div select
// - load     div url spin(true/false)
// - confirm  div url msg spin(true/false)
// - iconfirm iframe url msg
// - redirect url
// - iload    iframe url
// - post     div url frm (to serialize) spin(true/false)
// - submit   frm
// - logout   url
//

function btnoperation(button) {
 var op   = button.getAttribute("op");
 var div  = $("#"+button.getAttribute("div"));
 var spin = button.getAttribute("spin");
 var url  = button.getAttribute("url");

 if (op == 'toggle') {
  div.toggle();
 } else if (op == 'hide') {
  div.hide();
 } else if (op == 'single') {
  var selector = $(button.getAttribute("selector"));
  selector.hide();
  div.show();
 } else if (op == 'load') {
  if (spin == "true"){
   div.scrollTop(0);
   div.css("overflow-y","hidden");
   div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
  }
  div.load(url, function(responseTxt, statusTxt, xhr){ div.css("overflow-y","auto"); });
 } else if (op == 'confirm') {
  var msg  = button.getAttribute("msg");
  if (confirm(msg) == true){
   if (spin == "true"){
    div.scrollTop(0);
    div.css("overflow-y","hidden");
    div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
   }
   div.load(url, function(responseTxt, statusTxt, xhr){ div.css("overflow-y","auto"); });
  }
 } else if (op == 'iconfirm') {
  var msg = button.getAttribute("msg");
  var ifr = $("#"+button.getAttribute("iframe"));
  if (confirm(msg) == true){
   ifr.attr('src',url);
  }
 } else if (op == 'redirect') {
  location.replace(url);
 } else if (op == 'iload') {
  var ifr = $("#"+button.getAttribute("iframe"));
  ifr.attr('src',url);
 } else if (op == 'post') {
  var frm = button.getAttribute("frm");
  if (spin == "true"){
   div.scrollTop(0);
   div.css("overflow-y","hidden");
   div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
  }
  $.post(url, $("#"+frm).serialize() , function(result) { div.html(result); });
 } else if (op == 'submit') {
  var frm = button.getAttribute("frm");
  $("#"+frm).submit();
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
