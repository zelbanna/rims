"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[52],{52:function(t,n,e){e.r(n),e.d(n,{Main:function(){return v}});var o=e(37),r=e(671),a=e(144),i=e(340),s=e(882),c=e(791),u=e(252),l=e(355),p=e(885),f=e(582),m=e(184),v=function(t){(0,i.Z)(e,t);var n=(0,s.Z)(e);function e(t){var a;return(0,r.Z)(this,e),(a=n.call(this,t)).compileNavItems=function(){for(var t=[],n=function(){var n=(0,o.Z)(r[e],2),i=n[0],s=n[1];"module"===s.type?t.push((0,m.jsx)(l.NavDropButton,{title:i,onClick:function(){return a.context.changeMain(s)}},"mb_"+i)):"tab"===s.type?t.push((0,m.jsx)(l.NavDropButton,{title:i,onClick:function(){return window.open(s.tab,"_blank")}},"mb_"+i)):"frame"===s.type?t.push((0,m.jsx)(l.NavDropButton,{title:i,onClick:function(){return a.context.changeMain((0,m.jsx)("iframe",{className:f.Z.frame,title:i,src:s.frame}))}},"mb_"+i)):console.log("Unknown panel type:"+JSON.stringify(s))},e=0,r=Object.entries(a.state.data);e<r.length;e++)n();a.context.loadNavigation((0,m.jsx)(l.NavBar,{children:(0,m.jsx)(l.NavDropDown,{title:"Resources",children:t},"resources")},"resource_navbar"))},a.state={},a}return(0,a.Z)(e,[{key:"componentDidMount",value:function(){var t=this;(0,u.Fh)("api/portal/resources",{type:"resource"}).then((function(n){Object.assign(t.state,n),t.compileNavItems()}))}},{key:"componentDidUpdate",value:function(t){t!==this.props&&this.compileNavItems()}},{key:"render",value:function(){return(0,m.jsx)(c.Fragment,{})}}]),e}(c.Component);v.contextType=p.RimsContext}}]);
//# sourceMappingURL=52.c020dcd4.chunk.js.map