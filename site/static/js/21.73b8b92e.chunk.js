(this.webpackJsonprims=this.webpackJsonprims||[]).push([[21],{52:function(t,e,n){"use strict";n.r(e),n.d(e,"Main",(function(){return v}));var a=n(20),o=n(5),c=n(6),r=n(8),i=n(7),s=n(3),u=n.n(s),p=n(14),l=n(17),b=n(15),j=n(1),m=n.n(j),f=n(0),v=function(t){Object(r.a)(n,t);var e=Object(i.a)(n);function n(t){var c;return Object(o.a)(this,n),(c=e.call(this,t)).compileNavItems=function(){for(var t=[],e=function(){var e=Object(a.a)(o[n],2),r=e[0],i=e[1];"module"===i.type?t.push(Object(f.jsx)(l.NavDropButton,{title:r,onClick:function(){return c.context.changeMain(i)}},"mb_"+r)):"tab"===i.type?t.push(Object(f.jsx)(l.NavDropButton,{title:r,onClick:function(){return window.open(i.tab,"_blank")}},"mb_"+r)):"frame"===i.type?t.push(Object(f.jsx)(l.NavDropButton,{title:r,onClick:function(){return c.context.changeMain(Object(f.jsx)("iframe",{className:m.a.frame,title:r,src:i.frame}))}},"mb_"+r)):console.log("Unknown panel type:"+JSON.stringify(i))},n=0,o=Object.entries(c.state.data);n<o.length;n++)e();c.context.loadNavigation(Object(f.jsx)(l.NavBar,{children:Object(f.jsx)(l.NavDropDown,{title:"Resources",children:t},"resources")},"resource_navbar"))},c.state={},c}return Object(c.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(p.d)("api/portal/resources",{type:"resource"}).then((function(e){Object.assign(t.state,e),t.compileNavItems()}))}},{key:"componentDidUpdate",value:function(t){t!==this.props&&this.compileNavItems()}},{key:"render",value:function(){return Object(f.jsx)(u.a.Fragment,{})}}]),n}(s.Component);v.contextType=b.RimsContext}}]);
//# sourceMappingURL=21.73b8b92e.chunk.js.map