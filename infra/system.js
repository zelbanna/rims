// Tools created using javascript
//
// Version: 17.11.17GA
// Author:  Zacharias El Banna
// 

//
// Button functions - accepts proper JScript object:
//  Set attribute log=true to log operation
//
// - [load]   div url [spin=true/div] [msg = for confirmation] [frm = if doing a post]
// - redirect url
// - iload    iframe url
// - logout   url/div
// - toggle   div
// - hide     div
// - single   div select
// - empty    div
// - submit   frm
//

function btnfunction(event) {
 var op  = $(this).attr("op");
 var div = $("#"+$(this).attr("div"));
 var url = $(this).attr("url");
 var log = $(this).attr("log");

 if (log)
  console.log("Log OP:"+op);

 if (!op || op == 'load') {
  var msg  = this.getAttribute("msg");
  if (msg && !confirm(msg)) return;
  var spin = this.getAttribute("spin");
  if (spin){
    if(spin == 'true')
     spin = div;
    else
     spin = $("#"+spin);
    spin.scrollTop(0);
    spin.css("overflow-y","hidden");
    spin.append("<DIV CLASS='overlay'><DIV CLASS='loader'></DIV></DIV>");
  }
  var frm  = this.getAttribute("frm");
  if(frm)
   $.post(url, $("#"+frm).serializeArray() , function(result) { 
    div.html(result); 
    if(spin){
     $(".overlay").remove();
     spin.css("overflow-y","auto");
    }
   });
  else
   div.load(url, function(responseTxt, statusTxt, xhr){
    if (spin) {
     $(".overlay").remove();
     spin.css("overflow-y","auto");
    }
   });
 } else if (op == 'redirect') {
  location.replace(url);
 } else if (op == 'submit') {
  $("#"+ this.getAttribute("frm")).submit();
 } else if (op == 'iload') {
  $("#"+ this.getAttribute("iframe")).attr('src',url);
 } else if (op == 'logout') {
  var cookies = document.cookie.split(";");
  for(var i=0; i < cookies.length; i++) {
   var equals = cookies[i].indexOf("=");
   var name = equals > -1 ? cookies[i].substr(0, equals) : cookies[i];
   document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
  }
  if(url)
   location.replace(url);
  else
   div.html('')
 } else if (op == 'single') {
  $(this.getAttribute("selector")).hide();
  div.show();
 } else if (op == 'toggle') {
  div.toggle();
 } else if (op == 'hide') {
  div.hide();
 } else if (op == 'empty') {
  div.html('');
 }
};

//
//
function focusfunction(event){
 if (event.originalEvent.type == 'focus')
  $(this).addClass('highlight');
 else if (event.originalEvent.type == 'blur')
  $(this).removeClass('highlight');
};
