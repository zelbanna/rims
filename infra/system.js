// Tools created using javascript
//
// Version: 18.02.12GA
// Author:  Zacharias El Banna
// 


//
function create_cookie(name,value,life) {
 var date = new Date();
 seconds = (life) ? life*1000 : "3000000";
 date.setTime(date.getTime()+seconds);
 console.log("Creating cookie:" + name + " expires:" + date.toGMTString());
 document.cookie = name+"="+value+"; expires=" + date.toGMTString() + "; Path=/";
}

function read_cookie(name) {
 var nameEQ = name + "=";
 var cookies = document.cookie.split("; ");
 for(var i=0;i < cookies.length;i++) {
  var c = cookies[i];
  if (c.indexOf(nameEQ) == 0)
   return c.substring(nameEQ.length,c.length);
 }
 return null;
}

function erase_cookie(name) {
 document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
}

//
function include_html(dst,src) {
 var dest = $('#'+ dst);
 $.get(src,function(data) { load_result(dest,data);});
}

//
// Button functions - accepts proper JScript object:
//  Set attribute log=true to log operation
//
// - [load]   div url [spin=true/div] [msg = for confirmation] [frm = if doing a post] [input = True if populating input]
// - redirect url
// - iload    iframe url
// - logout   url/div
// - toggle   div
// - hide     div
// - single   div select
// - empty    div
// - submit   frm
//

function btn(e) {
 var op  = $(this).attr("op");
 var div = $("#"+$(this).attr("div"));
 var url = $(this).attr("url");
 var log = $(this).attr("log");

 if (log)
  console.log("Log OP:"+op);

 if (!op || op == 'load') {
  if (this.getAttribute("msg") && !confirm(this.getAttribute("msg"))) return;
  var spin = this.getAttribute("spin");
  if (spin){
    spin = (spin.toLowerCase() == 'true') ? div : $("#"+spin);
    load_spinner(spin);
  }
  var frm  =  this.getAttribute("frm");
  var input = this.getAttribute("input");
  if(frm)
   $.post(url, $("#"+frm).serializeArray() , function(result) { load_result(div,result,spin,input);  });
  else
   $.get(url, function(result) { load_result(div,result,spin,input); });

 } else if (op == 'redirect') {
  location.replace(url);
 } else if (op == 'submit') {
  $("#"+ this.getAttribute("frm")).submit();
 } else if (op == 'iload') {
  $("#"+ this.getAttribute("iframe")).attr('src',url);
 } else if (op == 'logout') {
  if (this.getAttribute("cookie")) {
   console.log('Expiring cookie:' + this.getAttribute("cookie"));
   erase_cookie(this.getAttribute("cookie"));
  } else {
   var cookies = document.cookie.split("; ");
   for(var i=0; i < cookies.length; i++) {
    var equals = cookies[i].indexOf("=");
    var name = equals > -1 ? cookies[i].substr(0, equals) : cookies[i];
    erase_cookie(this.getAttribute("cookie"));
   }
  }
  if(url)
   location.replace(url);
  else
   div.html('');
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
// Callback for loading result
//
function load_result(dest,data,spin,input){
 if (input)
  dest.val(data);
 else
  dest.html(data);
 if (spin) {
  $(".overlay").remove();
  spin.css("overflow-y","auto");
 }
}

//
// Loading spinner overlay, lock scrolling and scroll up first before adding spinner
//
function load_spinner(dest){
 dest.scrollTop(0);
 dest.css("overflow-y","hidden");
 dest.append("<DIV CLASS='overlay'><DIV CLASS='loader'></DIV></DIV>");
}

//
//
function focus(e){
 if (e.originalEvent.type == 'focus')
  $(this).addClass('highlight');
 else if (e.originalEvent.type == 'blur')
  $(this).removeClass('highlight');
};

//
// Drag-n'-drop
// - updating a list of element id's on attribute "dest" on drop element
//
function dragndrop(){
 $(".drag").off();
 $(".drop").off();
 $(".drag").attr("draggable","true");
 $(".drag").on("dragstart", dragstart);
 $(".drag").on("dragend", dragend);
 $(".drop").on("dragover", dragover);
 $(".drop").on("drop", drop);
 $(".drop").on("dragenter", dragenter);
 $(".drop").on("dragleave", dragleave);
}

//
function dragend(e){
 this.style.opacity = '';
}

//
function dragstart(e){
 console.log("Drag " + this.id + " FROM " + this.parentElement.id);
 this.style.opacity = '0.4';
 e.originalEvent.dataTransfer.setData("Text",this.id);
 e.originalEvent.dataTransfer.effectAllowed = 'move';
}

//
function dragover(e){
 if(e.preventDefault)
  e.preventDefault();
 return false;
}
function dragenter(e){ this.classList.add('highlight'); }
function dragleave(e){ this.classList.remove('highlight'); }

//
function drop(e){
 e.preventDefault();
 var el_id = e.originalEvent.dataTransfer.getData("Text");
 var el    = document.getElementById(el_id);
 var parent= el.parentElement;
 this.appendChild(el);
 console.log("Drop " + el_id + " INTO " + this.id + " FROM " + parent.id);
 updatelist(this);
 updatelist(parent);
 this.classList.remove('highlight');
}

//
function updatelist(obj){
 var list = [];
 for (i = 0; i < obj.children.length; i++){ list.push(obj.children[i].id); }
 $("#" + obj.getAttribute("dest")).attr("value",list);
}

