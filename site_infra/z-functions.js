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
// - load     div lnk spin(true/false)
// - confirm  div lnk msg spin(true/false)
// - iconfirm iframe lnk msg
// - reload   lnk
// - iload    iframe lnk
// - post     div lnk frm (to serialize) spin(true/false)
//

function btnoperation(button) {
 var op   = button.getAttribute("op");
 var div  = $("#"+button.getAttribute("div"));
 var spin = button.getAttribute("spin");

 if (op == 'toggle') {
  div.toggle();
 } else if (op == 'hide') {
  div.hide();
 } else if (op == 'single') {
  var selector = $(button.getAttribute("selector"));
  selector.hide();
  div.show();
 } else if (op == 'load') {
  var lnk = button.getAttribute("lnk");
  div.load(lnk, function(responseTxt, statusTxt, xhr){ div.css("overflow-y","auto"); });
  if (spin == "true"){
   div.scrollTop(0);
   div.css("overflow-y","hidden");
   div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
  }
 } else if (op == 'confirm') {
  var msg  = button.getAttribute("msg");
  var lnk  = button.getAttribute("lnk");
  if (confirm(msg) == true){
   if (spin == "true"){
    div.scrollTop(0);
    div.css("overflow-y","hidden");
    div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
   }
   div.load(lnk, function(responseTxt, statusTxt, xhr){ div.css("overflow-y","auto"); });
  }
 } else if (op == 'iconfirm') {
  var msg = button.getAttribute("msg");
  var lnk = button.getAttribute("lnk");
  var ifr = $("#"+button.getAttribute("iframe"));
  if (confirm(msg) == true){
   ifr.attr('src',lnk);
  }
 } else if (op == 'reload') {
  var lnk = button.getAttribute("lnk");
  location.replace(lnk);
 } else if (op == 'iload') {
  var ifr = $("#"+button.getAttribute("iframe"));
  var lnk = button.getAttribute("lnk");
  ifr.attr('src',lnk);
 } else if (op == 'post') {
  var lnk = button.getAttribute("lnk");
  var frm = button.getAttribute("frm");
  if (spin == "true"){
   div.scrollTop(0);
   div.css("overflow-y","hidden");
   div.append("<DIV CLASS='z-overlay'><DIV CLASS='z-loader'></DIV></DIV>");
  }
  $.post(lnk, $("#"+frm).serialize() , function(result) { div.html(result); });
 }
};
