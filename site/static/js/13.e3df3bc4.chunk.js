(this.webpackJsonprims=this.webpackJsonprims||[]).push([[13],{47:function(e,t,n){"use strict";n.r(t),n.d(t,"Manage",(function(){return y})),n.d(t,"Inventory",(function(){return _}));var a=n(18),o=n(14),c=n(3),r=n(4),i=n(5),s=n(6),u=n(0),l=n.n(u),p=n(12),d=n(13),v=n(15),f=n(19),h=n(16),y=function(e){Object(s.a)(Manage,e);var t=Object(i.a)(Manage);function Manage(){var e;Object(c.a)(this,Manage);for(var n=arguments.length,a=new Array(n),o=0;o<n;o++)a[o]=arguments[o];return(e=t.call.apply(t,[this].concat(a))).changeContent=function(t){return e.setState(t)},e}return Object(r.a)(Manage,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(p.d)("api/device/hostname",{id:this.props.device_id}).then((function(t){e.context.loadNavigation(l.a.createElement(h.NavBar,{key:"cons_navbar"},l.a.createElement(h.NavInfo,{key:"cons_nav_name",title:t.data}),l.a.createElement(h.NavButton,{key:"cons_nav_inv",title:"Inventory",onClick:function onClick(){return e.changeContent(l.a.createElement(_,{key:"cons_inventory",device_id:e.props.device_id,type:e.props.type}))}}),l.a.createElement(h.NavButton,{key:"con_nav_info",title:"Info",onClick:function onClick(){return e.changeContent(l.a.createElement(m,{key:"con_info",device_id:e.props.device_id,type:e.props.type}))}})))})),this.setState(l.a.createElement(_,{key:"cons_inventory",device_id:this.props.device_id,type:this.props.type}))}},{key:"render",value:function render(){return l.a.createElement(u.Fragment,null,this.state)}}]),Manage}(u.Component);y.contextType=d.RimsContext;var m=function(e){Object(s.a)(Info,e);var t=Object(i.a)(Info);function Info(e){var n;return Object(c.a)(this,Info),(n=t.call(this,e)).onChange=function(e){return n.setState({data:Object(o.a)({},n.state.data,Object(a.a)({},e.target.name,e.target.value))})},n.updateInfo=function(){return Object(p.d)("api/devices/"+n.props.type+"/info",Object(o.a)({op:"update"},n.state.data)).then((function(e){return n.setState(e)}))},n.state={},n}return Object(r.a)(Info,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(p.d)("api/devices/"+this.props.type+"/info",{device_id:this.props.device_id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function render(){var e=this;return this.state.data?l.a.createElement(d.Flex,{key:"ci_flex",style:{justifyContent:"space-evenly"}},l.a.createElement(d.InfoArticle,{key:"ci_article",header:"Console Info - "+this.props.type},l.a.createElement(d.InfoColumns,{key:"ci_info"},l.a.createElement(v.TextInput,{key:"ci_access_url",id:"access_url",label:"Access URL",value:this.state.data.access_url,onChange:this.onChange,title:"URL used as base together with port"}),l.a.createElement(v.TextInput,{key:"ci_port",id:"port",value:this.state.data.port,onChange:this.onChange})),l.a.createElement(f.ReloadButton,{key:"ci_btn_reload",onClick:function onClick(){return e.componentDidMount()}}),l.a.createElement(f.SaveButton,{key:"ci_btn_save",onClick:function onClick(){return e.updateInfo()}}))):l.a.createElement(d.Spinner,null)}}]),Info}(u.Component),_=function(e){Object(s.a)(Inventory,e);var t=Object(i.a)(Inventory);function Inventory(e){var n;return Object(c.a)(this,Inventory),(n=t.call(this,e)).changeContent=function(e){return n.setState({content:e})},n.cnctFunction=function(e){var t=parseInt(e)+parseInt(n.state.extra.port);window.open("".concat(n.state.extra.access_url,":").concat(t),"_self")},n.listItem=function(e){return[e.interface,e.name,l.a.createElement(f.TermButton,{key:"con_inv_btn_cnct_"+e.interface,onClick:function onClick(){return n.cnctFunction(e.interface)},title:"Connect"})]},n.state={},n}return Object(r.a)(Inventory,[{key:"componentDidMount",value:function componentDidMount(){var e=this;Object(p.d)("api/devices/"+this.props.type+"/inventory",{device_id:this.props.device_id}).then((function(t){return e.setState(t)}))}},{key:"render",value:function render(){var e=this;return this.state.data?l.a.createElement(u.Fragment,null,l.a.createElement(d.ContentList,{key:"con_cl",header:"Inventory",thead:["Port","Device",""],trows:this.state.data,listItem:this.listItem},l.a.createElement(f.ReloadButton,{key:"con_btn_reload",onClick:function onClick(){e.setState({data:void 0}),e.componentDidMount()}})),l.a.createElement(d.ContentData,{key:"con_cd"},this.state.content)):l.a.createElement(d.Spinner,null)}}]),Inventory}(u.Component)}}]);
//# sourceMappingURL=13.e3df3bc4.chunk.js.map