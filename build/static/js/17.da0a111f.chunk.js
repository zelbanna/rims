(this.webpackJsonprims=this.webpackJsonprims||[]).push([[17],{45:function(e,t,n){"use strict";n.r(t),n.d(t,"Main",(function(){return f}));var a=n(15),r=n(2),o=n(3),c=n(5),i=n(4),u=n(6),s=n(0),l=n.n(s),m=n(8),p=n(11),f=function(e){function t(e){var n;return Object(r.a)(this,t),(n=Object(c.a)(this,Object(i.a)(t).call(this,e))).compileNavItems=function(){for(var e=[],t=function(){var t=Object(a.a)(o[r],2),c=t[0],i=t[1];"module"===i.type?e.push(l.a.createElement(p.NavDropButton,{key:"mb_"+c,title:c,onClick:function(){return n.context.changeMain(i)}})):"tab"===i.type?e.push(l.a.createElement(p.NavDropButton,{key:"mb_"+c,title:c,onClick:function(){return window.open(i.tab,"_blank")}})):"frame"===i.type&&e.push(l.a.createElement(p.NavDropButton,{key:"mb_"+c,title:c,onClick:function(){return n.context.changeMain(l.a.createElement("iframe",{id:"resource_frame",name:"resource_frame",title:c,src:i.frame}))}}))},r=0,o=Object.entries(n.state.data);r<o.length;r++)t();n.context.loadNavigation(l.a.createElement(p.NavBar,{key:"resource_navbar"},l.a.createElement(p.NavDropDown,{key:"resources",title:"Resources"},e)))},n.state={},n}return Object(u.a)(t,e),Object(o.a)(t,[{key:"componentDidMount",value:function(){var e=this;Object(m.d)("api/portal/resources",{type:"tool"}).then((function(t){Object.assign(e.state,t),e.compileNavItems()}))}},{key:"componentDidUpdate",value:function(e){e!==this.props&&this.compileNavItems()}},{key:"render",value:function(){return l.a.createElement(s.Fragment,null)}}]),t}(s.Component);f.contextType=m.a}}]);
//# sourceMappingURL=17.da0a111f.chunk.js.map