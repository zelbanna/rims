(this.webpackJsonprims=this.webpackJsonprims||[]).push([[13],{45:function(e,t,n){"use strict";n.r(t),n.d(t,"Manage",(function(){return y})),n.d(t,"Inventory",(function(){return _}));var a=n(18),c=n(14),o=n(4),i=n(5),r=n(6),s=n(7),u=n(0),l=n.n(u),p=n(12),d=n(13),v=n(15),h=n(19),f=n(16),y=function(e){Object(s.a)(n,e);var t=Object(r.a)(n);function n(){var e;Object(o.a)(this,n);for(var a=arguments.length,c=new Array(a),i=0;i<a;i++)c[i]=arguments[i];return(e=t.call.apply(t,[this].concat(c))).changeContent=function(t){return e.setState(t)},e}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var e=this;Object(p.d)("api/device/hostname",{id:this.props.device_id}).then((function(t){e.context.loadNavigation(l.a.createElement(f.NavBar,{key:"cons_navbar"},l.a.createElement(f.NavInfo,{key:"cons_nav_name",title:t.data}),l.a.createElement(f.NavButton,{key:"cons_nav_inv",title:"Inventory",onClick:function(){return e.changeContent(l.a.createElement(_,{key:"cons_inventory",device_id:e.props.device_id,type:e.props.type}))}}),l.a.createElement(f.NavButton,{key:"con_nav_info",title:"Info",onClick:function(){return e.changeContent(l.a.createElement(m,{key:"con_info",device_id:e.props.device_id,type:e.props.type}))}})))})),this.setState(l.a.createElement(_,{key:"cons_inventory",device_id:this.props.device_id,type:this.props.type}))}},{key:"render",value:function(){return l.a.createElement(u.Fragment,{key:"manage_base"},this.state)}}]),n}(u.Component);y.contextType=d.RimsContext;var m=function(e){Object(s.a)(n,e);var t=Object(r.a)(n);function n(e){var i;return Object(o.a)(this,n),(i=t.call(this,e)).onChange=function(e){return i.setState({data:Object(c.a)({},i.state.data,Object(a.a)({},e.target.name,e.target.value))})},i.updateInfo=function(){return Object(p.d)("api/devices/"+i.props.type+"/info",Object(c.a)({op:"update"},i.state.data)).then((function(e){return i.setState(e)}))},i.state={},i}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var e=this;Object(p.d)("api/devices/"+this.props.type+"/info",{device_id:this.props.device_id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){var e=this;return this.state.data?l.a.createElement(d.Flex,{key:"ci_flex",style:{justifyContent:"space-evenly"}},l.a.createElement(d.InfoArticle,{key:"ci_article",header:"Console Info - "+this.props.type},l.a.createElement(d.InfoColumns,{key:"ci_info"},l.a.createElement(v.TextInput,{key:"ci_access_url",id:"access_url",label:"Access URL",value:this.state.data.access_url,onChange:this.onChange,title:"URL used as base together with port"}),l.a.createElement(v.TextInput,{key:"ci_port",id:"port",value:this.state.data.port,onChange:this.onChange})),l.a.createElement(h.ReloadButton,{key:"ci_btn_reload",onClick:function(){return e.componentDidMount()}}),l.a.createElement(h.SaveButton,{key:"ci_btn_save",onClick:function(){return e.updateInfo()}}))):l.a.createElement(d.Spinner,null)}}]),n}(u.Component),_=function(e){Object(s.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(o.a)(this,n),(a=t.call(this,e)).changeContent=function(e){return a.setState({content:e})},a.cnctFunction=function(e){var t=parseInt(e)+parseInt(a.state.extra.port);window.open("".concat(a.state.extra.access_url,":").concat(t),"_self")},a.listItem=function(e){return[e.interface,e.name,l.a.createElement(h.TermButton,{key:"con_inv_btn_cnct_"+e.interface,onClick:function(){return a.cnctFunction(e.interface)},title:"Connect"})]},a.state={},a}return Object(i.a)(n,[{key:"componentDidMount",value:function(){var e=this;Object(p.d)("api/devices/"+this.props.type+"/inventory",{device_id:this.props.device_id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function(){var e=this;return this.state.data?l.a.createElement(u.Fragment,{key:"con_fragment"},l.a.createElement(d.ContentList,{key:"con_cl",header:"Inventory",thead:["Port","Device",""],trows:this.state.data,listItem:this.listItem},l.a.createElement(h.ReloadButton,{key:"con_btn_reload",onClick:function(){e.setState({data:void 0}),e.componentDidMount()}})),l.a.createElement(d.ContentData,{key:"con_cd"},this.state.content)):l.a.createElement(d.Spinner,null)}}]),n}(u.Component)}}]);
//# sourceMappingURL=13.4fb47012.chunk.js.map